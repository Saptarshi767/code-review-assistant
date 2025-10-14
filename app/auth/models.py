"""
Authentication models and data structures.
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class RateLimitTier(str, Enum):
    """Rate limit tiers for different user types."""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"


class User(BaseModel):
    """User model for authentication."""
    id: str
    api_key: str
    email: Optional[str] = None
    rate_limit_tier: RateLimitTier = RateLimitTier.STANDARD
    created_at: datetime
    is_active: bool = True
    metadata: Dict[str, Any] = {}


class ApiKeyRequest(BaseModel):
    """Request model for API key generation."""
    email: Optional[str] = None
    rate_limit_tier: RateLimitTier = RateLimitTier.STANDARD


class ApiKeyResponse(BaseModel):
    """Response model for API key generation."""
    api_key: str
    user_id: str
    rate_limit_tier: RateLimitTier
    created_at: datetime


class RateLimitInfo(BaseModel):
    """Rate limit information for a user."""
    requests_per_minute: int
    current_usage: int
    reset_time: datetime
    tier: RateLimitTier