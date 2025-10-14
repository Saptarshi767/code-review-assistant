"""
Monitoring and metrics collection utilities for the Code Review Assistant.
"""

import time
import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from collections import defaultdict, deque
from threading import Lock
from dataclasses import dataclass, asdict
from fastapi import Request, Response
from pydantic import BaseModel

logger = logging.getLogger(__name__)


@dataclass
class RequestMetrics:
    """Metrics for a single request."""
    request_id: str
    method: str
    path: str
    status_code: int
    response_time_ms: float
    timestamp: datetime
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    content_length: Optional[int] = None
    error_type: Optional[str] = None


@dataclass
class SystemMetrics:
    """System-wide metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    requests_per_minute: float = 0.0
    error_rate: float = 0.0
    uptime_seconds: float = 0.0
    
    # Endpoint-specific metrics
    endpoint_metrics: Dict[str, Dict[str, Any]] = None
    
    # Error metrics
    error_counts: Dict[str, int] = None
    
    def __post_init__(self):
        if self.endpoint_metrics is None:
            self.endpoint_metrics = {}
        if self.error_counts is None:
            self.error_counts = {}


class MetricsCollector:
    """Thread-safe metrics collection system."""
    
    def __init__(self, max_history: int = 1000):
        self._lock = Lock()
        self._request_history: deque = deque(maxlen=max_history)
        self._endpoint_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'error_count': 0,
            'status_codes': defaultdict(int)
        })
        self._error_counts = defaultdict(int)
        self._start_time = time.time()
    
    def record_request(self, metrics: RequestMetrics):
        """Record metrics for a completed request."""
        with self._lock:
            self._request_history.append(metrics)
            
            # Update endpoint statistics
            endpoint_key = f"{metrics.method} {metrics.path}"
            stats = self._endpoint_stats[endpoint_key]
            stats['count'] += 1
            stats['total_time'] += metrics.response_time_ms
            stats['status_codes'][metrics.status_code] += 1
            
            if metrics.status_code >= 400:
                stats['error_count'] += 1
                if metrics.error_type:
                    self._error_counts[metrics.error_type] += 1
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics."""
        with self._lock:
            if not self._request_history:
                return SystemMetrics(uptime_seconds=time.time() - self._start_time)
            
            total_requests = len(self._request_history)
            successful_requests = sum(1 for r in self._request_history if r.status_code < 400)
            failed_requests = total_requests - successful_requests
            
            # Calculate average response time
            total_time = sum(r.response_time_ms for r in self._request_history)
            avg_response_time = total_time / total_requests if total_requests > 0 else 0.0
            
            # Calculate requests per minute (last 60 seconds)
            now = datetime.now(timezone.utc)
            recent_requests = [
                r for r in self._request_history 
                if (now - r.timestamp).total_seconds() <= 60
            ]
            requests_per_minute = len(recent_requests)
            
            # Calculate error rate
            error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0.0
            
            # Prepare endpoint metrics
            endpoint_metrics = {}
            for endpoint, stats in self._endpoint_stats.items():
                endpoint_metrics[endpoint] = {
                    'total_requests': stats['count'],
                    'avg_response_time_ms': stats['total_time'] / stats['count'] if stats['count'] > 0 else 0.0,
                    'error_count': stats['error_count'],
                    'error_rate': (stats['error_count'] / stats['count'] * 100) if stats['count'] > 0 else 0.0,
                    'status_codes': dict(stats['status_codes'])
                }
            
            return SystemMetrics(
                total_requests=total_requests,
                successful_requests=successful_requests,
                failed_requests=failed_requests,
                avg_response_time_ms=avg_response_time,
                requests_per_minute=requests_per_minute,
                error_rate=error_rate,
                uptime_seconds=time.time() - self._start_time,
                endpoint_metrics=endpoint_metrics,
                error_counts=dict(self._error_counts)
            )
    
    def get_recent_errors(self, limit: int = 10) -> List[RequestMetrics]:
        """Get recent error requests."""
        with self._lock:
            errors = [r for r in self._request_history if r.status_code >= 400]
            return sorted(errors, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def reset_metrics(self):
        """Reset all collected metrics."""
        with self._lock:
            self._request_history.clear()
            self._endpoint_stats.clear()
            self._error_counts.clear()
            self._start_time = time.time()


# Global metrics collector instance
metrics_collector = MetricsCollector()


class RequestLogger:
    """Enhanced request logging with structured format."""
    
    def __init__(self, logger_name: str = "request_logger"):
        self.logger = logging.getLogger(logger_name)
    
    def log_request_start(self, request: Request, request_id: str):
        """Log the start of a request."""
        self.logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "user_agent": request.headers.get("user-agent"),
                "ip_address": self._get_client_ip(request),
                "content_length": request.headers.get("content-length"),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    
    def log_request_end(
        self,
        request: Request,
        response: Response,
        request_id: str,
        response_time_ms: float,
        error_type: Optional[str] = None
    ):
        """Log the completion of a request."""
        log_level = logging.ERROR if response.status_code >= 400 else logging.INFO
        
        self.logger.log(
            log_level,
            f"Request completed - {response.status_code}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "response_time_ms": response_time_ms,
                "user_agent": request.headers.get("user-agent"),
                "ip_address": self._get_client_ip(request),
                "content_length": response.headers.get("content-length"),
                "error_type": error_type,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
        
        # Record metrics
        metrics = RequestMetrics(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            response_time_ms=response_time_ms,
            timestamp=datetime.now(timezone.utc),
            user_agent=request.headers.get("user-agent"),
            ip_address=self._get_client_ip(request),
            content_length=int(response.headers.get("content-length", 0)) or None,
            error_type=error_type
        )
        
        metrics_collector.record_request(metrics)
    
    def _get_client_ip(self, request: Request) -> Optional[str]:
        """Extract client IP address from request."""
        # Check for forwarded headers first (for reverse proxy setups)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return None


# Global request logger instance
request_logger = RequestLogger()


class HealthChecker:
    """System health monitoring utilities."""
    
    @staticmethod
    def check_llm_service() -> Dict[str, Any]:
        """Check LLM service health."""
        try:
            from app.services.llm_service import llm_service
            
            provider_status = llm_service.get_provider_status()
            current_provider = llm_service.current_provider
            
            # Try to get the provider to test configuration
            try:
                provider = llm_service.get_provider()
                status = "healthy"
                message = f"LLM service operational with {current_provider}"
            except ValueError as e:
                status = "degraded"
                message = f"LLM service configuration issue: {str(e)}"
            except Exception as e:
                status = "unhealthy"
                message = f"LLM service error: {str(e)}"
            
            return {
                "status": status,
                "message": message,
                "current_provider": current_provider,
                "providers": provider_status,
                "last_checked": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Failed to check LLM service: {str(e)}",
                "last_checked": datetime.now(timezone.utc).isoformat()
            }
    
    @staticmethod
    def check_file_storage() -> Dict[str, Any]:
        """Check file storage health."""
        try:
            import os
            from config import settings
            
            # Check if upload and reports directories exist and are writable
            upload_dir_ok = os.path.exists(settings.upload_dir) and os.access(settings.upload_dir, os.W_OK)
            reports_dir_ok = os.path.exists(settings.reports_dir) and os.access(settings.reports_dir, os.W_OK)
            
            if upload_dir_ok and reports_dir_ok:
                status = "healthy"
                message = "File storage directories accessible"
            else:
                status = "degraded"
                issues = []
                if not upload_dir_ok:
                    issues.append(f"Upload directory issue: {settings.upload_dir}")
                if not reports_dir_ok:
                    issues.append(f"Reports directory issue: {settings.reports_dir}")
                message = f"File storage issues: {', '.join(issues)}"
            
            return {
                "status": status,
                "message": message,
                "upload_dir": settings.upload_dir,
                "reports_dir": settings.reports_dir,
                "upload_dir_writable": upload_dir_ok,
                "reports_dir_writable": reports_dir_ok,
                "last_checked": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Failed to check file storage: {str(e)}",
                "last_checked": datetime.now(timezone.utc).isoformat()
            }
    
    @staticmethod
    def check_system_resources() -> Dict[str, Any]:
        """Check system resource usage."""
        try:
            import psutil
            
            # Get CPU and memory usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Determine status based on resource usage
            status = "healthy"
            warnings = []
            
            if cpu_percent > 80:
                status = "degraded"
                warnings.append(f"High CPU usage: {cpu_percent}%")
            
            if memory.percent > 80:
                status = "degraded"
                warnings.append(f"High memory usage: {memory.percent}%")
            
            if disk.percent > 90:
                status = "degraded"
                warnings.append(f"High disk usage: {disk.percent}%")
            
            message = "System resources normal" if not warnings else f"Resource warnings: {', '.join(warnings)}"
            
            return {
                "status": status,
                "message": message,
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "warnings": warnings,
                "last_checked": datetime.now(timezone.utc).isoformat()
            }
            
        except ImportError:
            return {
                "status": "unknown",
                "message": "psutil not available for system monitoring",
                "last_checked": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Failed to check system resources: {str(e)}",
                "last_checked": datetime.now(timezone.utc).isoformat()
            }
    
    @staticmethod
    def get_overall_health() -> Dict[str, Any]:
        """Get overall system health status."""
        llm_health = HealthChecker.check_llm_service()
        storage_health = HealthChecker.check_file_storage()
        system_health = HealthChecker.check_system_resources()
        metrics = metrics_collector.get_system_metrics()
        
        # Determine overall status
        service_statuses = [llm_health["status"], storage_health["status"], system_health["status"]]
        
        if all(status == "healthy" for status in service_statuses):
            overall_status = "healthy"
        elif any(status == "unhealthy" for status in service_statuses):
            overall_status = "unhealthy"
        else:
            overall_status = "degraded"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": {
                "llm": llm_health,
                "storage": storage_health,
                "system": system_health
            },
            "metrics": asdict(metrics),
            "version": "1.0.0"
        }