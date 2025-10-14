"""
Authentication middleware for FastAPI.
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from app.auth.user_store import user_store
from app.auth.rate_limiter import rate_limiter
from app.auth.models import User


class APIKeyAuth(HTTPBearer):
    """
    Custom authentication class for API key validation.
    """
    
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> Optional[User]:
        """
        Validate API key from request headers.
        
        Supports both:
        - Authorization: Bearer <api_key>
        - X-API-Key: <api_key>
        """
        api_key = None
        
        # Try Authorization header first
        try:
            credentials: HTTPAuthorizationCredentials = await super().__call__(request)
            if credentials:
                api_key = credentials.credentials
        except HTTPException:
            # If Authorization header fails, try X-API-Key header
            api_key = request.headers.get("X-API-Key")
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "message": "API key required",
                    "error": "Missing API key in Authorization header or X-API-Key header"
                },
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Validate API key
        user = user_store.validate_api_key(api_key)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "message": "Invalid API key",
                    "error": "The provided API key is invalid or inactive"
                },
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Check rate limits
        is_allowed, current_count, limit = rate_limiter.check_rate_limit(user)
        if not is_allowed:
            reset_time = rate_limiter.get_reset_time()
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "message": "Rate limit exceeded",
                    "error": f"Too many requests. Limit: {limit} per minute",
                    "current_usage": current_count,
                    "limit": limit,
                    "reset_time": reset_time.isoformat()
                },
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": str(max(0, limit - current_count)),
                    "X-RateLimit-Reset": str(int(reset_time.timestamp()))
                }
            )
        
        # Record the request
        rate_limiter.record_request(user)
        
        # Add rate limit headers to response
        request.state.rate_limit_headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(max(0, limit - current_count - 1)),
            "X-RateLimit-Reset": str(int(rate_limiter.get_reset_time().timestamp()))
        }
        
        return user


# Global auth instance
api_key_auth = APIKeyAuth(auto_error=True)
optional_api_key_auth = APIKeyAuth(auto_error=False)