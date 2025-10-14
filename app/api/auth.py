"""
Authentication API endpoints.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List

from app.auth.models import (
    User, ApiKeyRequest, ApiKeyResponse, RateLimitInfo, RateLimitTier
)
from app.auth.user_store import user_store
from app.auth.rate_limiter import rate_limiter
from app.auth.middleware import api_key_auth


router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/api-key", response_model=ApiKeyResponse)
async def create_api_key(request: ApiKeyRequest):
    """
    Create a new API key for a user.
    
    This is a simplified endpoint for MVP. In production, this would
    require proper user registration and verification.
    
    Args:
        request: API key creation request
        
    Returns:
        ApiKeyResponse with new API key and user information
    """
    try:
        user = user_store.create_user(
            email=request.email,
            rate_limit_tier=request.rate_limit_tier
        )
        
        return ApiKeyResponse(
            api_key=user.api_key,
            user_id=user.id,
            rate_limit_tier=user.rate_limit_tier,
            created_at=user.created_at
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Failed to create API key",
                "error": str(e)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Internal server error creating API key",
                "error": str(e)
            }
        )


@router.get("/me", response_model=User)
async def get_current_user(current_user: User = Depends(api_key_auth)):
    """
    Get information about the current authenticated user.
    
    Args:
        current_user: Current authenticated user from middleware
        
    Returns:
        User information
    """
    return current_user


@router.get("/rate-limit", response_model=RateLimitInfo)
async def get_rate_limit_info(current_user: User = Depends(api_key_auth)):
    """
    Get rate limit information for the current user.
    
    Args:
        current_user: Current authenticated user from middleware
        
    Returns:
        RateLimitInfo with current usage and limits
    """
    stats = rate_limiter.get_user_stats(current_user)
    reset_time = rate_limiter.get_reset_time()
    
    return RateLimitInfo(
        requests_per_minute=stats["limit"],
        current_usage=stats["current_count"],
        reset_time=reset_time,
        tier=current_user.rate_limit_tier
    )


@router.get("/users", response_model=List[User])
async def list_users(current_user: User = Depends(api_key_auth)):
    """
    List all users (admin endpoint).
    
    In production, this would require admin privileges.
    
    Args:
        current_user: Current authenticated user from middleware
        
    Returns:
        List of all users
    """
    # Simple admin check - in production, use proper role-based access
    if current_user.rate_limit_tier != RateLimitTier.PREMIUM:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Admin access required",
                "error": "Only premium users can access this endpoint"
            }
        )
    
    return user_store.list_users()


@router.post("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    current_user: User = Depends(api_key_auth)
):
    """
    Deactivate a user (admin endpoint).
    
    Args:
        user_id: ID of user to deactivate
        current_user: Current authenticated user from middleware
        
    Returns:
        Success message
    """
    # Simple admin check - in production, use proper role-based access
    if current_user.rate_limit_tier != RateLimitTier.PREMIUM:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Admin access required",
                "error": "Only premium users can access this endpoint"
            }
        )
    
    # Prevent self-deactivation
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Cannot deactivate yourself",
                "error": "Self-deactivation is not allowed"
            }
        )
    
    success = user_store.deactivate_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "User not found",
                "error": f"User {user_id} does not exist"
            }
        )
    
    return {
        "success": True,
        "message": f"User {user_id} deactivated successfully"
    }