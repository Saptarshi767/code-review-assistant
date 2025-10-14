"""
API endpoints for system monitoring and health checks.
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime, timezone

from app.models.api_models import HealthCheckResponse
from app.utils.monitoring import HealthChecker, metrics_collector
from app.auth.middleware import api_key_auth
from app.auth.models import User

router = APIRouter(prefix="/api", tags=["monitoring"])


@router.get("/health", response_model=HealthCheckResponse)
async def enhanced_health_check(
    include_metrics: bool = Query(False, description="Include system metrics in response"),
    include_services: bool = Query(True, description="Include service health details")
):
    """
    Enhanced health check endpoint with detailed system status.
    
    Provides comprehensive health information including:
    - Overall system status
    - Individual service health (LLM, storage, system resources)
    - Optional system metrics
    - Service availability and performance indicators
    
    Args:
        include_metrics: Whether to include detailed system metrics
        include_services: Whether to include detailed service health information
        
    Returns:
        HealthCheckResponse with system status and optional details
    """
    try:
        # Get overall health status
        health_data = HealthChecker.get_overall_health()
        
        # Prepare response data
        response_data = {
            "status": health_data["status"],
            "timestamp": datetime.fromisoformat(health_data["timestamp"].replace("Z", "+00:00")),
            "services": {},
            "version": health_data["version"]
        }
        
        if include_services:
            # Include detailed service information
            services = health_data["services"]
            response_data["services"] = {
                "llm": services["llm"]["status"],
                "storage": services["storage"]["status"],
                "system": services["system"]["status"]
            }
            
            # Add service details as additional fields
            response_data["service_details"] = services
        else:
            # Include basic service status only
            services = health_data["services"]
            response_data["services"] = {
                "llm": services["llm"]["status"],
                "storage": services["storage"]["status"],
                "system": services["system"]["status"]
            }
        
        if include_metrics:
            # Include system metrics
            response_data["metrics"] = health_data["metrics"]
        
        return HealthCheckResponse(**response_data)
        
    except Exception as e:
        # Return degraded status if health check itself fails
        return HealthCheckResponse(
            status="degraded",
            timestamp=datetime.now(timezone.utc),
            services={"health_check": "failed"},
            version="1.0.0"
        )


@router.get("/metrics")
async def get_system_metrics(
    current_user: User = Depends(api_key_auth),
    recent_errors: bool = Query(False, description="Include recent error details")
):
    """
    Get detailed system metrics and performance data.
    
    Requires authentication. Provides comprehensive metrics including:
    - Request statistics and performance
    - Error rates and types
    - Endpoint-specific metrics
    - System resource usage
    
    Args:
        recent_errors: Whether to include details of recent errors
        
    Returns:
        Detailed system metrics and performance data
    """
    try:
        # Get system metrics
        system_metrics = metrics_collector.get_system_metrics()
        
        # Prepare response
        metrics_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": system_metrics.uptime_seconds,
            "requests": {
                "total": system_metrics.total_requests,
                "successful": system_metrics.successful_requests,
                "failed": system_metrics.failed_requests,
                "per_minute": system_metrics.requests_per_minute,
                "avg_response_time_ms": system_metrics.avg_response_time_ms,
                "error_rate_percent": system_metrics.error_rate
            },
            "endpoints": system_metrics.endpoint_metrics,
            "errors": {
                "by_type": system_metrics.error_counts,
                "total_count": sum(system_metrics.error_counts.values())
            }
        }
        
        if recent_errors:
            # Include recent error details
            recent_error_list = metrics_collector.get_recent_errors(limit=10)
            metrics_data["recent_errors"] = [
                {
                    "request_id": error.request_id,
                    "method": error.method,
                    "path": error.path,
                    "status_code": error.status_code,
                    "error_type": error.error_type,
                    "timestamp": error.timestamp.isoformat(),
                    "response_time_ms": error.response_time_ms
                }
                for error in recent_error_list
            ]
        
        return metrics_data
        
    except Exception as e:
        from app.utils.error_handler import ErrorType, CodeReviewException
        raise CodeReviewException(
            error_type=ErrorType.INTERNAL_SERVER_ERROR,
            message="Failed to retrieve system metrics",
            details={"error": str(e)},
            status_code=500
        )


@router.post("/metrics/reset")
async def reset_metrics(current_user: User = Depends(api_key_auth)):
    """
    Reset system metrics collection.
    
    Requires authentication. Clears all collected metrics and starts fresh.
    Useful for testing or after system maintenance.
    
    Returns:
        Confirmation of metrics reset
    """
    try:
        metrics_collector.reset_metrics()
        
        return {
            "success": True,
            "message": "System metrics have been reset",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        from app.utils.error_handler import ErrorType, CodeReviewException
        raise CodeReviewException(
            error_type=ErrorType.INTERNAL_SERVER_ERROR,
            message="Failed to reset system metrics",
            details={"error": str(e)},
            status_code=500
        )


@router.get("/status")
async def get_service_status():
    """
    Get basic service status without authentication.
    
    Provides minimal status information for external monitoring systems.
    Does not require authentication for basic availability checks.
    
    Returns:
        Basic service availability status
    """
    try:
        # Get basic health information
        health_data = HealthChecker.get_overall_health()
        
        return {
            "status": health_data["status"],
            "timestamp": health_data["timestamp"],
            "version": health_data["version"],
            "services_operational": all(
                service["status"] in ["healthy", "degraded"]
                for service in health_data["services"].values()
            )
        }
        
    except Exception:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0",
            "services_operational": False
        }