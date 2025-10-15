"""
Configuration settings for the Code Review Assistant API.
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # LLM Configuration
    llm_provider: str = "gemini"  # "openai" or "gemini"
    
    # OpenAI Configuration
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    openai_max_tokens: int = 4000
    
    # Gemini Configuration
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    gemini_max_tokens: int = 4000
    
    # Authentication
    jwt_secret_key: str = "your-secret-key-change-in-production"
    api_key_salt: str = "your-salt-change-in-production"
    
    # File Upload Configuration
    max_file_size_mb: int = 10
    upload_dir: str = "./uploads"
    reports_dir: str = "./reports"
    
    # Supported file extensions
    supported_extensions: List[str] = [
        ".py", ".js", ".java", ".ts", ".go", 
        ".cpp", ".c", ".rb", ".php", ".zip"
    ]
    
    # Rate Limiting
    rate_limit_requests_per_minute: int = 10
    
    # Database Configuration
    database_url: str = "sqlite:///./code_review.db"
    
    # Security
    allowed_origins: str = "http://localhost:3000,http://localhost:8080"
    cors_enabled: bool = True
    disable_authentication: bool = False
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert comma-separated origins to list."""
        return [origin.strip() for origin in self.allowed_origins.split(',') if origin.strip()]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # In serverless environments like Vercel, use /tmp for writable storage
        if os.environ.get('VERCEL'):
            self.upload_dir = "/tmp/uploads"
            self.reports_dir = "/tmp/reports"
        
        # Create directories if they don't exist (only if writable)
        try:
            os.makedirs(self.upload_dir, exist_ok=True)
            os.makedirs(self.reports_dir, exist_ok=True)
        except OSError:
            # In read-only environments, directories will be created on-demand
            pass


# Global settings instance
settings = Settings()