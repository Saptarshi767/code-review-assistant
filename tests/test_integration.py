"""
Integration tests for complete workflows.
Tests upload-to-report workflow, error handling, and authentication.
"""

import pytest
import tempfile
import os
import json
import time
import io
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import status

from main import app
from app.models.api_models import ReportStatus
from app.auth.models import User, RateLimitTier


class TestUploadToReportWorkflow:
    """Test complete upload-to-report integration workflow."""
    
    def setup_method(self):
        """Set up test environment."""
        self.client = TestClient(app)
        self.test_user = User(
            id="integration-test-user",
            api_key="integration-test-key",
            email="integration@test.com",
            rate_limit_tier=RateLimitTier.STANDARD,
            created_at="2024-01-01T00:00:00Z",
            is_active=True
        )
    
    def test_complete_python_file_workflow(self, sample_python_code, mock_llm_response):
        """Test complete workflow from Python file upload to report generation."""
        # Mock authentication
        with patch('app.auth.middleware.user_store.validate_api_key', return_value=self.test_user):
            with patch('app.auth.middleware.rate_limiter.check_rate_limit', return_value=(True, 0, 10)):
                with patch('app.auth.middleware.rate_limiter.record_request'):
                    # Mock LLM service
                    with patch('app.services.llm_service.llm_service') as mock_llm:
                        mock_llm.chunk_code.return_value = [Mock(
                            content=sample_python_code,
                            start_line=1,
                            end_line=25,
                            context="Full file",
                            language="python"
                        )]
                        mock_llm.analyze_code.return_value = mock_llm_response
                        
                        # Create file upload
                        files = {
                            "file": ("security_test.py", sample_python_code, "text/plain")
                        }
                        
                        # Make request
                        response = self.client.post(
                            "/api/review",
                            files=files,
                            headers={"Authorization": "Bearer integration-test-key"}
                        )
                        
                        # Verify response
                        assert response.status_code == 200
                        data = response.json()
                        
                        assert "report_id" in data
                        assert data["status"] == "completed"
                        assert data["filename"] == "security_test.py"
                        assert data["language"] == "python"
                        
                        # Verify report can be retrieved
                        report_id = data["report_id"]
                        get_response = self.client.get(
                            f"/api/review/{report_id}",
                            headers={"Authorization": "Bearer integration-test-key"}
                        )
                        
                        assert get_response.status_code == 200
                        report_data = get_response.json()
                        
                        assert report_data["report_id"] == report_id
                        assert report_data["status"] == "completed"
                        assert len(report_data["issues"]) > 0
                        assert len(report_data["recommendations"]) > 0
    
    def test_complete_javascript_file_workflow(self, sample_javascript_code, mock_llm_response):
        """Test complete workflow with JavaScript file."""
        with patch('app.auth.middleware.user_store.validate_api_key', return_value=self.test_user):
            with patch('app.auth.middleware.rate_limiter.check_rate_limit', return_value=(True, 0, 10)):
                with patch('app.auth.middleware.rate_limiter.record_request'):
                    with patch('app.services.llm_service.llm_service') as mock_llm:
                        mock_llm.chunk_code.return_value = [Mock(
                            content=sample_javascript_code,
                            start_line=1,
                            end_line=20,
                            context="Full file",
                            language="javascript"
                        )]
                        mock_llm.analyze_code.return_value = mock_llm_response
                        
                        files = {
                            "file": ("auth.js", sample_javascript_code, "text/plain")
                        }
                        
                        response = self.client.post(
                            "/api/review",
                            files=files,
                            headers={"Authorization": "Bearer integration-test-key"}
                        )
                        
                        assert response.status_code == 200
                        data = response.json()
                        assert data["language"] == "javascript"
    
    def test_zip_file_workflow(self, zip_file_content, mock_llm_response):
        """Test workflow with zip file containing multiple source files."""
        with patch('app.auth.middleware.user_store.validate_api_key', return_value=self.test_user):
            with patch('app.auth.middleware.rate_limiter.check_rate_limit', return_value=(True, 0, 10)):
                with patch('app.auth.middleware.rate_limiter.record_request'):
                    with patch('app.services.llm_service.llm_service') as mock_llm:
                        mock_llm.chunk_code.return_value = [Mock(
                            content="print('Hello, World!')",
                            start_line=1,
                            end_line=1,
                            context="Simple script",
                            language="python"
                        )]
                        mock_llm.analyze_code.return_value = mock_llm_response
                        
                        files = {
                            "file": ("project.zip", zip_file_content, "application/zip")
                        }
                        
                        response = self.client.post(
                            "/api/review",
                            files=files,
                            headers={"Authorization": "Bearer integration-test-key"}
                        )
                        
                        assert response.status_code == 200
                        data = response.json()
                        assert "report_id" in data


class TestErrorHandling:
    """Test error handling for edge cases."""
    
    def setup_method(self):
        """Set up test environment."""
        self.client = TestClient(app)
        self.test_user = User(
            id="error-test-user",
            api_key="error-test-key",
            email="error@test.com",
            rate_limit_tier=RateLimitTier.STANDARD,
            created_at="2024-01-01T00:00:00Z",
            is_active=True
        )
    
    def test_file_too_large_error(self, large_file_content):
        """Test handling of files exceeding size limit."""
        with patch('app.auth.middleware.user_store.validate_api_key', return_value=self.test_user):
            with patch('app.auth.middleware.rate_limiter.check_rate_limit', return_value=(True, 0, 10)):
                with patch('app.auth.middleware.rate_limiter.record_request'):
                    files = {
                        "file": ("large_file.py", large_file_content, "text/plain")
                    }
                    
                    response = self.client.post(
                        "/api/review",
                        files=files,
                        headers={"Authorization": "Bearer error-test-key"}
                    )
                    
                    assert response.status_code == 400
                    data = response.json()
                    assert "error" in data
                    assert "too large" in data["error"]["message"].lower()
    
    def test_unsupported_file_type_error(self, binary_file_content):
        """Test handling of unsupported file types."""
        with patch('app.auth.middleware.user_store.validate_api_key', return_value=self.test_user):
            with patch('app.auth.middleware.rate_limiter.check_rate_limit', return_value=(True, 0, 10)):
                with patch('app.auth.middleware.rate_limiter.record_request'):
                    files = {
                        "file": ("image.png", binary_file_content, "image/png")
                    }
                    
                    response = self.client.post(
                        "/api/review",
                        files=files,
                        headers={"Authorization": "Bearer error-test-key"}
                    )
                    
                    assert response.status_code == 400
                    data = response.json()
                    assert "error" in data
                    assert "validation" in data["error"]["message"].lower()
    
    def test_llm_service_error_handling(self, sample_python_code):
        """Test handling of LLM service failures."""
        with patch('app.auth.middleware.user_store.validate_api_key', return_value=self.test_user):
            with patch('app.auth.middleware.rate_limiter.check_rate_limit', return_value=(True, 0, 10)):
                with patch('app.auth.middleware.rate_limiter.record_request'):
                    # Mock LLM service to raise an exception
                    with patch('app.services.llm_service.llm_service') as mock_llm:
                        mock_llm.chunk_code.return_value = [Mock()]
                        mock_llm.analyze_code.side_effect = Exception("LLM service unavailable")
                        
                        files = {
                            "file": ("test.py", sample_python_code, "text/plain")
                        }
                        
                        response = self.client.post(
                            "/api/review",
                            files=files,
                            headers={"Authorization": "Bearer error-test-key"}
                        )
                        
                        assert response.status_code == 500
                        data = response.json()
                        assert "error" in data
                        assert "analysis failed" in data["error"]["message"].lower()
    
    def test_invalid_report_id_error(self):
        """Test handling of invalid report ID requests."""
        with patch('app.auth.middleware.user_store.validate_api_key', return_value=self.test_user):
            with patch('app.auth.middleware.rate_limiter.check_rate_limit', return_value=(True, 0, 10)):
                with patch('app.auth.middleware.rate_limiter.record_request'):
                    response = self.client.get(
                        "/api/review/invalid-report-id",
                        headers={"Authorization": "Bearer error-test-key"}
                    )
                    
                    assert response.status_code == 404
                    data = response.json()
                    assert "error" in data
                    assert "not found" in data["error"]["message"].lower()
    
    def test_malformed_request_error(self):
        """Test handling of malformed requests."""
        with patch('app.auth.middleware.user_store.validate_api_key', return_value=self.test_user):
            with patch('app.auth.middleware.rate_limiter.check_rate_limit', return_value=(True, 0, 10)):
                with patch('app.auth.middleware.rate_limiter.record_request'):
                    # Send request without file
                    response = self.client.post(
                        "/api/review",
                        headers={"Authorization": "Bearer error-test-key"}
                    )
                    
                    assert response.status_code == 422  # Validation error


class TestAuthentication:
    """Test authentication and authorization."""
    
    def setup_method(self):
        """Set up test environment."""
        self.client = TestClient(app)
        self.valid_user = User(
            id="auth-test-user",
            api_key="valid-api-key",
            email="auth@test.com",
            rate_limit_tier=RateLimitTier.STANDARD,
            created_at="2024-01-01T00:00:00Z",
            is_active=True
        )
        self.inactive_user = User(
            id="inactive-user",
            api_key="inactive-api-key",
            email="inactive@test.com",
            rate_limit_tier=RateLimitTier.STANDARD,
            created_at="2024-01-01T00:00:00Z",
            is_active=False
        )
    
    def test_valid_api_key_authentication(self, sample_python_code):
        """Test successful authentication with valid API key."""
        with patch('app.auth.middleware.user_store.validate_api_key', return_value=self.valid_user):
            with patch('app.auth.middleware.rate_limiter.check_rate_limit', return_value=(True, 0, 10)):
                with patch('app.auth.middleware.rate_limiter.record_request'):
                    files = {
                        "file": ("test.py", sample_python_code, "text/plain")
                    }
                    
                    response = self.client.post(
                        "/api/review",
                        files=files,
                        headers={"Authorization": "Bearer valid-api-key"}
                    )
                    
                    # Should not get authentication error
                    assert response.status_code != 401
    
    def test_invalid_api_key_authentication(self, sample_python_code):
        """Test authentication failure with invalid API key."""
        with patch('app.auth.middleware.user_store.validate_api_key', return_value=None):
            files = {
                "file": ("test.py", sample_python_code, "text/plain")
            }
            
            response = self.client.post(
                "/api/review",
                files=files,
                headers={"Authorization": "Bearer invalid-api-key"}
            )
            
            assert response.status_code == 401
            data = response.json()
            assert "error" in data["detail"]
            assert "invalid" in data["detail"]["message"].lower()
    
    def test_missing_api_key_authentication(self, sample_python_code):
        """Test authentication failure with missing API key."""
        files = {
            "file": ("test.py", sample_python_code, "text/plain")
        }
        
        response = self.client.post("/api/review", files=files)
        
        assert response.status_code == 401
        data = response.json()
        assert "required" in data["detail"]["message"].lower()
    
    def test_x_api_key_header_authentication(self, sample_python_code):
        """Test authentication using X-API-Key header."""
        with patch('app.auth.middleware.user_store.validate_api_key', return_value=self.valid_user):
            with patch('app.auth.middleware.rate_limiter.check_rate_limit', return_value=(True, 0, 10)):
                with patch('app.auth.middleware.rate_limiter.record_request'):
                    files = {
                        "file": ("test.py", sample_python_code, "text/plain")
                    }
                    
                    response = self.client.post(
                        "/api/review",
                        files=files,
                        headers={"X-API-Key": "valid-api-key"}
                    )
                    
                    assert response.status_code != 401
    
    def test_inactive_user_authentication(self, sample_python_code):
        """Test authentication failure with inactive user."""
        with patch('app.auth.middleware.user_store.validate_api_key', return_value=None):  # Inactive users return None
            files = {
                "file": ("test.py", sample_python_code, "text/plain")
            }
            
            response = self.client.post(
                "/api/review",
                files=files,
                headers={"Authorization": "Bearer inactive-api-key"}
            )
            
            assert response.status_code == 401


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.client = TestClient(app)
        self.basic_user = User(
            id="basic-user",
            api_key="basic-api-key",
            email="basic@test.com",
            rate_limit_tier=RateLimitTier.BASIC,
            created_at="2024-01-01T00:00:00Z",
            is_active=True
        )
        self.premium_user = User(
            id="premium-user",
            api_key="premium-api-key",
            email="premium@test.com",
            rate_limit_tier=RateLimitTier.PREMIUM,
            created_at="2024-01-01T00:00:00Z",
            is_active=True
        )
    
    def test_rate_limit_enforcement(self, sample_python_code):
        """Test that rate limits are enforced."""
        with patch('app.auth.middleware.user_store.validate_api_key', return_value=self.basic_user):
            # Mock rate limiter to simulate limit exceeded
            with patch('app.auth.middleware.rate_limiter.check_rate_limit', return_value=(False, 5, 5)):
                with patch('app.auth.middleware.rate_limiter.get_reset_time') as mock_reset:
                    from datetime import datetime, timedelta
                    mock_reset.return_value = datetime.utcnow() + timedelta(minutes=1)
                    
                    files = {
                        "file": ("test.py", sample_python_code, "text/plain")
                    }
                    
                    response = self.client.post(
                        "/api/review",
                        files=files,
                        headers={"Authorization": "Bearer basic-api-key"}
                    )
                    
                    assert response.status_code == 429
                    data = response.json()
                    assert "rate limit" in data["detail"]["message"].lower()
                    
                    # Check rate limit headers
                    assert "Retry-After" in response.headers
                    assert "X-RateLimit-Limit" in response.headers
                    assert "X-RateLimit-Remaining" in response.headers
    
    def test_rate_limit_headers_on_success(self, sample_python_code):
        """Test that rate limit headers are included on successful requests."""
        with patch('app.auth.middleware.user_store.validate_api_key', return_value=self.basic_user):
            with patch('app.auth.middleware.rate_limiter.check_rate_limit', return_value=(True, 2, 5)):
                with patch('app.auth.middleware.rate_limiter.record_request'):
                    with patch('app.auth.middleware.rate_limiter.get_reset_time') as mock_reset:
                        from datetime import datetime, timedelta
                        mock_reset.return_value = datetime.utcnow() + timedelta(minutes=1)
                        
                        # Mock LLM service for successful processing
                        with patch('app.services.llm_service.llm_service') as mock_llm:
                            mock_llm.chunk_code.return_value = [Mock()]
                            mock_llm.analyze_code.return_value = Mock(
                                summary="Test summary",
                                issues=[],
                                recommendations=[],
                                confidence=0.9,
                                processing_time=1.0
                            )
                            
                            files = {
                                "file": ("test.py", sample_python_code, "text/plain")
                            }
                            
                            response = self.client.post(
                                "/api/review",
                                files=files,
                                headers={"Authorization": "Bearer basic-api-key"}
                            )
                            
                            # Should include rate limit headers even on success
                            assert "X-RateLimit-Limit" in response.headers
                            assert "X-RateLimit-Remaining" in response.headers
                            assert "X-RateLimit-Reset" in response.headers
    
    def test_different_rate_limits_by_tier(self, sample_python_code):
        """Test that different user tiers have different rate limits."""
        # Test basic user (5 requests/minute)
        with patch('app.auth.middleware.user_store.validate_api_key', return_value=self.basic_user):
            with patch('app.auth.middleware.rate_limiter.check_rate_limit', return_value=(True, 0, 5)):
                with patch('app.auth.middleware.rate_limiter.record_request'):
                    files = {
                        "file": ("test.py", sample_python_code, "text/plain")
                    }
                    
                    response = self.client.post(
                        "/api/review",
                        files=files,
                        headers={"Authorization": "Bearer basic-api-key"}
                    )
                    
                    assert response.headers.get("X-RateLimit-Limit") == "5"
        
        # Test premium user (50 requests/minute)
        with patch('app.auth.middleware.user_store.validate_api_key', return_value=self.premium_user):
            with patch('app.auth.middleware.rate_limiter.check_rate_limit', return_value=(True, 0, 50)):
                with patch('app.auth.middleware.rate_limiter.record_request'):
                    files = {
                        "file": ("test.py", sample_python_code, "text/plain")
                    }
                    
                    response = self.client.post(
                        "/api/review",
                        files=files,
                        headers={"Authorization": "Bearer premium-api-key"}
                    )
                    
                    assert response.headers.get("X-RateLimit-Limit") == "50"


class TestReportManagement:
    """Test report listing, retrieval, and deletion."""
    
    def setup_method(self):
        """Set up test environment."""
        self.client = TestClient(app)
        self.test_user = User(
            id="report-test-user",
            api_key="report-test-key",
            email="report@test.com",
            rate_limit_tier=RateLimitTier.STANDARD,
            created_at="2024-01-01T00:00:00Z",
            is_active=True
        )
    
    def test_list_reports_pagination(self):
        """Test report listing with pagination."""
        with patch('app.auth.middleware.user_store.validate_api_key', return_value=self.test_user):
            with patch('app.auth.middleware.rate_limiter.check_rate_limit', return_value=(True, 0, 10)):
                with patch('app.auth.middleware.rate_limiter.record_request'):
                    response = self.client.get(
                        "/api/reviews?page=1&limit=5",
                        headers={"Authorization": "Bearer report-test-key"}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    
                    assert "reports" in data
                    assert "total" in data
                    assert "page" in data
                    assert "limit" in data
                    assert data["page"] == 1
                    assert data["limit"] == 5
    
    def test_list_reports_filtering(self):
        """Test report listing with filters."""
        with patch('app.auth.middleware.user_store.validate_api_key', return_value=self.test_user):
            with patch('app.auth.middleware.rate_limiter.check_rate_limit', return_value=(True, 0, 10)):
                with patch('app.auth.middleware.rate_limiter.record_request'):
                    response = self.client.get(
                        "/api/reviews?language=python&status=completed",
                        headers={"Authorization": "Bearer report-test-key"}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert "reports" in data
    
    def test_delete_report_success(self):
        """Test successful report deletion."""
        with patch('app.auth.middleware.user_store.validate_api_key', return_value=self.test_user):
            with patch('app.auth.middleware.rate_limiter.check_rate_limit', return_value=(True, 0, 10)):
                with patch('app.auth.middleware.rate_limiter.record_request'):
                    # Mock report manager
                    with patch('app.services.report_manager.get_report_manager') as mock_manager:
                        mock_report_manager = mock_manager.return_value
                        mock_report_manager.get_report.return_value = Mock(report_id="test-report-id")
                        mock_report_manager.delete_report.return_value = True
                        
                        response = self.client.delete(
                            "/api/review/test-report-id",
                            headers={"Authorization": "Bearer report-test-key"}
                        )
                        
                        assert response.status_code == 200
                        data = response.json()
                        assert data["success"] is True
                        assert "deleted successfully" in data["message"]
    
    def test_delete_nonexistent_report(self):
        """Test deletion of non-existent report."""
        with patch('app.auth.middleware.user_store.validate_api_key', return_value=self.test_user):
            with patch('app.auth.middleware.rate_limiter.check_rate_limit', return_value=(True, 0, 10)):
                with patch('app.auth.middleware.rate_limiter.record_request'):
                    with patch('app.services.report_manager.get_report_manager') as mock_manager:
                        mock_report_manager = mock_manager.return_value
                        mock_report_manager.get_report.return_value = None
                        
                        response = self.client.delete(
                            "/api/review/nonexistent-id",
                            headers={"Authorization": "Bearer report-test-key"}
                        )
                        
                        assert response.status_code == 404


class TestSystemEndpoints:
    """Test system health and limits endpoints."""
    
    def setup_method(self):
        """Set up test environment."""
        self.client = TestClient(app)
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_limits_endpoint(self):
        """Test system limits endpoint."""
        response = self.client.get("/api/limits")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "max_file_size_mb" in data
        assert "supported_languages" in data
        assert "supported_extensions" in data
        assert "rate_limits" in data
        
        # Verify structure
        assert isinstance(data["supported_languages"], list)
        assert isinstance(data["supported_extensions"], list)
        assert isinstance(data["rate_limits"], dict)
    
    def test_root_endpoint(self):
        """Test root API endpoint."""
        response = self.client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "version" in data
        assert "docs" in data
                    