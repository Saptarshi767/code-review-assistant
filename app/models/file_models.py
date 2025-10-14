"""
Data models for file upload and validation.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from enum import Enum


class FileType(str, Enum):
    """Supported file types for code analysis."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"
    CPP = "cpp"
    C = "c"
    RUBY = "ruby"
    PHP = "php"
    ZIP = "zip"


class UploadResponse(BaseModel):
    """Response model for file upload endpoint."""
    report_id: str = Field(..., description="Unique identifier for the analysis report")
    status: str = Field(..., description="Current processing status")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    language: Optional[str] = Field(None, description="Detected programming language")
    estimated_time: Optional[int] = Field(None, description="Estimated processing time in seconds")


class ValidationError(BaseModel):
    """Model for file validation errors."""
    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")


class FileValidationResponse(BaseModel):
    """Response model for file validation."""
    valid: bool = Field(..., description="Whether the file passed validation")
    errors: List[ValidationError] = Field(default_factory=list, description="List of validation errors")
    file_size: int = Field(..., description="File size in bytes")
    detected_type: str = Field(..., description="Detected file type")
    language: Optional[str] = Field(None, description="Detected programming language")


class SupportedFormatsResponse(BaseModel):
    """Response model for supported file formats."""
    extensions: List[str] = Field(..., description="List of supported file extensions")
    max_file_size_mb: int = Field(..., description="Maximum file size in MB")
    languages: List[str] = Field(..., description="List of supported programming languages")