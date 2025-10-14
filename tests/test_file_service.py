"""
Unit tests for file service functionality.
Tests file validation, processing, and sanitization logic.
"""

import pytest
import tempfile
import os
from unittest.mock import patch, Mock
from fastapi import UploadFile
import io

from app.services.file_service import FileService, file_service
from app.models.file_models import ValidationError
from app.models.processing_models import ExtractedFile, RedactedSecret


class TestFileService:
    """Test cases for FileService class."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.file_service = FileService()
    
    @pytest.mark.asyncio
    async def test_validate_file_success(self, create_upload_file, sample_python_code):
        """Test successful file validation."""
        upload_file = create_upload_file(sample_python_code, "test.py")
        
        result = await self.file_service.validate_file(upload_file)
        
        assert result.valid is True
        assert len(result.errors) == 0
        assert result.detected_type == ".py"
        assert result.language == "python"
        assert result.file_size > 0
    
    @pytest.mark.asyncio
    async def test_validate_file_too_large(self, create_upload_file, large_file_content):
        """Test file validation with oversized file."""
        upload_file = create_upload_file(large_file_content, "large.py")
        
        result = await self.file_service.validate_file(upload_file)
        
        assert result.valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "FILE_TOO_LARGE"
        assert "exceeds maximum allowed size" in result.errors[0].message
    
    @pytest.mark.asyncio
    async def test_validate_file_unsupported_format(self, create_upload_file):
        """Test file validation with unsupported file type."""
        upload_file = create_upload_file("some content", "test.txt")
        
        result = await self.file_service.validate_file(upload_file)
        
        assert result.valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "UNSUPPORTED_FORMAT"
        assert "not supported" in result.errors[0].message
    
    @pytest.mark.asyncio
    async def test_validate_file_binary_content(self, binary_file_content):
        """Test file validation with binary content."""
        file_obj = io.BytesIO(binary_file_content)
        upload_file = UploadFile(file=file_obj, filename="image.py")
        
        result = await self.file_service.validate_file(upload_file)
        
        assert result.valid is False
        assert any(error.code == "BINARY_CONTENT" for error in result.errors)
    
    @pytest.mark.asyncio
    async def test_save_uploaded_file(self, create_upload_file, sample_python_code, temp_upload_dir):
        """Test saving uploaded file to disk."""
        with patch.object(self.file_service, 'upload_dir', temp_upload_dir):
            upload_file = create_upload_file(sample_python_code, "test.py")
            
            file_id, file_path = await self.file_service.save_uploaded_file(upload_file)
            
            assert file_id is not None
            assert file_path.startswith(temp_upload_dir)
            assert file_path.endswith(".py")
            assert os.path.exists(file_path)
            
            # Verify file content
            with open(file_path, 'r') as f:
                content = f.read()
                assert content == sample_python_code
    
    def test_get_file_extension(self):
        """Test file extension extraction."""
        assert self.file_service._get_file_extension("test.py") == ".py"
        assert self.file_service._get_file_extension("script.js") == ".js"
        assert self.file_service._get_file_extension("Test.JAVA") == ".java"
        assert self.file_service._get_file_extension("noextension") == ""
        assert self.file_service._get_file_extension("") == ""
    
    def test_detect_language(self):
        """Test programming language detection."""
        content = b"print('hello')"
        
        assert self.file_service._detect_language("test.py", content) == "python"
        assert self.file_service._detect_language("script.js", content) == "javascript"
        assert self.file_service._detect_language("Main.java", content) == "java"
        assert self.file_service._detect_language("unknown.xyz", content) is None
    
    def test_is_binary_content(self):
        """Test binary content detection."""
        text_content = b"def hello(): print('world')"
        binary_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\r'
        
        assert self.file_service._is_binary_content(text_content) is False
        assert self.file_service._is_binary_content(binary_content) is True
    
    @pytest.mark.asyncio
    async def test_process_file_python(self, create_upload_file, sample_python_code):
        """Test processing a Python file."""
        upload_file = create_upload_file(sample_python_code, "test.py")
        
        result = await self.file_service.process_file(upload_file)
        
        assert result.filename == "test.py"
        assert result.language == "python"
        assert result.content == sample_python_code
        assert result.size > 0
        assert result.sanitized is not None
        assert len(result.extracted_files) == 0  # Not a zip file
    
    @pytest.mark.asyncio
    async def test_process_file_javascript(self, create_upload_file, sample_javascript_code):
        """Test processing a JavaScript file."""
        upload_file = create_upload_file(sample_javascript_code, "script.js")
        
        result = await self.file_service.process_file(upload_file)
        
        assert result.filename == "script.js"
        assert result.language == "javascript"
        assert result.content == sample_javascript_code
        assert result.sanitized is not None
    
    @pytest.mark.asyncio
    async def test_extract_zip_files(self, zip_file_content):
        """Test extracting files from zip archive."""
        extracted = await self.file_service._extract_zip_files(zip_file_content)
        
        assert len(extracted) == 2
        
        # Check Python file
        py_file = next((f for f in extracted if f.path == "main.py"), None)
        assert py_file is not None
        assert py_file.language == "python"
        assert "hello_world" in py_file.content
        
        # Check JavaScript file
        js_file = next((f for f in extracted if f.path == "script.js"), None)
        assert js_file is not None
        assert js_file.language == "javascript"
        assert "greet" in js_file.content
    
    def test_sanitize_content_with_secrets(self, sample_python_code):
        """Test content sanitization with secret detection."""
        result = self.file_service._sanitize_content(sample_python_code)
        
        assert result.content is not None
        assert len(result.redacted_secrets) > 0
        assert len(result.warnings) > 0
        
        # Check that API key was detected
        api_key_detected = any(
            secret.type == "api_key" for secret in result.redacted_secrets
        )
        assert api_key_detected
    
    def test_sanitize_content_clean_code(self):
        """Test content sanitization with clean code (no secrets)."""
        clean_code = '''
def add_numbers(a, b):
    return a + b

def main():
    result = add_numbers(5, 3)
    print(f"Result: {result}")
'''
        
        result = self.file_service._sanitize_content(clean_code)
        
        assert result.content == clean_code
        assert len(result.redacted_secrets) == 0
        assert len(result.warnings) == 0
    
    def test_get_supported_formats(self):
        """Test getting supported formats information."""
        formats = self.file_service.get_supported_formats()
        
        assert "extensions" in formats
        assert "max_file_size_mb" in formats
        assert "languages" in formats
        
        assert ".py" in formats["extensions"]
        assert ".js" in formats["extensions"]
        assert "python" in formats["languages"]
        assert "javascript" in formats["languages"]


class TestFileServiceEdgeCases:
    """Test edge cases and error conditions for FileService."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.file_service = FileService()
    
    @pytest.mark.asyncio
    async def test_process_file_encoding_error(self):
        """Test processing file with encoding issues."""
        # Create file with invalid UTF-8 content
        invalid_content = b'\xff\xfe\x00\x00invalid utf-8'
        file_obj = io.BytesIO(invalid_content)
        upload_file = UploadFile(file=file_obj, filename="test.py")
        
        # Should handle encoding gracefully
        result = await self.file_service.process_file(upload_file)
        
        assert result.filename == "test.py"
        assert result.content is not None  # Should decode with fallback encoding
    
    @pytest.mark.asyncio
    async def test_extract_zip_files_invalid_zip(self):
        """Test extracting from invalid zip content."""
        invalid_zip = b"not a zip file"
        
        with pytest.raises(Exception):  # Should raise HTTPException
            await self.file_service._extract_zip_files(invalid_zip)
    
    @pytest.mark.asyncio
    async def test_extract_zip_files_empty_zip(self):
        """Test extracting from empty zip file."""
        import zipfile
        import io
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w'):
            pass  # Create empty zip
        
        zip_buffer.seek(0)
        extracted = await self.file_service._extract_zip_files(zip_buffer.getvalue())
        
        assert len(extracted) == 0
    
    @pytest.mark.asyncio
    async def test_validate_file_no_filename(self):
        """Test file validation with missing filename."""
        file_obj = io.BytesIO(b"content")
        upload_file = UploadFile(file=file_obj, filename=None)
        
        result = await self.file_service.validate_file(upload_file)
        
        # Should handle missing filename gracefully
        assert result.detected_type == ""
        assert result.language is None
    
    def test_secret_patterns_coverage(self):
        """Test that secret patterns detect various types of secrets."""
        test_content = '''
API_KEY = "sk-1234567890abcdef"
password = "mySecretPassword123"
auth_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
DATABASE_URL = "postgresql://user:pass@localhost/db"
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
-----END RSA PRIVATE KEY-----
'''
        
        result = self.file_service._sanitize_content(test_content)
        
        # Should detect multiple types of secrets
        assert len(result.redacted_secrets) > 0
        assert len(result.warnings) > 0
        
        # Content should be redacted
        assert "sk-1234567890abcdef" not in result.content
        assert "[REDACTED]" in result.content or "***" in result.content


# Integration test with global file service instance
class TestGlobalFileService:
    """Test the global file service instance."""
    
    @pytest.mark.asyncio
    async def test_global_file_service_instance(self, create_upload_file, sample_python_code):
        """Test that global file service instance works correctly."""
        upload_file = create_upload_file(sample_python_code, "test.py")
        
        result = await file_service.validate_file(upload_file)
        
        assert result.valid is True
        assert result.language == "python"
    
    def test_global_file_service_configuration(self):
        """Test that global file service is properly configured."""
        assert file_service.max_file_size > 0
        assert len(file_service.supported_extensions) > 0
        assert file_service.upload_dir is not None