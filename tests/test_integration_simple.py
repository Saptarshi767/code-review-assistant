"""
Simplified integration tests focusing on core functionality.
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


class TestBasicIntegration:
    """Test basic integration functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.client = TestClient(app)
    
    def test_health_endpoint(self):
        """Test health check endpoint works."""
        response = self.client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_limits_endpoint(self):
        """Test system limits endpoint works."""
        response = self.client.get("/api/limits")
        assert response.status_code == 200
        data = response.json()
        
        assert "max_file_size_mb" in data
        assert "supported_languages" in data
        assert "supported_extensions" in data
        assert "rate_limits" in data
    
    def test_root_endpoint(self):
        """Test root API endpoint works."""
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "version" in data
        assert "docs" in data


class TestAuthenticationFlow:
    """Test authentication flow with real auth components."""
    
    def setup_method(self):
        """Set up test environment."""
        self.client = TestClient(app)
    
    def test_missing_api_key_returns_401(self):
        """Test that missing API key returns 401."""
        files = {
            "file": ("test.py", "print('hello')", "text/plain")
        }
        
        response = self.client.post("/api/review", files=files)
        assert response.status_code == 401
    
    def test_invalid_api_key_returns_401(self):
        """Test that invalid API key returns 401."""
        files = {
            "file": ("test.py", "print('hello')", "text/plain")
        }
        
        response = self.client.post(
            "/api/review",
            files=files,
            headers={"Authorization": "Bearer invalid-key"}
        )
        assert response.status_code == 401
    
    def test_valid_api_key_passes_auth(self):
        """Test that valid API key passes authentication."""
        files = {
            "file": ("test.py", "print('hello')", "text/plain")
        }
        
        # Use the default test API key from user store
        response = self.client.post(
            "/api/review",
            files=files,
            headers={"Authorization": "Bearer test-admin-key-12345"}
        )
        
        # Should not get 401 (will get other errors due to LLM service, but auth should pass)
        assert response.status_code != 401
    
    def test_x_api_key_header_works(self):
        """Test that X-API-Key header works for authentication."""
        files = {
            "file": ("test.py", "print('hello')", "text/plain")
        }
        
        response = self.client.post(
            "/api/review",
            files=files,
            headers={"X-API-Key": "test-admin-key-12345"}
        )
        
        # Should not get 401
        assert response.status_code != 401


class TestFileValidation:
    """Test file validation and error handling."""
    
    def setup_method(self):
        """Set up test environment."""
        self.client = TestClient(app)
    
    def test_file_too_large_error(self):
        """Test handling of files exceeding size limit."""
        # Create content larger than 10MB
        large_content = "x" * (11 * 1024 * 1024)
        
        files = {
            "file": ("large_file.py", large_content, "text/plain")
        }
        
        response = self.client.post(
            "/api/review",
            files=files,
            headers={"Authorization": "Bearer test-admin-key-12345"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
    
    def test_binary_file_rejection(self):
        """Test rejection of binary files."""
        # Create binary content (PNG header)
        binary_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        
        files = {
            "file": ("image.png", binary_content, "image/png")
        }
        
        response = self.client.post(
            "/api/review",
            files=files,
            headers={"Authorization": "Bearer test-admin-key-12345"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
    
    def test_malformed_request_error(self):
        """Test handling of malformed requests."""
        # Send request without file
        response = self.client.post(
            "/api/review",
            headers={"Authorization": "Bearer test-admin-key-12345"}
        )
        
        assert response.status_code == 422  # Validation error


class TestRateLimitingBasic:
    """Test basic rate limiting functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.client = TestClient(app)
    
    def test_rate_limit_headers_present(self):
        """Test that rate limit headers are present in responses."""
        files = {
            "file": ("test.py", "print('hello')", "text/plain")
        }
        
        response = self.client.post(
            "/api/review",
            files=files,
            headers={"Authorization": "Bearer test-admin-key-12345"}
        )
        
        # Check for rate limit headers (should be present even on errors)
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers


class TestReportEndpoints:
    """Test report management endpoints."""
    
    def setup_method(self):
        """Set up test environment."""
        self.client = TestClient(app)
    
    def test_list_reports_endpoint(self):
        """Test report listing endpoint."""
        response = self.client.get(
            "/api/reviews",
            headers={"Authorization": "Bearer test-admin-key-12345"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "reports" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
    
    def test_list_reports_with_pagination(self):
        """Test report listing with pagination parameters."""
        response = self.client.get(
            "/api/reviews?page=1&limit=5",
            headers={"Authorization": "Bearer test-admin-key-12345"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["page"] == 1
        assert data["limit"] == 5
    
    def test_get_nonexistent_report(self):
        """Test retrieval of non-existent report."""
        response = self.client.get(
            "/api/review/nonexistent-id",
            headers={"Authorization": "Bearer test-admin-key-12345"}
        )
        
        assert response.status_code == 404
    
    def test_delete_nonexistent_report(self):
        """Test deletion of non-existent report."""
        response = self.client.delete(
            "/api/review/nonexistent-id",
            headers={"Authorization": "Bearer test-admin-key-12345"}
        )
        
        assert response.status_code == 404


class TestCompleteWorkflowMocked:
    """Test complete workflow with mocked LLM service."""
    
    def setup_method(self):
        """Set up test environment."""
        self.client = TestClient(app)
    
    @patch('app.services.llm_service.llm_service')
    def test_successful_python_file_analysis(self, mock_llm):
        """Test successful analysis of Python file with mocked LLM."""
        # Mock LLM service responses
        mock_chunk = Mock()
        mock_chunk.content = "print('hello world')"
        mock_chunk.start_line = 1
        mock_chunk.end_line = 1
        mock_chunk.context = "Simple script"
        mock_chunk.language = "python"
        
        mock_llm.chunk_code.return_value = [mock_chunk]
        
        mock_analysis = Mock()
        mock_analysis.summary = "Simple Python script with no issues"
        mock_analysis.issues = []
        mock_analysis.recommendations = []
        mock_analysis.confidence = 0.9
        mock_analysis.processing_time = 1.0
        
        mock_llm.analyze_code.return_value = mock_analysis
        
        files = {
            "file": ("hello.py", "print('hello world')", "text/plain")
        }
        
        response = self.client.post(
            "/api/review",
            files=files,
            headers={"Authorization": "Bearer test-admin-key-12345"}
        )
        
        # Should succeed with mocked LLM
        assert response.status_code == 200
        data = response.json()
        
        assert "report_id" in data
        assert data["status"] == "completed"
        assert data["filename"] == "hello.py"
        assert data["language"] == "python"
        
        # Verify we can retrieve the report
        report_id = data["report_id"]
        get_response = self.client.get(
            f"/api/review/{report_id}",
            headers={"Authorization": "Bearer test-admin-key-12345"}
        )
        
        assert get_response.status_code == 200
        report_data = get_response.json()
        assert report_data["report_id"] == report_id
        assert report_data["status"] == "completed"
    
    @patch('app.services.llm_service.llm_service')
    def test_javascript_file_analysis(self, mock_llm):
        """Test analysis of JavaScript file."""
        mock_chunk = Mock()
        mock_chunk.content = "console.log('hello');"
        mock_chunk.start_line = 1
        mock_chunk.end_line = 1
        mock_chunk.context = "Simple script"
        mock_chunk.language = "javascript"
        
        mock_llm.chunk_code.return_value = [mock_chunk]
        
        mock_analysis = Mock()
        mock_analysis.summary = "Simple JavaScript with console.log"
        mock_analysis.issues = []
        mock_analysis.recommendations = []
        mock_analysis.confidence = 0.9
        mock_analysis.processing_time = 1.0
        
        mock_llm.analyze_code.return_value = mock_analysis
        
        files = {
            "file": ("script.js", "console.log('hello');", "text/plain")
        }
        
        response = self.client.post(
            "/api/review",
            files=files,
            headers={"Authorization": "Bearer test-admin-key-12345"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "javascript"
    
    @patch('app.services.llm_service.llm_service')
    def test_llm_service_error_handling(self, mock_llm):
        """Test handling of LLM service errors."""
        mock_llm.chunk_code.return_value = [Mock()]
        mock_llm.analyze_code.side_effect = Exception("LLM service unavailable")
        
        files = {
            "file": ("test.py", "print('hello')", "text/plain")
        }
        
        response = self.client.post(
            "/api/review",
            files=files,
            headers={"Authorization": "Bearer test-admin-key-12345"}
        )
        
        assert response.status_code == 500
        data = response.json()
        assert "error" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])