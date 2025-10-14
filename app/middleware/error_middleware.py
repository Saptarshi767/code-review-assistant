"""
Error handling middleware for comprehensive error management.
"""

import time
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.utils.error_handler import (
    ErrorHandler, CodeReviewException, ErrorType
)
from app.utils.monitoring import request_logger


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for centralized error handling and logging."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with comprehensive error handling."""
        
        # Generate request ID for tracking
        request_id = ErrorHandler.generate_request_id()
        request.state.request_id = request_id
        
        # Log request start
        request_logger.log_request_start(request, request_id)
        
        start_time = time.time()
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate response time
            response_time_ms = (time.time() - start_time) * 1000
            
            # Log successful request completion
            request_logger.log_request_end(
                request, response, request_id, response_time_ms
            )
            
            # Add request ID to response headers for tracking
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except CodeReviewException as exc:
            # Handle our custom exceptions
            response_time_ms = (time.time() - start_time) * 1000
            
            error_response = ErrorHandler.handle_code_review_exception(
                request, exc, request_id
            )
            
            # Log error completion
            request_logger.log_request_end(
                request, error_response, request_id, response_time_ms, exc.error_type.value
            )
            
            # Add request ID to error response headers
            error_response.headers["X-Request-ID"] = request_id
            
            return error_response
            
        except StarletteHTTPException as exc:
            # Handle Starlette/FastAPI HTTP exceptions
            response_time_ms = (time.time() - start_time) * 1000
            
            error_response = ErrorHandler.handle_http_exception(
                request, exc, request_id
            )
            
            # Determine error type for logging
            error_type = None
            if hasattr(exc, 'detail') and isinstance(exc.detail, dict):
                error_type = exc.detail.get('error')
            
            # Log error completion
            request_logger.log_request_end(
                request, error_response, request_id, response_time_ms, error_type
            )
            
            # Add request ID to error response headers
            error_response.headers["X-Request-ID"] = request_id
            
            return error_response
            
        except Exception as exc:
            # Handle unexpected exceptions
            response_time_ms = (time.time() - start_time) * 1000
            
            error_response = ErrorHandler.handle_unexpected_exception(
                request, exc, request_id
            )
            
            # Log error completion
            request_logger.log_request_end(
                request, error_response, request_id, response_time_ms, ErrorType.INTERNAL_SERVER_ERROR.value
            )
            
            # Add request ID to error response headers
            error_response.headers["X-Request-ID"] = request_id
            
            return error_response


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for request validation and preprocessing."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Validate and preprocess requests."""
        
        try:
            # Check content length for file uploads
            content_length = request.headers.get("content-length")
            if content_length:
                content_length_int = int(content_length)
                max_size = 10 * 1024 * 1024  # 10MB in bytes
                
                if content_length_int > max_size:
                    from app.utils.error_handler import ValidationException
                    raise ValidationException(
                        "Request body too large",
                        details={
                            "max_size_mb": 10,
                            "actual_size_mb": round(content_length_int / (1024 * 1024), 2)
                        }
                    )
            
            # Check for required headers on certain endpoints
            if request.url.path.startswith("/api/") and request.method != "GET":
                if request.url.path not in ["/api/health", "/api/limits"]:
                    # Most API endpoints require authentication
                    auth_header = request.headers.get("authorization")
                    api_key_header = request.headers.get("x-api-key")
                    
                    if not auth_header and not api_key_header:
                        from app.utils.error_handler import AuthenticationException
                        raise AuthenticationException("Authentication required")
            
            return await call_next(request)
            
        except Exception:
            # Let the error handling middleware deal with exceptions
            raise