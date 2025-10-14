"""
Unit tests for API endpoints.
Tests API request/response handling and various input scenarios.
"""

import pytest
import json
import io
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import status

from main import app
from app.models.api_models import ReportStatus
from app.auth.models import User


class TestReviewEndpoints:
    """Test review API endpoints."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def test_upload_file_success(self, sample_python_code, mock_user):
        """Test successful file upload and review."""
        # Mock authentication
        with patch('app.api.review.api_key_auth', return_value=mock_user):
            # Mock file service validation
            with patch('app.services.file_service.file_service.validate_file') as mock_validate:
                mock_validate.return_value = Mock(
                    valid=True,
                    errors=[],
                    file_size=len(sample_python_code),
                    detected_type=".py",
                    language="python"
                )
                
                # Mock file processing
                with patch('app.services.file_service.file_service.process_file') as mock_process:
                    mock_process.return_value = Mock(
                        filename="test.py",
                        language="python",
                        content=sample_python_code,
                        size=len(sample_python_code),
                        sanitized=Mock(content=sample_python_code),
                        extracted_files=[]
                    )
                    
                    # Mock report manager
                    with patch('app.services.report_manager.get_report_manager') as mock_rm:
                        mock_report = Mock(report_id="test-report-123")
                        mock_rm.return_value.create_report.return_value = mock_report
                        mock_rm.return_value.complete_report.return_value = mock_report
                        
                        # Mock LLM analysis
                        with patch('app.api.review._perform_code_analysis') as mock_analysis:
                            mock_analysis.return_value = Mock(
                                summary="Analysis complete",
                                issues=[],
                                recommendations=[],
                                processing_time=1.0
                            )
                            
                            # Mock analysis processor
                            with patch('app.services.analysis_processor.analysis_processor.parse_llm_response') as mock_parser:
                                mock_parser.return_value = Mock(
                                    summary="Analysis complete",
                                    issues=[],
                                    recommendations=[]
                                )
                                
                                # Make request
                                files = {"file": ("test.py", sample_python_code, "text/plain")}
                                response = self.client.post("/api/review", files=files)
                                
                                assert response.status_code == status.HTTP_200_OK
                                data = response.json()
                                assert data["report_id"] == "test-report-123"
                                assert data["status"] == ReportStatus.COMPLETED
                                assert data["filename"] == "test.py"
                                assert data["language"] == "python"
    
    def test_upload_file_validation_error(self, mock_user):
        """Test file upload with validation errors."""
        with patch('app.api.review.api_key_auth', return_value=mock_user):
            with patch('app.services.file_service.file_service.validate_file') as mock_validate:
                mock_validate.return_value = Mock(
                    valid=False,
                    errors=[Mock(message="File too large", code="FILE_TOO_LARGE")],
                    file_size=0,
                    detected_type="",
                    language=None
                )
                
                files = {"file": ("large.py", "x" * 1000, "text/plain")}
                response = self.client.post("/api/review", files=files)
                
                assert response.status_code == status.HTTP_400_BAD_REQUEST
                data = response.json()
                assert "validation failed" in data["error"]["message"].lower()
    
    def test_upload_file_async_processing(self, sample_python_code, mock_user):
        """Test file upload with async processing flag."""
        with patch('app.api.review.api_key_auth', return_value=mock_user):
            with patch('app.services.file_service.file_service.validate_file') as mock_validate:
                mock_validate.return_value = Mock(
                    valid=True,
                    errors=[],
                    file_size=len(sample_python_code),
                    detected_type=".py",
                    language="python"
                )
                
                with patch('app.services.file_service.file_service.process_file') as mock_process:
                    mock_process.return_value = Mock(
                        filename="test.py",
                        language="python",
                        sanitized=Mock(content=sample_python_code)
                    )
                    
                    with patch('app.services.report_manager.get_report_manager') as mock_rm:
                        mock_report = Mock(report_id="async-report-123")
                        mock_rm.return_value.create_report.return_value = mock_report
                        
                        files = {"file": ("test.py", sample_python_code, "text/plain")}
                        response = self.client.post("/api/review?async_processing=true", files=files)
                        
                        assert response.status_code == status.HTTP_200_OK
                        data = response.json()
                        assert data["status"] == ReportStatus.PROCESSING
                        assert "estimated_time" in data
    
    def test_upload_file_large_file_auto_async(self, mock_user):
        """Test that large files automatically trigger async processing."""
        large_content = "x" * (2 * 1024 * 1024)  # 2MB file
        
        with patch('app.api.review.api_key_auth', return_value=mock_user):
            with patch('app.services.file_service.file_service.validate_file') as mock_validate:
                mock_validate.return_value = Mock(
                    valid=True,
                    errors=[],
                    file_size=len(large_content),
                    detected_type=".py",
                    language="python"
                )
                
                with patch('app.services.file_service.file_service.process_file') as mock_process:
                    mock_process.return_value = Mock(
                        filename="large.py",
                        language="python",
                        sanitized=Mock(content=large_content)
                    )
                    
                    with patch('app.services.report_manager.get_report_manager') as mock_rm:
                        mock_report = Mock(report_id="large-report-123")
                        mock_rm.return_value.create_report.return_value = mock_report
                        
                        files = {"file": ("large.py", large_content, "text/plain")}
                        response = self.client.post("/api/review", files=files)
                        
                        assert response.status_code == status.HTTP_200_OK
                        data = response.json()
                        assert data["status"] == ReportStatus.PROCESSING
    
    def test_upload_file_analysis_error(self, sample_python_code, mock_user):
        """Test file upload with analysis error."""
        with patch('app.api.review.api_key_auth', return_value=mock_user):
            with patch('app.services.file_service.file_service.validate_file') as mock_validate:
                mock_validate.return_value = Mock(
                    valid=True,
                    errors=[],
                    file_size=len(sample_python_code),
                    detected_type=".py",
                    language="python"
                )
                
                with patch('app.services.file_service.file_service.process_file') as mock_process:
                    mock_process.return_value = Mock(
                        filename="test.py",
                        language="python",
                        sanitized=Mock(content=sample_python_code)
                    )
                    
                    with patch('app.services.report_manager.get_report_manager') as mock_rm:
                        mock_report = Mock(report_id="error-report-123")
                        mock_rm.return_value.create_report.return_value = mock_report
                        mock_rm.return_value.fail_report.return_value = None
                        
                        # Mock analysis to raise error
                        with patch('app.api.review._perform_code_analysis') as mock_analysis:
                            mock_analysis.side_effect = Exception("LLM service error")
                            
                            files = {"file": ("test.py", sample_python_code, "text/plain")}
                            response = self.client.post("/api/review", files=files)
                            
                            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
                            data = response.json()
                            assert "analysis failed" in data["error"]["message"].lower()
    
    def test_upload_file_without_authentication(self, sample_python_code):
        """Test file upload without authentication."""
        files = {"file": ("test.py", sample_python_code, "text/plain")}
        response = self.client.post("/api/review", files=files)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_report_success(self, mock_user):
        """Test successful report retrieval."""
        with patch('app.api.review.api_key_auth', return_value=mock_user):
            with patch('app.services.report_manager.get_report_manager') as mock_rm:
                mock_report = Mock(
                    report_id="test-report-123",
                    filename="test.py",
                    language="python",
                    status=ReportStatus.COMPLETED,
                    summary="Analysis complete",
                    issues=[],
                    recommendations=[]
                )
                mock_rm.return_value.get_report.return_value = mock_report
                
                response = self.client.get("/api/review/test-report-123")
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["report_id"] == "test-report-123"
                assert data["filename"] == "test.py"
    
    def test_get_report_not_found(self, mock_user):
        """Test report retrieval for non-existent report."""
        with patch('app.api.review.api_key_auth', return_value=mock_user):
            with patch('app.services.report_manager.get_report_manager') as mock_rm:
                mock_rm.return_value.get_report.return_value = None
                
                response = self.client.get("/api/review/nonexistent-report")
                
                assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_list_reports_success(self, mock_user):
        """Test successful report listing."""
        with patch('app.api.review.api_key_auth', return_value=mock_user):
            with patch('app.services.report_manager.get_report_manager') as mock_rm:
                mock_reports = [
                    Mock(report_id="report-1", filename="test1.py"),
                    Mock(report_id="report-2", filename="test2.js")
                ]
                mock_result = Mock(
                    reports=mock_reports,
                    total=2,
                    page=1,
                    limit=10
                )
                mock_rm.return_value.list_reports.return_value = mock_result
                
                response = self.client.get("/api/reviews")
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert len(data["reports"]) == 2
                assert data["total"] == 2
                assert data["page"] == 1
    
    def test_list_reports_with_filters(self, mock_user):
        """Test report listing with filters."""
        with patch('app.api.review.api_key_auth', return_value=mock_user):
            with patch('app.services.report_manager.get_report_manager') as mock_rm:
                mock_result = Mock(reports=[], total=0, page=1, limit=10)
                mock_rm.return_value.list_reports.return_value = mock_result
                
                response = self.client.get(
                    "/api/reviews?language=python&status=completed&page=2&limit=5"
                )
                
                assert response.status_code == status.HTTP_200_OK
                # Verify filters were passed to report manager
                mock_rm.return_value.list_reports.assert_called_once()
                call_args = mock_rm.return_value.list_reports.call_args
                assert call_args.kwargs["language"] == "python"
                assert call_args.kwargs["page"] == 2
                assert call_args.kwargs["limit"] == 5
    
    def test_list_reports_invalid_date_range(self, mock_user):
        """Test report listing with invalid date range."""
        with patch('app.api.review.api_key_auth', return_value=mock_user):
            response = self.client.get(
                "/api/reviews?date_from=2024-12-01&date_to=2024-11-01"
            )
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            data = response.json()
            assert "date_from must be before date_to" in data["error"]["message"]
    
    def test_delete_report_success(self, mock_user):
        """Test successful report deletion."""
        with patch('app.api.review.api_key_auth', return_value=mock_user):
            with patch('app.services.report_manager.get_report_manager') as mock_rm:
                mock_report = Mock(report_id="test-report-123")
                mock_rm.return_value.get_report.return_value = mock_report
                mock_rm.return_value.delete_report.return_value = True
                
                response = self.client.delete("/api/review/test-report-123")
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["success"] is True
                assert "deleted successfully" in data["message"]
    
    def test_delete_report_not_found(self, mock_user):
        """Test deleting non-existent report."""
        with patch('app.api.review.api_key_auth', return_value=mock_user):
            with patch('app.services.report_manager.get_report_manager') as mock_rm:
                mock_rm.return_value.get_report.return_value = None
                
                response = self.client.delete("/api/review/nonexistent-report")
                
                assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_report_failure(self, mock_user):
        """Test report deletion failure."""
        with patch('app.api.review.api_key_auth', return_value=mock_user):
            with patch('app.services.report_manager.get_report_manager') as mock_rm:
                mock_report = Mock(report_id="test-report-123")
                mock_rm.return_value.get_report.return_value = mock_report
                mock_rm.return_value.delete_report.return_value = False
                
                response = self.client.delete("/api/review/test-report-123")
                
                assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
                data = response.json()
                assert "failed to delete" in data["error"]["message"].lower()
    
    def test_get_system_limits(self):
        """Test getting system limits."""
        with patch('app.services.file_service.file_service.get_supported_formats') as mock_formats:
            mock_formats.return_value = {
                "max_file_size_mb": 10,
                "languages": ["python", "javascript"],
                "extensions": [".py", ".js"]
            }
            
            response = self.client.get("/api/limits")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["max_file_size_mb"] == 10
            assert "python" in data["supported_languages"]
            assert ".py" in data["supported_extensions"]
            assert "rate_limits" in data


class TestAPIInputValidation:
    """Test API input validation scenarios."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def test_upload_file_missing_file(self, mock_user):
        """Test upload endpoint without file."""
        with patch('app.api.review.api_key_auth', return_value=mock_user):
            response = self.client.post("/api/review")
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_upload_file_empty_file(self, mock_user):
        """Test upload with empty file."""
        with patch('app.api.review.api_key_auth', return_value=mock_user):
            files = {"file": ("empty.py", "", "text/plain")}
            
            with patch('app.services.file_service.file_service.validate_file') as mock_validate:
                mock_validate.return_value = Mock(
                    valid=False,
                    errors=[Mock(message="Empty file", code="EMPTY_FILE")],
                    file_size=0
                )
                
                response = self.client.post("/api/review", files=files)
                
                assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_list_reports_invalid_pagination(self, mock_user):
        """Test report listing with invalid pagination parameters."""
        with patch('app.api.review.api_key_auth', return_value=mock_user):
            # Test negative page number
            response = self.client.get("/api/reviews?page=-1")
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            
            # Test zero page number
            response = self.client.get("/api/reviews?page=0")
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            
            # Test excessive limit
            response = self.client.get("/api/reviews?limit=1000")
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_get_report_invalid_id_format(self, mock_user):
        """Test getting report with invalid ID format."""
        with patch('app.api.review.api_key_auth', return_value=mock_user):
            with patch('app.services.report_manager.get_report_manager') as mock_rm:
                mock_rm.return_value.get_report.return_value = None
                
                # Test with various invalid formats
                invalid_ids = ["", "   ", "invalid-id-format", "123"]
                
                for invalid_id in invalid_ids:
                    response = self.client.get(f"/api/review/{invalid_id}")
                    assert response.status_code == status.HTTP_404_NOT_FOUND


class TestAPIErrorHandling:
    """Test API error handling scenarios."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def test_upload_file_internal_error(self, sample_python_code, mock_user):
        """Test handling of unexpected internal errors."""
        with patch('app.api.review.api_key_auth', return_value=mock_user):
            with patch('app.services.file_service.file_service.validate_file') as mock_validate:
                mock_validate.side_effect = Exception("Unexpected error")
                
                files = {"file": ("test.py", sample_python_code, "text/plain")}
                response = self.client.post("/api/review", files=files)
                
                assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
                data = response.json()
                assert "internal server error" in data["error"]["message"].lower()
    
    def test_get_report_internal_error(self, mock_user):
        """Test handling of internal errors in report retrieval."""
        with patch('app.api.review.api_key_auth', return_value=mock_user):
            with patch('app.services.report_manager.get_report_manager') as mock_rm:
                mock_rm.return_value.get_report.side_effect = Exception("Database error")
                
                response = self.client.get("/api/review/test-report-123")
                
                assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
                data = response.json()
                assert "internal server error" in data["error"]["message"].lower()
    
    def test_list_reports_internal_error(self, mock_user):
        """Test handling of internal errors in report listing."""
        with patch('app.api.review.api_key_auth', return_value=mock_user):
            with patch('app.services.report_manager.get_report_manager') as mock_rm:
                mock_rm.return_value.list_reports.side_effect = Exception("Service unavailable")
                
                response = self.client.get("/api/reviews")
                
                assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def test_get_limits_internal_error(self):
        """Test handling of internal errors in limits endpoint."""
        with patch('app.services.file_service.file_service.get_supported_formats') as mock_formats:
            mock_formats.side_effect = Exception("Configuration error")
            
            response = self.client.get("/api/limits")
            
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestAPIResponseFormats:
    """Test API response format consistency."""
    
    def setup_method(self):
        """Set up test client."""
        self.client = TestClient(app)
    
    def test_error_response_format(self, mock_user):
        """Test that error responses follow consistent format."""
        with patch('app.api.review.api_key_auth', return_value=mock_user):
            with patch('app.services.file_service.file_service.validate_file') as mock_validate:
                mock_validate.return_value = Mock(
                    valid=False,
                    errors=[Mock(message="Test error", code="TEST_ERROR")],
                    file_size=0
                )
                
                files = {"file": ("test.py", "content", "text/plain")}
                response = self.client.post("/api/review", files=files)
                
                assert response.status_code == status.HTTP_400_BAD_REQUEST
                data = response.json()
                
                # Check error response structure
                assert "error" in data
                assert "type" in data["error"]
                assert "message" in data["error"]
                assert "details" in data["error"]
    
    def test_success_response_format(self, sample_python_code, mock_user):
        """Test that success responses follow consistent format."""
        with patch('app.api.review.api_key_auth', return_value=mock_user):
            with patch('app.services.file_service.file_service.validate_file') as mock_validate:
                mock_validate.return_value = Mock(
                    valid=True,
                    errors=[],
                    file_size=len(sample_python_code),
                    detected_type=".py",
                    language="python"
                )
                
                with patch('app.services.file_service.file_service.process_file') as mock_process:
                    mock_process.return_value = Mock(
                        filename="test.py",
                        language="python",
                        sanitized=Mock(content=sample_python_code)
                    )
                    
                    with patch('app.services.report_manager.get_report_manager') as mock_rm:
                        mock_report = Mock(report_id="test-report-123")
                        mock_rm.return_value.create_report.return_value = mock_report
                        
                        files = {"file": ("test.py", sample_python_code, "text/plain")}
                        response = self.client.post("/api/review?async_processing=true", files=files)
                        
                        assert response.status_code == status.HTTP_200_OK
                        data = response.json()
                        
                        # Check success response structure
                        assert "report_id" in data
                        assert "status" in data
                        assert "filename" in data
                        assert "language" in data