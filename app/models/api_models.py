"""
Pydantic models for API requests and responses.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum

from .analysis_models import IssueModel, RecommendationModel, SeverityLevel


class ReportStatus(str, Enum):
    """Status values for analysis reports."""
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ReviewRequest(BaseModel):
    """Request model for code review endpoint."""
    language: Optional[str] = Field(None, description="Programming language (auto-detected if not provided)")
    ruleset: Optional[List[str]] = Field(None, description="Specific analysis rules to apply")
    async_processing: bool = Field(False, description="Whether to process asynchronously")
    
    class Config:
        schema_extra = {
            "example": {
                "language": "python",
                "ruleset": ["security", "performance"],
                "async_processing": False
            }
        }


class ReviewResponse(BaseModel):
    """Response model for code review submission."""
    report_id: str = Field(..., description="Unique identifier for the analysis report")
    status: ReportStatus = Field(..., description="Current processing status")
    filename: str = Field(..., description="Original filename")
    language: Optional[str] = Field(None, description="Detected or specified programming language")
    estimated_time: Optional[int] = Field(None, description="Estimated processing time in seconds")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Report creation timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "report_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "processing",
                "filename": "example.py",
                "language": "python",
                "estimated_time": 30,
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


class ReportSummary(BaseModel):
    """Summary statistics for a code review report."""
    total_issues: int = Field(0, ge=0, description="Total number of issues found")
    high_severity_issues: int = Field(0, ge=0, description="Number of high severity issues")
    medium_severity_issues: int = Field(0, ge=0, description="Number of medium severity issues")
    low_severity_issues: int = Field(0, ge=0, description="Number of low severity issues")
    total_recommendations: int = Field(0, ge=0, description="Total number of recommendations")
    confidence_score: float = Field(0.0, ge=0.0, le=1.0, description="Overall confidence score")
    
    @validator('total_issues')
    def validate_total_issues(cls, v, values):
        """Ensure total issues matches sum of severity counts."""
        if all(key in values for key in ['high_severity_issues', 'medium_severity_issues', 'low_severity_issues']):
            expected_total = values['high_severity_issues'] + values['medium_severity_issues'] + values['low_severity_issues']
            if v != expected_total:
                return expected_total
        return v


class Report(BaseModel):
    """Complete report model for API responses."""
    report_id: str = Field(..., description="Unique identifier for the report")
    status: ReportStatus = Field(..., description="Current processing status")
    filename: str = Field(..., description="Original filename")
    language: Optional[str] = Field(None, description="Programming language")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    
    # Analysis results (only present when status is 'completed')
    summary: Optional[str] = Field(None, description="Analysis summary")
    report_summary: Optional[ReportSummary] = Field(None, description="Report statistics")
    issues: List[IssueModel] = Field(default_factory=list, description="List of issues found")
    recommendations: List[RecommendationModel] = Field(default_factory=list, description="List of recommendations")
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Report creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Report completion timestamp")
    processing_time_ms: Optional[int] = Field(None, description="Processing time in milliseconds")
    error_message: Optional[str] = Field(None, description="Error message if processing failed")
    
    class Config:
        schema_extra = {
            "example": {
                "report_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "completed",
                "filename": "example.py",
                "language": "python",
                "file_size": 1024,
                "summary": "Code analysis completed successfully",
                "report_summary": {
                    "total_issues": 3,
                    "high_severity_issues": 1,
                    "medium_severity_issues": 2,
                    "low_severity_issues": 0,
                    "total_recommendations": 2,
                    "confidence_score": 0.85
                },
                "created_at": "2024-01-15T10:30:00Z",
                "completed_at": "2024-01-15T10:30:45Z",
                "processing_time_ms": 45000
            }
        }


class ReportListItem(BaseModel):
    """Simplified report model for list responses."""
    report_id: str = Field(..., description="Unique identifier for the report")
    filename: str = Field(..., description="Original filename")
    language: Optional[str] = Field(None, description="Programming language")
    status: ReportStatus = Field(..., description="Current processing status")
    created_at: datetime = Field(..., description="Report creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Report completion timestamp")
    
    # Summary statistics (only for completed reports)
    total_issues: Optional[int] = Field(None, description="Total number of issues found")
    high_severity_issues: Optional[int] = Field(None, description="Number of high severity issues")
    
    class Config:
        schema_extra = {
            "example": {
                "report_id": "550e8400-e29b-41d4-a716-446655440000",
                "filename": "example.py",
                "language": "python",
                "status": "completed",
                "created_at": "2024-01-15T10:30:00Z",
                "completed_at": "2024-01-15T10:30:45Z",
                "total_issues": 3,
                "high_severity_issues": 1
            }
        }


class ReportListResponse(BaseModel):
    """Response model for report listing endpoint."""
    reports: List[ReportListItem] = Field(..., description="List of reports")
    total: int = Field(..., ge=0, description="Total number of reports")
    page: int = Field(1, ge=1, description="Current page number")
    limit: int = Field(10, ge=1, le=100, description="Number of items per page")
    has_next: bool = Field(False, description="Whether there are more pages")
    
    class Config:
        schema_extra = {
            "example": {
                "reports": [
                    {
                        "report_id": "550e8400-e29b-41d4-a716-446655440000",
                        "filename": "example.py",
                        "language": "python",
                        "status": "completed",
                        "created_at": "2024-01-15T10:30:00Z",
                        "completed_at": "2024-01-15T10:30:45Z",
                        "total_issues": 3,
                        "high_severity_issues": 1
                    }
                ],
                "total": 1,
                "page": 1,
                "limit": 10,
                "has_next": False
            }
        }


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Overall system status")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Health check timestamp")
    services: Dict[str, str] = Field(..., description="Status of individual services")
    version: Optional[str] = Field(None, description="Application version")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-15T10:30:00Z",
                "services": {
                    "database": "healthy",
                    "llm_service": "healthy",
                    "file_storage": "healthy"
                },
                "version": "1.0.0"
            }
        }


class LimitsResponse(BaseModel):
    """Response model for system limits endpoint."""
    max_file_size_mb: int = Field(..., description="Maximum file size in MB")
    supported_languages: List[str] = Field(..., description="List of supported programming languages")
    supported_extensions: List[str] = Field(..., description="List of supported file extensions")
    rate_limits: Dict[str, int] = Field(..., description="Rate limits per endpoint")
    
    class Config:
        schema_extra = {
            "example": {
                "max_file_size_mb": 10,
                "supported_languages": ["python", "javascript", "typescript", "java", "go"],
                "supported_extensions": [".py", ".js", ".ts", ".java", ".go"],
                "rate_limits": {
                    "review_per_minute": 10,
                    "reports_per_minute": 60
                }
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str = Field(..., description="Error type or code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    request_id: Optional[str] = Field(None, description="Request identifier for tracking")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Error timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "VALIDATION_ERROR",
                "message": "File size exceeds maximum limit",
                "details": {
                    "max_size_mb": 10,
                    "actual_size_mb": 15
                },
                "request_id": "req_123456789",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class DeleteResponse(BaseModel):
    """Response model for delete operations."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Operation result message")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Report deleted successfully"
            }
        }