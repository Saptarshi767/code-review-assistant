"""
Code Review Assistant API

A FastAPI-based service for automated code review using LLM integration.
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
import os
import logging
from dotenv import load_dotenv
from app.api.review import router as review_router
from app.api.auth import router as auth_router
from app.api.dashboard import router as dashboard_router
from app.api.monitoring import router as monitoring_router
from app.security.headers import create_security_headers_middleware
from app.middleware.error_middleware import ErrorHandlingMiddleware, RequestValidationMiddleware
from config import settings

# Load environment variables
load_dotenv()

# Setup logging
from app.utils.logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app instance
app = FastAPI(
    title="Code Review Assistant",
    description="Automated code analysis system with LLM integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Rate limit headers middleware
class RateLimitHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add rate limit headers if they were set by auth middleware
        if hasattr(request.state, 'rate_limit_headers'):
            for header, value in request.state.rate_limit_headers.items():
                response.headers[header] = value
        
        return response

# Add middleware in correct order (last added = first executed)
app.add_middleware(RateLimitHeadersMiddleware)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestValidationMiddleware)

# Add security headers middleware
security_middleware = create_security_headers_middleware(
    strict_csp=False,  # Allow inline scripts for development
    enable_hsts=False,  # Only enable for HTTPS in production
    custom_headers={
        "X-API-Version": "1.0.0"
    }
)
app.add_middleware(type(security_middleware), headers=security_middleware.security_headers)

# Mount static files for the new frontend
import os
from fastapi.responses import FileResponse

# Mount the new glassmorphism frontend assets
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# Serve CSS and JS files
@app.get("/styles.css")
async def get_styles():
    return FileResponse("styles.css", media_type="text/css")

@app.get("/app.js")
async def get_app_js():
    return FileResponse("app.js", media_type="application/javascript")

@app.get("/sw.js")
async def get_service_worker():
    return FileResponse("sw.js", media_type="application/javascript")

@app.get("/accessibility-test.js")
async def get_accessibility_test():
    return FileResponse("accessibility-test.js", media_type="application/javascript")

@app.get("/performance-test.js")
async def get_performance_test():
    return FileResponse("performance-test.js", media_type="application/javascript")

# Mount legacy static files if they exist
static_dir = os.path.join(os.path.dirname(__file__), "app", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include API routers
app.include_router(review_router)
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(monitoring_router)

# Configure CORS with security considerations
allowed_origins = settings.allowed_origins_list if settings.cors_enabled else []
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"]
)

@app.get("/")
async def root():
    """Serve the glassmorphism landing page."""
    return FileResponse("index.html", media_type="text/html")

@app.get("/api-info")
async def api_info():
    """API information endpoint."""
    return {
        "message": "Code Review Assistant API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/api/config")
async def get_config():
    """Get frontend configuration."""
    return {
        "gemini_api_key": settings.gemini_api_key,
        "llm_provider": settings.llm_provider,
        "gemini_model": settings.gemini_model
    }

# Health check is now handled by the monitoring router

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    # Check for TLS configuration
    from app.security.tls_config import tls_config
    ssl_config = tls_config.get_uvicorn_ssl_config()
    
    if ssl_config:
        print("Starting server with HTTPS/TLS enabled")
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=True,
            log_level="info",
            **ssl_config
        )
    else:
        print("Starting server with HTTP (no TLS configured)")
        print("For production, configure TLS_CERT_FILE and TLS_KEY_FILE environment variables")
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=True,
            log_level="info"
        )