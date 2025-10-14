"""
Report management utilities for creating and managing code review reports.
"""

from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import logging

from ..models.api_models import Report, ReportStatus, ReportSummary, ReportListResponse
from ..models.analysis_models import IssueModel, RecommendationModel, SeverityLevel
from .storage_service import get_storage_service

logger = logging.getLogger(__name__)


class ReportManager:
    """Manager class for handling report operations."""
    
    def __init__(self):
        """Initialize the report manager."""
        self.storage = get_storage_service()
    
    def create_report(
        self,
        filename: str,
        language: Optional[str] = None,
        file_size: int = 0
    ) -> Report:
        """
        Create a new report with processing status.
        
        Args:
            filename: Original filename
            language: Programming language (optional)
            file_size: File size in bytes
            
        Returns:
            New Report object with processing status
        """
        report_id = self.storage.generate_report_id()
        
        report = Report(
            report_id=report_id,
            status=ReportStatus.PROCESSING,
            filename=filename,
            language=language,
            file_size=file_size,
            created_at=datetime.now(timezone.utc)
        )
        
        # Store the initial report
        success = self.storage.store_report(report)
        if not success:
            logger.error(f"Failed to store initial report {report_id}")
            raise RuntimeError(f"Failed to create report {report_id}")
        
        logger.info(f"Created new report {report_id} for file {filename}")
        return report
    
    def complete_report(
        self,
        report_id: str,
        summary: str,
        issues: List[IssueModel],
        recommendations: List[RecommendationModel],
        processing_time_ms: Optional[int] = None
    ) -> Optional[Report]:
        """
        Mark a report as completed with analysis results.
        
        Args:
            report_id: Report identifier
            summary: Analysis summary
            issues: List of issues found
            recommendations: List of recommendations
            processing_time_ms: Processing time in milliseconds
            
        Returns:
            Updated Report object or None if not found
        """
        report = self.storage.get_report(report_id)
        if not report:
            logger.error(f"Report {report_id} not found for completion")
            return None
        
        # Calculate summary statistics
        report_summary = self._calculate_report_summary(issues, recommendations)
        
        # Update report with results
        report.status = ReportStatus.COMPLETED
        report.summary = summary
        report.report_summary = report_summary
        report.issues = issues
        report.recommendations = recommendations
        report.completed_at = datetime.now(timezone.utc)
        report.processing_time_ms = processing_time_ms
        
        # Store the updated report
        success = self.storage.store_report(report)
        if not success:
            logger.error(f"Failed to store completed report {report_id}")
            return None
        
        logger.info(f"Completed report {report_id} with {len(issues)} issues and {len(recommendations)} recommendations")
        return report
    
    def fail_report(
        self,
        report_id: str,
        error_message: str,
        processing_time_ms: Optional[int] = None
    ) -> Optional[Report]:
        """
        Mark a report as failed with error message.
        
        Args:
            report_id: Report identifier
            error_message: Error description
            processing_time_ms: Processing time in milliseconds
            
        Returns:
            Updated Report object or None if not found
        """
        report = self.storage.get_report(report_id)
        if not report:
            logger.error(f"Report {report_id} not found for failure update")
            return None
        
        # Update report with failure status
        report.status = ReportStatus.FAILED
        report.error_message = error_message
        report.completed_at = datetime.now(timezone.utc)
        report.processing_time_ms = processing_time_ms
        
        # Store the updated report
        success = self.storage.store_report(report)
        if not success:
            logger.error(f"Failed to store failed report {report_id}")
            return None
        
        logger.info(f"Marked report {report_id} as failed: {error_message}")
        return report
    
    def get_report(self, report_id: str) -> Optional[Report]:
        """
        Get a report by ID.
        
        Args:
            report_id: Report identifier
            
        Returns:
            Report object or None if not found
        """
        return self.storage.get_report(report_id)
    
    def delete_report(self, report_id: str) -> bool:
        """
        Delete a report by ID.
        
        Args:
            report_id: Report identifier
            
        Returns:
            True if successful, False otherwise
        """
        return self.storage.delete_report(report_id)
    
    def list_reports(
        self,
        page: int = 1,
        limit: int = 10,
        language: Optional[str] = None,
        status: Optional[ReportStatus] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> ReportListResponse:
        """
        List reports with pagination and filtering.
        
        Args:
            page: Page number (1-based)
            limit: Number of items per page
            language: Filter by programming language
            status: Filter by report status
            date_from: Filter reports created after this date
            date_to: Filter reports created before this date
            
        Returns:
            ReportListResponse with paginated results
        """
        # Validate pagination parameters
        page = max(1, page)
        limit = max(1, min(100, limit))  # Limit between 1 and 100
        
        # Get reports and total count
        reports = self.storage.list_reports(
            page=page,
            limit=limit,
            language=language,
            status=status,
            date_from=date_from,
            date_to=date_to
        )
        
        total = self.storage.get_report_count(
            language=language,
            status=status,
            date_from=date_from,
            date_to=date_to
        )
        
        # Calculate if there are more pages
        has_next = (page * limit) < total
        
        return ReportListResponse(
            reports=reports,
            total=total,
            page=page,
            limit=limit,
            has_next=has_next
        )
    
    def _calculate_report_summary(
        self,
        issues: List[IssueModel],
        recommendations: List[RecommendationModel]
    ) -> ReportSummary:
        """
        Calculate summary statistics for a report.
        
        Args:
            issues: List of issues
            recommendations: List of recommendations
            
        Returns:
            ReportSummary object with statistics
        """
        # Count issues by severity
        high_severity = sum(1 for issue in issues if issue.severity == SeverityLevel.HIGH)
        medium_severity = sum(1 for issue in issues if issue.severity == SeverityLevel.MEDIUM)
        low_severity = sum(1 for issue in issues if issue.severity == SeverityLevel.LOW)
        
        # Calculate average confidence
        if issues:
            avg_confidence = sum(issue.confidence for issue in issues) / len(issues)
        else:
            avg_confidence = 1.0
        
        return ReportSummary(
            total_issues=len(issues),
            high_severity_issues=high_severity,
            medium_severity_issues=medium_severity,
            low_severity_issues=low_severity,
            total_recommendations=len(recommendations),
            confidence_score=round(avg_confidence, 2)
        )
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.
        
        Returns:
            Dictionary with storage statistics
        """
        return self.storage.get_storage_stats()


# Global report manager instance
_report_manager: Optional[ReportManager] = None


def get_report_manager() -> ReportManager:
    """
    Get the global report manager instance.
    
    Returns:
        ReportManager instance
    """
    global _report_manager
    if _report_manager is None:
        _report_manager = ReportManager()
    return _report_manager