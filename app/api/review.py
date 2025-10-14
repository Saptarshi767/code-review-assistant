"""
API endpoints for code review functionality.
"""

import uuid
import time
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Query, Depends
from fastapi.responses import JSONResponse
from typing import Optional, List
from datetime import datetime

from app.models.file_models import UploadResponse, SupportedFormatsResponse
from app.models.processing_models import ProcessedFile
from app.models.api_models import (
    ReviewResponse, Report, ReportListResponse, ReportStatus, 
    DeleteResponse, LimitsResponse
)
from app.models.analysis_models import AnalysisContextModel
from app.services.file_service import file_service
from app.services.llm_service import llm_service, AnalysisContext, CodeChunk
from app.services.analysis_processor import analysis_processor
from app.services.report_manager import get_report_manager
from app.auth.middleware import api_key_auth, optional_api_key_auth
from app.auth.models import User
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["review"])


async def get_current_user_optional():
    """Get current user optionally based on configuration."""
    if settings.disable_authentication:
        return None
    try:
        return await api_key_auth()
    except HTTPException:
        return None


@router.post("/review", response_model=ReviewResponse)
async def upload_file_for_review(
    file: UploadFile = File(..., description="Source code file to analyze"),
    language: Optional[str] = Query(None, description="Programming language (auto-detected if not provided)"),
    async_processing: bool = Query(False, description="Whether to process asynchronously"),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Upload a source code file for automated review.
    
    Accepts single files or zip archives containing multiple source files.
    Validates file size (max 10MB) and supported file types.
    Performs LLM analysis and returns structured review report.
    
    Args:
        file: Uploaded file (source code or zip archive)
        language: Programming language override (optional)
        async_processing: Whether to process asynchronously (for large files)
        
    Returns:
        ReviewResponse with report ID and analysis results
        
    Raises:
        HTTPException: If file validation or processing fails
    """
    start_time = time.time()
    report_manager = get_report_manager()
    
    try:
        # Validate the uploaded file
        validation_result = await file_service.validate_file(file)
        
        if not validation_result.valid:
            from app.utils.error_handler import ValidationException
            raise ValidationException(
                "File validation failed",
                details={
                    "errors": [error.message for error in validation_result.errors],
                    "supported_formats": file_service.get_supported_formats()
                }
            )
        
        # Process the file (content reading, language detection, sanitization)
        processed_file = await file_service.process_file(file)
        
        # Use provided language or detected language
        detected_language = language or processed_file.language
        
        # Create initial report
        report = report_manager.create_report(
            filename=file.filename,
            language=detected_language,
            file_size=validation_result.file_size
        )
        
        # Determine processing mode based on file size and user preference
        file_size_mb = validation_result.file_size / (1024 * 1024)
        should_process_async = async_processing or file_size_mb > 1.0
        
        if should_process_async:
            # For large files or when requested, return immediately and process in background
            # TODO: Implement background processing in future tasks
            estimated_time = max(30, int(file_size_mb * 10))  # Rough estimate
            
            return ReviewResponse(
                report_id=report.report_id,
                status=ReportStatus.PROCESSING,
                filename=file.filename,
                language=detected_language,
                estimated_time=estimated_time
            )
        
        # Synchronous processing for small files (< 1MB)
        try:
            # Perform LLM analysis
            analysis_result = await _perform_code_analysis(
                processed_file.sanitized.content,
                detected_language,
                file.filename
            )
            
            # Convert LLM results to our models
            analysis_model = analysis_processor.parse_llm_response(
                _convert_analysis_to_json(analysis_result),
                analysis_result.processing_time
            )
            
            # Complete the report
            processing_time_ms = int((time.time() - start_time) * 1000)
            completed_report = report_manager.complete_report(
                report.report_id,
                analysis_model.summary,
                analysis_model.issues,
                analysis_model.recommendations,
                processing_time_ms
            )
            
            if not completed_report:
                from app.utils.error_handler import ErrorType, CodeReviewException
                raise CodeReviewException(
                    error_type=ErrorType.STORAGE_ERROR,
                    message="Failed to save analysis results",
                    status_code=500
                )
            
            return ReviewResponse(
                report_id=completed_report.report_id,
                status=ReportStatus.COMPLETED,
                filename=completed_report.filename,
                language=completed_report.language,
                estimated_time=None
            )
            
        except Exception as analysis_error:
            # Mark report as failed
            processing_time_ms = int((time.time() - start_time) * 1000)
            report_manager.fail_report(
                report.report_id,
                f"Analysis failed: {str(analysis_error)}",
                processing_time_ms
            )
            
            logger.error(f"Analysis failed for report {report.report_id}: {analysis_error}")
            from app.utils.error_handler import ErrorType, CodeReviewException
            raise CodeReviewException(
                error_type=ErrorType.LLM_SERVICE_ERROR,
                message="Code analysis failed",
                details={
                    "report_id": report.report_id,
                    "error": str(analysis_error)
                },
                status_code=500
            )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in review endpoint: {e}")
        from app.utils.error_handler import ErrorType, CodeReviewException
        raise CodeReviewException(
            error_type=ErrorType.INTERNAL_SERVER_ERROR,
            message="Internal server error during file processing",
            details={"error": str(e)},
            status_code=500
        )


async def _perform_code_analysis(content: str, language: str, filename: str):
    """Perform LLM-based code analysis."""
    try:
        # Create analysis context
        context = AnalysisContext(
            language=language,
            ruleset=["security", "performance", "style", "maintainability"],
            focus_areas=["security", "performance", "readability", "maintainability"],
            max_severity="high"
        )
        
        # Check if we need to chunk the code
        chunks = llm_service.chunk_code(content, language)
        
        if len(chunks) == 1:
            # Single chunk analysis
            return await llm_service.analyze_code(chunks[0], context)
        else:
            # Multi-chunk analysis
            results = []
            for chunk in chunks:
                chunk_result = await llm_service.analyze_code(chunk, context)
                results.append(chunk_result)
            
            # Aggregate results
            return llm_service.aggregate_results(results)
            
    except Exception as e:
        logger.error(f"LLM analysis failed: {e}")
        raise


def _convert_analysis_to_json(analysis_result) -> str:
    """Convert LLM analysis result to JSON string for processing."""
    import json
    
    # Convert the analysis result to the expected JSON format
    result_dict = {
        "summary": analysis_result.summary,
        "issues": [
            {
                "type": issue.type,
                "severity": issue.severity,
                "line": issue.line,
                "message": issue.message,
                "suggestion": issue.suggestion,
                "code_snippet": issue.code_snippet,
                "confidence": issue.confidence
            }
            for issue in analysis_result.issues
        ],
        "recommendations": [
            {
                "area": rec.area,
                "message": rec.message,
                "impact": rec.impact,
                "effort": rec.effort,
                "examples": rec.examples or []
            }
            for rec in analysis_result.recommendations
        ]
    }
    
    return json.dumps(result_dict)


@router.get("/review/{report_id}", response_model=Report)
async def get_report(report_id: str, current_user: Optional[User] = Depends(get_current_user_optional)):
    """
    Get a specific report by ID.
    
    Args:
        report_id: Unique report identifier
        
    Returns:
        Complete Report object with analysis results
        
    Raises:
        HTTPException: If report not found
    """
    report_manager = get_report_manager()
    
    try:
        report = report_manager.get_report(report_id)
        
        if not report:
            from app.utils.error_handler import raise_not_found
            raise_not_found("Report", report_id)
        
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving report {report_id}: {e}")
        from app.utils.error_handler import ErrorType, CodeReviewException
        raise CodeReviewException(
            error_type=ErrorType.INTERNAL_SERVER_ERROR,
            message="Internal server error retrieving report",
            details={"report_id": report_id, "error": str(e)},
            status_code=500
        )


@router.get("/reviews", response_model=ReportListResponse)
async def list_reports(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
    language: Optional[str] = Query(None, description="Filter by programming language"),
    status: Optional[ReportStatus] = Query(None, description="Filter by report status"),
    date_from: Optional[datetime] = Query(None, description="Filter reports created after this date"),
    date_to: Optional[datetime] = Query(None, description="Filter reports created before this date"),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    List reports with pagination and filtering.
    
    Args:
        page: Page number (1-based)
        limit: Number of items per page (1-100)
        language: Filter by programming language (optional)
        status: Filter by report status (optional)
        date_from: Filter reports created after this date (optional)
        date_to: Filter reports created before this date (optional)
        
    Returns:
        ReportListResponse with paginated results
    """
    report_manager = get_report_manager()
    
    try:
        # Validate date range
        if date_from and date_to and date_from > date_to:
            from app.utils.error_handler import ValidationException
            raise ValidationException("date_from must be before date_to")
        
        # Get paginated reports
        result = report_manager.list_reports(
            page=page,
            limit=limit,
            language=language,
            status=status,
            date_from=date_from,
            date_to=date_to
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing reports: {e}")
        from app.utils.error_handler import ErrorType, CodeReviewException
        raise CodeReviewException(
            error_type=ErrorType.INTERNAL_SERVER_ERROR,
            message="Internal server error listing reports",
            details={"error": str(e)},
            status_code=500
        )


@router.delete("/review/{report_id}", response_model=DeleteResponse)
async def delete_report(report_id: str, current_user: Optional[User] = Depends(get_current_user_optional)):
    """
    Delete a specific report by ID.
    
    Args:
        report_id: Unique report identifier
        
    Returns:
        DeleteResponse indicating success or failure
        
    Raises:
        HTTPException: If report not found or deletion fails
    """
    report_manager = get_report_manager()
    
    try:
        # Check if report exists
        report = report_manager.get_report(report_id)
        if not report:
            from app.utils.error_handler import raise_not_found
            raise_not_found("Report", report_id)
        
        # Delete the report
        success = report_manager.delete_report(report_id)
        
        if not success:
            from app.utils.error_handler import ErrorType, CodeReviewException
            raise CodeReviewException(
                error_type=ErrorType.STORAGE_ERROR,
                message=f"Failed to delete report {report_id}",
                details={"report_id": report_id},
                status_code=500
            )
        
        return DeleteResponse(
            success=True,
            message=f"Report {report_id} deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting report {report_id}: {e}")
        from app.utils.error_handler import ErrorType, CodeReviewException
        raise CodeReviewException(
            error_type=ErrorType.INTERNAL_SERVER_ERROR,
            message="Internal server error deleting report",
            details={"report_id": report_id, "error": str(e)},
            status_code=500
        )


@router.get("/limits", response_model=LimitsResponse)
async def get_system_limits():
    """
    Get information about system limits and supported formats.
    
    Returns:
        LimitsResponse with format and rate limits
    """
    try:
        formats_info = file_service.get_supported_formats()
        
        return LimitsResponse(
            max_file_size_mb=formats_info["max_file_size_mb"],
            supported_languages=formats_info["languages"],
            supported_extensions=formats_info["extensions"],
            rate_limits={
                "review_per_minute": settings.rate_limit_requests_per_minute,
                "reports_per_minute": 60  # Higher limit for read operations
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting system limits: {e}")
        from app.utils.error_handler import ErrorType, CodeReviewException
        raise CodeReviewException(
            error_type=ErrorType.INTERNAL_SERVER_ERROR,
            message="Internal server error getting system limits",
            details={"error": str(e)},
            status_code=500
        )