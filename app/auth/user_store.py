"""
Simple in-memory user store for MVP authentication.
"""

import uuid
import hashlib
import secrets
from datetime import datetime
from typing import Dict, Optional, List
from threading import Lock

from app.auth.models import User, RateLimitTier
from config import settings


class InMemoryUserStore:
    """
    Simple in-memory user store for MVP.
    In production, this should be replaced with a proper database.
    """
    
    def __init__(self):
        self._users: Dict[str, User] = {}
        self._api_key_to_user_id: Dict[str, str] = {}
        self._lock = Lock()
        
        # Create a default admin user for testing
        self._create_default_users()
    
    def _create_default_users(self):
        """Create default users for testing purposes."""
        # Create admin user with a known API key for testing
        admin_api_key = "test-admin-key-12345"
        admin_user = self.create_user(
            api_key=admin_api_key,
            email="admin@example.com",
            rate_limit_tier=RateLimitTier.PREMIUM
        )
        
        # Create standard user for testing
        standard_api_key = "test-standard-key-67890"
        standard_user = self.create_user(
            api_key=standard_api_key,
            email="user@example.com",
            rate_limit_tier=RateLimitTier.STANDARD
        )
    
    def generate_api_key(self) -> str:
        """Generate a secure API key."""
        # Generate a random token
        token = secrets.token_urlsafe(32)
        
        # Add a prefix for identification
        api_key = f"cra_{token}"
        
        return api_key
    
    def create_user(
        self, 
        email: Optional[str] = None,
        rate_limit_tier: RateLimitTier = RateLimitTier.STANDARD,
        api_key: Optional[str] = None
    ) -> User:
        """Create a new user with an API key."""
        with self._lock:
            user_id = str(uuid.uuid4())
            
            # Generate API key if not provided
            if api_key is None:
                api_key = self.generate_api_key()
            
            # Ensure API key is unique
            if api_key in self._api_key_to_user_id:
                raise ValueError("API key already exists")
            
            user = User(
                id=user_id,
                api_key=api_key,
                email=email,
                rate_limit_tier=rate_limit_tier,
                created_at=datetime.utcnow(),
                is_active=True
            )
            
            self._users[user_id] = user
            self._api_key_to_user_id[api_key] = user_id
            
            return user
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self._users.get(user_id)
    
    def get_user_by_api_key(self, api_key: str) -> Optional[User]:
        """Get user by API key."""
        user_id = self._api_key_to_user_id.get(api_key)
        if user_id:
            return self._users.get(user_id)
        return None
    
    def validate_api_key(self, api_key: str) -> Optional[User]:
        """Validate API key and return user if valid."""
        user = self.get_user_by_api_key(api_key)
        if user and user.is_active:
            return user
        return None
    
    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user."""
        with self._lock:
            user = self._users.get(user_id)
            if user:
                user.is_active = False
                return True
            return False
    
    def list_users(self) -> List[User]:
        """List all users (for admin purposes)."""
        return list(self._users.values())
    
    def get_rate_limit_for_tier(self, tier: RateLimitTier) -> int:
        """Get rate limit for a specific tier."""
        rate_limits = {
            RateLimitTier.BASIC: 5,
            RateLimitTier.STANDARD: 10,
            RateLimitTier.PREMIUM: 50
        }
        return rate_limits.get(tier, 10)


# Global user store instance
user_store = InMemoryUserStore()