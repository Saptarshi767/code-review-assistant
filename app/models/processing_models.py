"""
Data models for file processing and content analysis.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class ExtractedFile(BaseModel):
    """Model for files extracted from archives."""
    path: str = Field(..., description="Original file path within archive")
    content: str = Field(..., description="File content as text")
    language: Optional[str] = Field(None, description="Detected programming language")
    size: int = Field(..., description="File size in bytes")


class RedactedSecret(BaseModel):
    """Model for detected and redacted secrets."""
    type: str = Field(..., description="Type of secret detected (api_key, password, etc.)")
    line_number: int = Field(..., description="Line number where secret was found")
    pattern: str = Field(..., description="Pattern that matched the secret")
    redacted_value: str = Field(..., description="Redacted version of the secret")


class SanitizedContent(BaseModel):
    """Model for sanitized file content."""
    content: str = Field(..., description="Sanitized content with secrets redacted")
    redacted_secrets: List[RedactedSecret] = Field(default_factory=list, description="List of redacted secrets")
    warnings: List[str] = Field(default_factory=list, description="Security warnings")


class ProcessedFile(BaseModel):
    """Model for fully processed file."""
    filename: str = Field(..., description="Original filename")
    language: Optional[str] = Field(None, description="Detected programming language")
    content: str = Field(..., description="File content")
    size: int = Field(..., description="File size in bytes")
    sanitized: SanitizedContent = Field(..., description="Sanitization results")
    extracted_files: List[ExtractedFile] = Field(default_factory=list, description="Files extracted from archive (if applicable)")