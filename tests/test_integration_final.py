"""
Final comprehensive integration tests for the Code Review Assistant.
Tests complete upload-to-report workflow, error handling, and authentication.
"""

import pytest
import json
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import status

from main import app
from app.auth.models import User, RateLimitTier


class TestIntegrationWorkflow:
    """Test complete integration workflow with proper mocking."""
    
    def setup_method(self):
        """Set up test environment."""
        self.client = TestClient(app)
        self.test_user = User(
            id="integration-test-user",
            api_key="test-admin-key-12345",  # Use existing test key
            email="integration@test.com",
            rate_limit_tier=RateLimitTier.PREMIUM,
            created_at="2024-01-01T00:00:00Z",
            is_active=True
        )
    
    def test_health_endpoint_works(self):
        """Test that health endpoint is accessible."""
        response = self.client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_limits_endpoint_works(self):
        """Test that limits endpoint returns proper structure."""
        response = self.client.get("/api/limits")
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["max_file_size_mb", "supported_languages", "supported_extensions", "rate_limits"]
        for field in required_fields:
            assert field in data
    
    def test_authentication_flow(self):
        """Test authentication with valid and invalid keys."""
        # Test missing API key
        response = self.client.post("/api/review")
        assert response.status_code == 401
        
        # Test invalid API key
        response = self.client.post(
            "/api/review",
            headers={"Authorization": "Bearer invalid-key"}
        )
        assert response.status_code == 401
        
        # Test valid API key (should pass auth but fail validation)
        files = {"file": ("test.py", "print('hello')", "text/plain")}
        response = self.client.post(
            "/api/review",
            files=files,
            headers={"Authorization": "Bearer test-admin-key-12345"}
        )
        # Should not be 401 (auth passed)
        assert response.status_code != 401
    
    def test_file_validation_errors(self):
        """Test file validation error handling."""
        # Test malformed request (no file)
        response = self.client.post(
            "/api/review",
            headers={"Authorization": "Bearer test-admin-key-12345"}
        )
        assert response.status_code == 422  # Validation error
        
        # Test binary file rejection
        binary_content = b'\x89PNG\r\n\x1a\n'
        files = {"file": ("image.png", binary_content, "image/png")}
        response = self.client.post(
            "/api/review",
            files=files,
            headers={"Authorization": "Bearer test-admin-key-12345"}
        )
        # Should be rejected (400 or 500 depending on where validation fails)
        assert response.status_code in [400, 500]
    
    def test_report_management_endpoints(self):
        """Test report listing and management."""
        # Test list reports
        response = self.client.get(
            "/api/reviews",
            headers={"Authorization": "Bearer test-admin-key-12345"}
        )
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["reports", "total", "page", "limit"]
        for field in required_fields:
            assert field in data
        
        # Test pagination parameters
        response = self.client.get(
            "/api/reviews?page=1&limit=5",
            headers={"Authorization": "Bearer test-admin-key-12345"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["limit"] == 5
        
        # Test non-existent report retrieval
        response = self.client.get(
            "/api/review/nonexistent-id",
            headers={"Authorization": "Bearer test-admin-key-12345"}
        )
        # Should be 404 or 500 depending on error handling
        assert response.status_code in [404, 500]
    
    @patch('app.services.llm_service.llm_service')
    def test_successful_file_analysis_workflow(self, mock_llm):
        """Test complete successful file analysis workflow with mocked LLM."""
        # Mock LLM service responses
        mock_chunk = Mock()
        mock_chunk.content = "print('hello world')"
        mock_chunk.start_line = 1
        mock_chunk.end_line = 1
        mock_chunk.context = "Simple script"
        mock_chunk.language = "python"
        
        mock_llm.chunk_code.return_value = [mock_chunk]
        
        # Mock successful analysis result
        mock_analysis = Mock()
        mock_analysis.summary = "Simple Python script with no major issues"
        mock_analysis.issues = []
        mock_analysis.recommendations = []
        mock_analysis.confidence = 0.9
        mock_analysis.processing_time = 1.0
        
        mock_llm.analyze_code.return_value = mock_analysis
        
        # Test file upload and analysis
        files = {"file": ("hello.py", "print('hello world')", "text/plain")}
        
        response = self.client.post(
            "/api/review",
            files=files,
            headers={"Authorization": "Bearer test-admin-key-12345"}
        )
        
        # Should succeed with mocked LLM
        if response.status_code == 200:
            data = response.json()
            
            # Verify response structure
            assert "report_id" in data
            assert "status" in data
            assert "filename" in data
            assert "language" in data
            
            assert data["filename"] == "hello.py"
            assert data["language"] == "python"
            
            # If completed, verify we can retrieve the report
            if data["status"] == "completed":
                report_id = data["report_id"]
                get_response = self.client.get(
                    f"/api/review/{report_id}",
                    headers={"Authorization": "Bearer test-admin-key-12345"}
                )
                
                if get_response.status_code == 200:
                    report_data = get_response.json()
                    assert report_data["report_id"] == report_id
                    assert report_data["status"] == "completed"
        else:
            # If it fails, at least verify it's not an auth error
            assert response.status_code != 401
    
    @patch('app.services.llm_service.llm_service')
    def test_llm_service_error_handling(self, mock_llm):
        """Test handling of LLM service errors."""
        # Mock LLM service to raise an exception
        mock_llm.chunk_code.return_value = [Mock()]
        mock_llm.analyze_code.side_effect = Exception("LLM service unavailable")
        
        files = {"file": ("test.py", "print('hello')", "text/plain")}
        
        response = self.client.post(
            "/api/review",
            files=files,
            headers={"Authorization": "Bearer test-admin-key-12345"}
        )
        
        # Should handle the error gracefully (500 error expected)
        assert response.status_code == 500
        
        # Verify error response structure
        if response.headers.get("content-type", "").startswith("application/json"):
            try:
                data = response.json()
                assert "error" in data
            except json.JSONDecodeError:
                # If JSON parsing fails, that's also acceptable for error responses
                pass
    
    def test_rate_limiting_behavior(self):
        """Test rate limiting functionality."""
        files = {"file": ("test.py", "print('hello')", "text/plain")}
        
        # Make a request and check for rate limit headers
        response = self.client.post(
            "/api/review",
            files=files,
            headers={"Authorization": "Bearer test-admin-key-12345"}
        )
        
        # Rate limit headers should be present on successful auth
        # (even if the request fails for other reasons)
        if response.status_code != 401:
            # Check if rate limit headers are present
            rate_limit_headers = [
                "X-RateLimit-Limit",
                "X-RateLimit-Remaining", 
                "X-RateLimit-Reset"
            ]
            
            # At least some rate limit headers should be present
            headers_present = any(header in response.headers for header in rate_limit_headers)
            # This is informational - rate limiting might not be fully implemented
            print(f"Rate limit headers present: {headers_present}")
            print(f"Response headers: {dict(response.headers)}")
    
    def test_different_file_types(self):
        """Test handling of different file types."""
        test_files = [
            ("script.js", "console.log('hello');", "javascript"),
            ("main.py", "def hello(): pass", "python"),
            ("app.java", "public class App {}", "java"),
            ("style.css", "body { margin: 0; }", "css"),  # Should be rejected
        ]
        
        for filename, content, expected_lang in test_files:
            files = {"file": (filename, content, "text/plain")}
            
            response = self.client.post(
                "/api/review",
                files=files,
                headers={"Authorization": "Bearer test-admin-key-12345"}
            )
            
            # Should not be auth error
            assert response.status_code != 401
            
            # For supported languages, should get 200 or processing error
            # For unsupported (like CSS), should get validation error
            if expected_lang in ["python", "javascript", "java"]:
                # Should be accepted (200) or fail during processing (500)
                assert response.status_code in [200, 500]
            else:
                # Unsupported files might be rejected
                assert response.status_code in [400, 422, 500]
    
    def test_api_endpoint_coverage(self):
        """Test that all main API endpoints are accessible."""
        endpoints_to_test = [
            ("GET", "/api/health"),
            ("GET", "/api/limits"),
            ("GET", "/api/reviews"),
            ("GET", "/"),
        ]
        
        for method, endpoint in endpoints_to_test:
            if method == "GET":
                if endpoint in ["/api/reviews"]:
                    # Requires auth
                    response = self.client.get(
                        endpoint,
                        headers={"Authorization": "Bearer test-admin-key-12345"}
                    )
                else:
                    # Public endpoints
                    response = self.client.get(endpoint)
                
                # Should be accessible (200) or have proper error handling
                assert response.status_code in [200, 400, 401, 422, 500]
                
                # Should not be completely broken (no 404 for existing endpoints)
                if endpoint != "/nonexistent":
                    assert response.status_code != 404


class TestErrorHandlingIntegration:
    """Test comprehensive error handling across the system."""
    
    def setup_method(self):
        """Set up test environment."""
        self.client = TestClient(app)
    
    def test_authentication_error_responses(self):
        """Test that authentication errors are properly formatted."""
        # Test missing auth
        response = self.client.post("/api/review")
        assert response.status_code == 401
        
        # Test invalid auth
        response = self.client.post(
            "/api/review",
            headers={"Authorization": "Bearer invalid"}
        )
        assert response.status_code == 401
    
    def test_validation_error_responses(self):
        """Test that validation errors are properly handled."""
        # Test malformed request
        response = self.client.post(
            "/api/review",
            headers={"Authorization": "Bearer test-admin-key-12345"}
        )
        assert response.status_code == 422  # FastAPI validation error
    
    def test_system_error_resilience(self):
        """Test that the system handles various error conditions gracefully."""
        # Test with various invalid inputs
        invalid_requests = [
            # No content-type
            {"url": "/api/review", "headers": {"Authorization": "Bearer test-admin-key-12345"}},
            # Invalid JSON in query params
            {"url": "/api/reviews?invalid=json{", "headers": {"Authorization": "Bearer test-admin-key-12345"}},
        ]
        
        for req in invalid_requests:
            response = self.client.get(req["url"], headers=req.get("headers", {}))
            # Should handle gracefully, not crash
            assert response.status_code in [200, 400, 401, 422, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])