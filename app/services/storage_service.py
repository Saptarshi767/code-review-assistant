"""
Simple file-based storage service for MVP implementation.
Stores reports as JSON files with UUID naming.
"""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

from ..models.api_models import Report, ReportListItem, ReportStatus
from ..models.analysis_models import IssueModel, RecommendationModel

logger = logging.getLogger(__name__)


class StorageService:
    """Simple file-based storage service for code review reports."""
    
    def __init__(self, storage_path: str = "reports"):
        """
        Initialize the storage service.
        
        Args:
            storage_path: Directory path where reports will be stored
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        logger.info(f"Storage service initialized with path: {self.storage_path}")
    
    def _get_report_file_path(self, report_id: str) -> Path:
        """Get the file path for a report."""
        return self.storage_path / f"{report_id}.json"
    
    def _serialize_report(self, report: Report) -> Dict[str, Any]:
        """
        Serialize a Report object to a dictionary for JSON storage.
        
        Args:
            report: Report object to serialize
            
        Returns:
            Dictionary representation of the report
        """
        # Convert Pydantic model to dict with proper datetime serialization
        report_dict = report.dict()
        
        # Convert datetime objects to ISO format strings
        if report_dict.get('created_at'):
            report_dict['created_at'] = report_dict['created_at'].isoformat()
        if report_dict.get('completed_at'):
            report_dict['completed_at'] = report_dict['completed_at'].isoformat()
            
        return report_dict
    
    def _deserialize_report(self, report_dict: Dict[str, Any]) -> Report:
        """
        Deserialize a dictionary to a Report object.
        
        Args:
            report_dict: Dictionary representation of the report
            
        Returns:
            Report object
        """
        # Convert ISO format strings back to datetime objects
        if report_dict.get('created_at') and isinstance(report_dict['created_at'], str):
            report_dict['created_at'] = datetime.fromisoformat(report_dict['created_at'])
        if report_dict.get('completed_at') and isinstance(report_dict['completed_at'], str):
            report_dict['completed_at'] = datetime.fromisoformat(report_dict['completed_at'])
            
        return Report(**report_dict)
    
    def store_report(self, report: Report) -> bool:
        """
        Store a report to the file system.
        
        Args:
            report: Report object to store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self._get_report_file_path(report.report_id)
            report_dict = self._serialize_report(report)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Report {report.report_id} stored successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store report {report.report_id}: {str(e)}")
            return False
    
    def get_report(self, report_id: str) -> Optional[Report]:
        """
        Retrieve a report by ID.
        
        Args:
            report_id: Unique identifier of the report
            
        Returns:
            Report object if found, None otherwise
        """
        try:
            file_path = self._get_report_file_path(report_id)
            
            if not file_path.exists():
                logger.warning(f"Report {report_id} not found")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                report_dict = json.load(f)
            
            report = self._deserialize_report(report_dict)
            logger.info(f"Report {report_id} retrieved successfully")
            return report
            
        except Exception as e:
            logger.error(f"Failed to retrieve report {report_id}: {str(e)}")
            return None
    
    def update_report(self, report: Report) -> bool:
        """
        Update an existing report.
        
        Args:
            report: Updated report object
            
        Returns:
            True if successful, False otherwise
        """
        # For file-based storage, update is the same as store
        return self.store_report(report)
    
    def delete_report(self, report_id: str) -> bool:
        """
        Delete a report by ID.
        
        Args:
            report_id: Unique identifier of the report to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self._get_report_file_path(report_id)
            
            if not file_path.exists():
                logger.warning(f"Report {report_id} not found for deletion")
                return False
            
            file_path.unlink()
            logger.info(f"Report {report_id} deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete report {report_id}: {str(e)}")
            return False
    
    def list_reports(
        self, 
        page: int = 1, 
        limit: int = 10,
        language: Optional[str] = None,
        status: Optional[ReportStatus] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[ReportListItem]:
        """
        List reports with optional filtering and pagination.
        
        Args:
            page: Page number (1-based)
            limit: Number of items per page
            language: Filter by programming language
            status: Filter by report status
            date_from: Filter reports created after this date
            date_to: Filter reports created before this date
            
        Returns:
            List of ReportListItem objects
        """
        try:
            reports = []
            
            # Get all JSON files in the storage directory
            for file_path in self.storage_path.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        report_dict = json.load(f)
                    
                    # Apply filters
                    if language and report_dict.get('language') != language:
                        continue
                    
                    if status and report_dict.get('status') != status.value:
                        continue
                    
                    # Parse created_at for date filtering
                    created_at_str = report_dict.get('created_at')
                    if created_at_str:
                        created_at = datetime.fromisoformat(created_at_str)
                        
                        if date_from and created_at < date_from:
                            continue
                        if date_to and created_at > date_to:
                            continue
                    
                    # Create ReportListItem
                    completed_at = None
                    if report_dict.get('completed_at'):
                        completed_at = datetime.fromisoformat(report_dict['completed_at'])
                    
                    # Extract summary statistics for completed reports
                    total_issues = None
                    high_severity_issues = None
                    if report_dict.get('status') == ReportStatus.COMPLETED.value:
                        if report_dict.get('report_summary'):
                            total_issues = report_dict['report_summary'].get('total_issues')
                            high_severity_issues = report_dict['report_summary'].get('high_severity_issues')
                        elif report_dict.get('issues'):
                            # Calculate from issues if summary not available
                            issues = report_dict['issues']
                            total_issues = len(issues)
                            high_severity_issues = sum(1 for issue in issues if issue.get('severity') == 'high')
                    
                    report_item = ReportListItem(
                        report_id=report_dict['report_id'],
                        filename=report_dict['filename'],
                        language=report_dict.get('language'),
                        status=ReportStatus(report_dict['status']),
                        created_at=created_at,
                        completed_at=completed_at,
                        total_issues=total_issues,
                        high_severity_issues=high_severity_issues
                    )
                    
                    reports.append(report_item)
                    
                except Exception as e:
                    logger.warning(f"Failed to process report file {file_path}: {str(e)}")
                    continue
            
            # Sort by created_at descending (newest first)
            reports.sort(key=lambda x: x.created_at, reverse=True)
            
            # Apply pagination
            start_idx = (page - 1) * limit
            end_idx = start_idx + limit
            paginated_reports = reports[start_idx:end_idx]
            
            logger.info(f"Listed {len(paginated_reports)} reports (page {page}, limit {limit})")
            return paginated_reports
            
        except Exception as e:
            logger.error(f"Failed to list reports: {str(e)}")
            return []
    
    def get_report_count(
        self,
        language: Optional[str] = None,
        status: Optional[ReportStatus] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> int:
        """
        Get the total count of reports matching the filters.
        
        Args:
            language: Filter by programming language
            status: Filter by report status
            date_from: Filter reports created after this date
            date_to: Filter reports created before this date
            
        Returns:
            Total count of matching reports
        """
        try:
            count = 0
            
            for file_path in self.storage_path.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        report_dict = json.load(f)
                    
                    # Apply same filters as list_reports
                    if language and report_dict.get('language') != language:
                        continue
                    
                    if status and report_dict.get('status') != status.value:
                        continue
                    
                    created_at_str = report_dict.get('created_at')
                    if created_at_str:
                        created_at = datetime.fromisoformat(created_at_str)
                        
                        if date_from and created_at < date_from:
                            continue
                        if date_to and created_at > date_to:
                            continue
                    
                    count += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to process report file {file_path} for counting: {str(e)}")
                    continue
            
            return count
            
        except Exception as e:
            logger.error(f"Failed to count reports: {str(e)}")
            return 0
    
    def report_exists(self, report_id: str) -> bool:
        """
        Check if a report exists.
        
        Args:
            report_id: Unique identifier of the report
            
        Returns:
            True if report exists, False otherwise
        """
        file_path = self._get_report_file_path(report_id)
        return file_path.exists()
    
    def generate_report_id(self) -> str:
        """
        Generate a new unique report ID.
        
        Returns:
            UUID string for the new report
        """
        return str(uuid.uuid4())
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.
        
        Returns:
            Dictionary with storage statistics
        """
        try:
            total_reports = len(list(self.storage_path.glob("*.json")))
            
            # Calculate total storage size
            total_size = sum(f.stat().st_size for f in self.storage_path.glob("*.json"))
            
            # Count by status
            status_counts = {status.value: 0 for status in ReportStatus}
            
            for file_path in self.storage_path.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        report_dict = json.load(f)
                    
                    status = report_dict.get('status', 'unknown')
                    if status in status_counts:
                        status_counts[status] += 1
                        
                except Exception:
                    continue
            
            return {
                'total_reports': total_reports,
                'total_size_bytes': total_size,
                'storage_path': str(self.storage_path),
                'status_counts': status_counts
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage stats: {str(e)}")
            return {
                'total_reports': 0,
                'total_size_bytes': 0,
                'storage_path': str(self.storage_path),
                'status_counts': {},
                'error': str(e)
            }


# Global storage service instance
_storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """
    Get the global storage service instance.
    
    Returns:
        StorageService instance
    """
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service


def init_storage_service(storage_path: str = "reports") -> StorageService:
    """
    Initialize the global storage service with custom path.
    
    Args:
        storage_path: Directory path where reports will be stored
        
    Returns:
        StorageService instance
    """
    global _storage_service
    _storage_service = StorageService(storage_path)
    return _storage_service