"""
File processing and validation service.
"""

import os
import uuid
import mimetypes
import zipfile
import re
import io
from typing import List, Tuple, Optional, Dict
from fastapi import UploadFile, HTTPException
from config import settings
from app.models.file_models import FileValidationResponse, ValidationError, FileType
from app.models.processing_models import ExtractedFile, RedactedSecret, SanitizedContent, ProcessedFile
from app.security.secret_detector import secret_detector


class FileService:
    """Service for handling file uploads and validation."""
    
    # Mapping of file extensions to programming languages
    EXTENSION_TO_LANGUAGE = {
        '.py': 'python',
        '.js': 'javascript', 
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.go': 'go',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.c': 'c',
        '.rb': 'ruby',
        '.php': 'php',
        '.zip': 'zip'
    }
    
    # Patterns for detecting secrets and sensitive information
    SECRET_PATTERNS = {
        'api_key': [
            r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?',
            r'(?i)(secret[_-]?key|secretkey)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?',
        ],
        'password': [
            r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']?([^\s"\']{8,})["\']?',
        ],
        'token': [
            r'(?i)(token|auth[_-]?token)\s*[:=]\s*["\']?([a-zA-Z0-9_\-\.]{20,})["\']?',
            r'(?i)(bearer[_-]?token)\s*[:=]\s*["\']?([a-zA-Z0-9_\-\.]{20,})["\']?',
        ],
        'database_url': [
            r'(?i)(database[_-]?url|db[_-]?url)\s*[:=]\s*["\']?((?:mysql|postgresql|mongodb)://[^\s"\']+)["\']?',
        ],
        'private_key': [
            r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----',
            r'-----BEGIN\s+OPENSSH\s+PRIVATE\s+KEY-----',
        ]
    }
    
    def __init__(self):
        """Initialize the file service."""
        self.max_file_size = settings.max_file_size_mb * 1024 * 1024  # Convert MB to bytes
        self.supported_extensions = settings.supported_extensions
        self.upload_dir = settings.upload_dir
        
        # Ensure upload directory exists
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def validate_file(self, file: UploadFile) -> FileValidationResponse:
        """
        Validate uploaded file against size and type constraints.
        
        Args:
            file: The uploaded file to validate
            
        Returns:
            FileValidationResponse with validation results
        """
        errors = []
        
        # Read file content to get actual size
        content = await file.read()
        file_size = len(content)
        
        # Reset file pointer for later use
        await file.seek(0)
        
        # Validate file size
        if file_size > self.max_file_size:
            errors.append(ValidationError(
                field="file_size",
                message=f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds maximum allowed size ({settings.max_file_size_mb}MB)",
                code="FILE_TOO_LARGE"
            ))
        
        # Validate file extension
        file_ext = self._get_file_extension(file.filename)
        if file_ext not in self.supported_extensions:
            errors.append(ValidationError(
                field="file_type",
                message=f"File type '{file_ext}' is not supported. Supported types: {', '.join(self.supported_extensions)}",
                code="UNSUPPORTED_FORMAT"
            ))
        
        # Detect programming language
        language = self._detect_language(file.filename, content)
        
        # Check for binary content (basic check)
        if self._is_binary_content(content) and file_ext != '.zip':
            errors.append(ValidationError(
                field="content_type",
                message="Binary files are not supported for code analysis",
                code="BINARY_CONTENT"
            ))
        
        return FileValidationResponse(
            valid=len(errors) == 0,
            errors=errors,
            file_size=file_size,
            detected_type=file_ext,
            language=language
        )
    
    async def save_uploaded_file(self, file: UploadFile) -> Tuple[str, str]:
        """
        Save uploaded file to disk and return file path and unique ID.
        
        Args:
            file: The uploaded file to save
            
        Returns:
            Tuple of (file_id, file_path)
        """
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Create safe filename
        file_ext = self._get_file_extension(file.filename)
        safe_filename = f"{file_id}{file_ext}"
        file_path = os.path.join(self.upload_dir, safe_filename)
        
        # Save file content
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)
        
        return file_id, file_path
    
    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension from filename."""
        if not filename:
            return ""
        return os.path.splitext(filename.lower())[1]
    
    def _detect_language(self, filename: str, content: bytes) -> Optional[str]:
        """
        Detect programming language from filename and content.
        
        Args:
            filename: Original filename
            content: File content as bytes
            
        Returns:
            Detected language or None
        """
        file_ext = self._get_file_extension(filename)
        return self.EXTENSION_TO_LANGUAGE.get(file_ext)
    
    def _is_binary_content(self, content: bytes) -> bool:
        """
        Check if content appears to be binary.
        
        Args:
            content: File content as bytes
            
        Returns:
            True if content appears to be binary
        """
        # Simple heuristic: check for null bytes in first 1024 bytes
        sample = content[:1024]
        return b'\x00' in sample
    
    async def process_file(self, file: UploadFile) -> ProcessedFile:
        """
        Process uploaded file including content reading, language detection, and sanitization.
        
        Args:
            file: The uploaded file to process
            
        Returns:
            ProcessedFile with all processing results
        """
        # Read file content
        content = await file.read()
        
        # Handle zip files
        extracted_files = []
        if file.filename.lower().endswith('.zip'):
            extracted_files = await self._extract_zip_files(content)
            # For zip files, use the first extracted file as main content
            if extracted_files:
                main_content = extracted_files[0].content
                main_language = extracted_files[0].language
            else:
                main_content = ""
                main_language = None
        else:
            # Regular file processing
            try:
                main_content = content.decode('utf-8')
            except UnicodeDecodeError:
                # Try other common encodings
                for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        main_content = content.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise HTTPException(
                        status_code=400,
                        detail="Unable to decode file content. Please ensure the file is text-based."
                    )
            
            main_language = self._detect_language(file.filename, content)
        
        # Sanitize content
        sanitized = self._sanitize_content(main_content)
        
        return ProcessedFile(
            filename=file.filename,
            language=main_language,
            content=main_content,
            size=len(content),
            sanitized=sanitized,
            extracted_files=extracted_files
        )
    
    async def _extract_zip_files(self, zip_content: bytes) -> List[ExtractedFile]:
        """
        Extract source code files from zip archive.
        
        Args:
            zip_content: Zip file content as bytes
            
        Returns:
            List of extracted source code files
        """
        extracted_files = []
        
        try:
            with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_file:
                for file_info in zip_file.filelist:
                    # Skip directories and hidden files
                    if file_info.is_dir() or file_info.filename.startswith('.'):
                        continue
                    
                    # Check if file has supported extension
                    file_ext = self._get_file_extension(file_info.filename)
                    if file_ext not in self.supported_extensions or file_ext == '.zip':
                        continue
                    
                    # Skip files that are too large
                    if file_info.file_size > self.max_file_size:
                        continue
                    
                    try:
                        # Extract and decode file content
                        file_content = zip_file.read(file_info.filename)
                        
                        # Try to decode as text
                        try:
                            text_content = file_content.decode('utf-8')
                        except UnicodeDecodeError:
                            # Try other encodings
                            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                                try:
                                    text_content = file_content.decode(encoding)
                                    break
                                except UnicodeDecodeError:
                                    continue
                            else:
                                # Skip binary files
                                continue
                        
                        # Detect language
                        language = self._detect_language(file_info.filename, file_content)
                        
                        extracted_files.append(ExtractedFile(
                            path=file_info.filename,
                            content=text_content,
                            language=language,
                            size=file_info.file_size
                        ))
                        
                    except Exception as e:
                        # Skip files that can't be processed
                        continue
                        
        except zipfile.BadZipFile:
            raise HTTPException(
                status_code=400,
                detail="Invalid zip file format"
            )
        
        return extracted_files
    
    def _sanitize_content(self, content: str) -> SanitizedContent:
        """
        Sanitize content by detecting and redacting secrets/sensitive information.
        
        Args:
            content: File content to sanitize
            
        Returns:
            SanitizedContent with redacted secrets and warnings
        """
        # Use the enhanced secret detector
        sanitized_content, detected_secrets = secret_detector.scan_and_redact(content)
        
        # Convert detected secrets to our model format
        redacted_secrets = []
        warnings = []
        
        for secret in detected_secrets:
            redacted_secrets.append(RedactedSecret(
                type=secret.type,
                line_number=secret.line_number,
                pattern=f"Confidence: {secret.confidence}",
                redacted_value=secret.redacted_value
            ))
            
            warnings.append(
                f"Detected {secret.type} on line {secret.line_number} "
                f"(confidence: {secret.confidence:.2f})"
            )
        
        return SanitizedContent(
            content=sanitized_content,
            redacted_secrets=redacted_secrets,
            warnings=warnings
        )
    
    def get_supported_formats(self) -> dict:
        """
        Get information about supported file formats.
        
        Returns:
            Dictionary with supported formats information
        """
        return {
            "extensions": self.supported_extensions,
            "max_file_size_mb": settings.max_file_size_mb,
            "languages": list(set(self.EXTENSION_TO_LANGUAGE.values()))
        }


# Global file service instance
file_service = FileService()