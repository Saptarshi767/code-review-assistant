"""
Comprehensive error handling utilities for the Code Review Assistant.
"""

import uuid
import logging
import traceback
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, Optional, Union
from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ErrorType(str, Enum):
    """Standardized error types for consistent error handling."""
    
    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    UNSUPPORTED_FORMAT = "UNSUPPORTED_FORMAT"
    INVALID_REQUEST = "INVALID_REQUEST"
    
    # Authentication and authorization errors
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    AUTHORIZATION_FAILED = "AUTHORIZATION_FAILED"
    API_KEY_INVALID = "API_KEY_INVALID"
    
    # Rate limiting errors
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"
    
    # Service errors
    LLM_SERVICE_ERROR = "LLM_SERVICE_ERROR"
    FILE_PROCESSING_ERROR = "FILE_PROCESSING_ERROR"
    STORAGE_ERROR = "STORAGE_ERROR"
    
    # System errors
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    
    # Resource errors
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    RESOURCE_GONE = "RESOURCE_GONE"


class ErrorDetail(BaseModel):
    """Detailed error information."""
    field: Optional[str] = None
    code: Optional[str] = None
    message: str
    value: Optional[Any] = None


class StandardErrorResponse(BaseModel):
    """Enhanced standard error response format."""
    error: ErrorType
    message: str
    details: Optional[Dict[str, Any]] = None
    errors: Optional[list[ErrorDetail]] = None
    request_id: str
    timestamp: datetime
    path: Optional[str] = None
    method: Optional[str] = None
    retry_after: Optional[int] = None
    
    class Config:
        use_enum_values = True


class CodeReviewException(Exception):
    """Base exception class for Code Review Assistant specific errors."""
    
    def __init__(
        self,
        error_type: ErrorType,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500,
        retry_after: Optional[int] = None
    ):
        self.error_type = error_type
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        self.retry_after = retry_after
        super().__init__(message)


class ValidationException(CodeReviewException):
    """Exception for validation errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            error_type=ErrorType.VALIDATION_ERROR,
            message=message,
            details=details,
            status_code=400
        )


class AuthenticationException(CodeReviewException):
    """Exception for authentication errors."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            error_type=ErrorType.AUTHENTICATION_FAILED,
            message=message,
            status_code=401
        )


class AuthorizationException(CodeReviewException):
    """Exception for authorization errors."""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            error_type=ErrorType.AUTHORIZATION_FAILED,
            message=message,
            status_code=403
        )


class RateLimitException(CodeReviewException):
    """Exception for rate limiting errors."""
    
    def __init__(self, message: str, retry_after: int):
        super().__init__(
            error_type=ErrorType.RATE_LIMIT_EXCEEDED,
            message=message,
            status_code=429,
            retry_after=retry_after
        )


class ResourceNotFoundException(CodeReviewException):
    """Exception for resource not found errors."""
    
    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} '{resource_id}' not found"
        super().__init__(
            error_type=ErrorType.RESOURCE_NOT_FOUND,
            message=message,
            details={"resource_type": resource_type, "resource_id": resource_id},
            status_code=404
        )


class ServiceUnavailableException(CodeReviewException):
    """Exception for service unavailable errors."""
    
    def __init__(self, service_name: str, retry_after: Optional[int] = None):
        message = f"Service '{service_name}' is currently unavailable"
        super().__init__(
            error_type=ErrorType.SERVICE_UNAVAILABLE,
            message=message,
            details={"service": service_name},
            status_code=503,
            retry_after=retry_after
        )


class ErrorHandler:
    """Centralized error handling utility."""
    
    @staticmethod
    def generate_request_id() -> str:
        """Generate a unique request ID for error tracking."""
        return str(uuid.uuid4())
    
    @staticmethod
    def create_error_response(
        request: Request,
        error_type: ErrorType,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        errors: Optional[list[ErrorDetail]] = None,
        retry_after: Optional[int] = None,
        request_id: Optional[str] = None
    ) -> JSONResponse:
        """Create a standardized error response."""
        
        if not request_id:
            request_id = ErrorHandler.generate_request_id()
        
        error_response = StandardErrorResponse(
            error=error_type,
            message=message,
            details=details,
            errors=errors,
            request_id=request_id,
            timestamp=datetime.now(timezone.utc),
            path=str(request.url.path),
            method=request.method,
            retry_after=retry_after
        )
        
        # Log the error
        logger.error(
            f"Error {error_type}: {message}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "status_code": status_code,
                "details": details
            }
        )
        
        headers = {}
        if retry_after:
            headers["Retry-After"] = str(retry_after)
        
        return JSONResponse(
            status_code=status_code,
            content=error_response.model_dump(mode='json'),
            headers=headers
        )
    
    @staticmethod
    def handle_code_review_exception(
        request: Request,
        exc: CodeReviewException,
        request_id: Optional[str] = None
    ) -> JSONResponse:
        """Handle CodeReviewException instances."""
        
        return ErrorHandler.create_error_response(
            request=request,
            error_type=exc.error_type,
            message=exc.message,
            status_code=exc.status_code,
            details=exc.details,
            retry_after=exc.retry_after,
            request_id=request_id
        )
    
    @staticmethod
    def handle_http_exception(
        request: Request,
        exc: HTTPException,
        request_id: Optional[str] = None
    ) -> JSONResponse:
        """Handle FastAPI HTTPException instances."""
        
        # Map HTTP status codes to error types
        error_type_mapping = {
            400: ErrorType.VALIDATION_ERROR,
            401: ErrorType.AUTHENTICATION_FAILED,
            403: ErrorType.AUTHORIZATION_FAILED,
            404: ErrorType.RESOURCE_NOT_FOUND,
            409: ErrorType.RESOURCE_CONFLICT,
            429: ErrorType.RATE_LIMIT_EXCEEDED,
            500: ErrorType.INTERNAL_SERVER_ERROR,
            503: ErrorType.SERVICE_UNAVAILABLE
        }
        
        error_type = error_type_mapping.get(exc.status_code, ErrorType.INTERNAL_SERVER_ERROR)
        
        # Extract details from HTTPException detail
        details = None
        message = str(exc.detail)
        
        if isinstance(exc.detail, dict):
            message = exc.detail.get("message", str(exc.detail))
            details = {k: v for k, v in exc.detail.items() if k != "message"}
        
        return ErrorHandler.create_error_response(
            request=request,
            error_type=error_type,
            message=message,
            status_code=exc.status_code,
            details=details if details else None,
            request_id=request_id
        )
    
    @staticmethod
    def handle_unexpected_exception(
        request: Request,
        exc: Exception,
        request_id: Optional[str] = None
    ) -> JSONResponse:
        """Handle unexpected exceptions."""
        
        # Log the full traceback for debugging
        logger.error(
            f"Unexpected error: {str(exc)}",
            extra={
                "request_id": request_id or ErrorHandler.generate_request_id(),
                "path": request.url.path,
                "method": request.method,
                "traceback": traceback.format_exc()
            }
        )
        
        # Don't expose internal error details in production
        message = "An unexpected error occurred"
        details = {"error_type": type(exc).__name__}
        
        # In development, include more details
        import os
        if os.getenv("DEBUG", "false").lower() == "true":
            details["error_message"] = str(exc)
        
        return ErrorHandler.create_error_response(
            request=request,
            error_type=ErrorType.INTERNAL_SERVER_ERROR,
            message=message,
            status_code=500,
            details=details,
            request_id=request_id
        )


# Convenience functions for common error scenarios
def raise_validation_error(message: str, details: Optional[Dict[str, Any]] = None):
    """Raise a validation error."""
    raise ValidationException(message, details)


def raise_not_found(resource_type: str, resource_id: str):
    """Raise a resource not found error."""
    raise ResourceNotFoundException(resource_type, resource_id)


def raise_rate_limit_error(message: str, retry_after: int):
    """Raise a rate limit error."""
    raise RateLimitException(message, retry_after)


def raise_service_unavailable(service_name: str, retry_after: Optional[int] = None):
    """Raise a service unavailable error."""
    raise ServiceUnavailableException(service_name, retry_after)