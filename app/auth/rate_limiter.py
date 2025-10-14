"""
Rate limiting implementation for API endpoints.
"""

import time
from typing import Dict, Tuple
from threading import Lock
from datetime import datetime, timedelta

from app.auth.models import User, RateLimitTier


class RateLimiter:
    """
    Simple in-memory rate limiter.
    Tracks requests per user per minute.
    """
    
    def __init__(self):
        # Structure: {user_id: {minute_timestamp: request_count}}
        self._request_counts: Dict[str, Dict[int, int]] = {}
        self._lock = Lock()
    
    def _get_current_minute(self) -> int:
        """Get current minute as timestamp."""
        return int(time.time() // 60)
    
    def _cleanup_old_entries(self, user_id: str, current_minute: int):
        """Remove entries older than 2 minutes to prevent memory leaks."""
        if user_id in self._request_counts:
            old_minutes = [
                minute for minute in self._request_counts[user_id].keys()
                if minute < current_minute - 1
            ]
            for minute in old_minutes:
                del self._request_counts[user_id][minute]
    
    def check_rate_limit(self, user: User) -> Tuple[bool, int, int]:
        """
        Check if user has exceeded rate limit.
        
        Args:
            user: User object with rate limit tier
            
        Returns:
            Tuple of (is_allowed, current_count, limit)
        """
        with self._lock:
            current_minute = self._get_current_minute()
            user_id = user.id
            
            # Initialize user tracking if needed
            if user_id not in self._request_counts:
                self._request_counts[user_id] = {}
            
            # Cleanup old entries
            self._cleanup_old_entries(user_id, current_minute)
            
            # Get current count for this minute
            current_count = self._request_counts[user_id].get(current_minute, 0)
            
            # Get rate limit for user's tier
            rate_limits = {
                RateLimitTier.BASIC: 5,
                RateLimitTier.STANDARD: 10,
                RateLimitTier.PREMIUM: 50
            }
            limit = rate_limits.get(user.rate_limit_tier, 10)
            
            # Check if limit exceeded
            is_allowed = current_count < limit
            
            return is_allowed, current_count, limit
    
    def record_request(self, user: User):
        """Record a request for the user."""
        with self._lock:
            current_minute = self._get_current_minute()
            user_id = user.id
            
            # Initialize user tracking if needed
            if user_id not in self._request_counts:
                self._request_counts[user_id] = {}
            
            # Increment count for current minute
            self._request_counts[user_id][current_minute] = (
                self._request_counts[user_id].get(current_minute, 0) + 1
            )
    
    def get_reset_time(self) -> datetime:
        """Get the time when rate limits reset (next minute)."""
        current_time = datetime.utcnow()
        next_minute = current_time.replace(second=0, microsecond=0) + timedelta(minutes=1)
        return next_minute
    
    def get_user_stats(self, user: User) -> Dict[str, int]:
        """Get current usage stats for a user."""
        with self._lock:
            current_minute = self._get_current_minute()
            user_id = user.id
            
            if user_id not in self._request_counts:
                return {"current_count": 0, "limit": 10}
            
            current_count = self._request_counts[user_id].get(current_minute, 0)
            
            rate_limits = {
                RateLimitTier.BASIC: 5,
                RateLimitTier.STANDARD: 10,
                RateLimitTier.PREMIUM: 50
            }
            limit = rate_limits.get(user.rate_limit_tier, 10)
            
            return {
                "current_count": current_count,
                "limit": limit
            }


# Global rate limiter instance
rate_limiter = RateLimiter()