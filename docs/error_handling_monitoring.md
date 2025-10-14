# Error Handling and Monitoring System

This document describes the comprehensive error handling and monitoring system implemented for the Code Review Assistant.

## Overview

The system provides:
- Standardized error responses with detailed information
- Request logging and metrics collection
- Enhanced health check endpoints
- System monitoring and performance tracking
- Centralized error handling middleware

## Error Handling

### Error Types

The system defines standardized error types in `ErrorType` enum:

```python
class ErrorType(str, Enum):
    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    UNSUPPORTED_FORMAT = "UNSUPPORTED_FORMAT"
    INVALID_REQUEST = "INVALID_REQUEST"
    
    # Authentication and authorization errors
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    AUTHORIZATION_FAILED = "AUTHORIZATION_FAILED"
    API_KEY_INVALID = "API_KEY_INVALID"
    
    # Rate limiting errors
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"
    
    # Service errors
    LLM_SERVICE_ERROR = "LLM_SERVICE_ERROR"
    FILE_PROCESSING_ERROR = "FILE_PROCESSING_ERROR"
    STORAGE_ERROR = "STORAGE_ERROR"
    
    # System errors
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    
    # Resource errors
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    RESOURCE_GONE = "RESOURCE_GONE"
```

### Error Response Format

All errors return a standardized JSON response:

```json
{
  "error": "VALIDATION_ERROR",
  "message": "File validation failed",
  "details": {
    "errors": ["File size exceeds maximum limit"],
    "supported_formats": {...}
  },
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-15T10:30:00Z",
  "path": "/api/review",
  "method": "POST",
  "retry_after": null
}
```

### Custom Exceptions

The system provides custom exception classes:

- `CodeReviewException`: Base exception for application-specific errors
- `ValidationException`: For input validation errors
- `AuthenticationException`: For authentication failures
- `AuthorizationException`: For authorization failures
- `RateLimitException`: For rate limiting violations
- `ResourceNotFoundException`: For missing resources
- `ServiceUnavailableException`: For service availability issues

### Usage Examples

```python
# Raise validation error
from app.utils.error_handler import ValidationException
raise ValidationException("Invalid file format", details={"format": "exe"})

# Raise not found error
from app.utils.error_handler import raise_not_found
raise_not_found("Report", "invalid-id")

# Raise rate limit error
from app.utils.error_handler import raise_rate_limit_error
raise_rate_limit_error("Too many requests", retry_after=60)
```

## Monitoring and Metrics

### Request Logging

All requests are automatically logged with structured information:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "logger": "request_logger",
  "message": "Request completed - 200",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "method": "POST",
  "path": "/api/review",
  "status_code": 200,
  "response_time_ms": 1250.5,
  "user_agent": "Mozilla/5.0...",
  "ip_address": "192.168.1.100",
  "content_length": 1024
}
```

### Metrics Collection

The system collects comprehensive metrics:

- **Request Statistics**: Total, successful, failed requests
- **Performance Metrics**: Average response time, requests per minute
- **Error Tracking**: Error rates by type and endpoint
- **Endpoint Analytics**: Per-endpoint performance and error rates

### Health Check Endpoints

#### `/api/health` - Enhanced Health Check

Provides comprehensive system health information:

```bash
GET /api/health?include_metrics=true&include_services=true
```

Response includes:
- Overall system status
- Individual service health (LLM, storage, system resources)
- Optional system metrics
- Service availability indicators

#### `/api/status` - Basic Status

Provides minimal status for external monitoring:

```bash
GET /api/status
```

#### `/api/metrics` - Detailed Metrics

Requires authentication. Provides detailed system metrics:

```bash
GET /api/metrics?recent_errors=true
Authorization: Bearer <token>
```

### System Resource Monitoring

The system monitors:
- CPU usage percentage
- Memory usage percentage  
- Disk usage percentage
- Service availability (LLM, storage)

Warnings are generated when:
- CPU usage > 80%
- Memory usage > 80%
- Disk usage > 90%

## Middleware Components

### ErrorHandlingMiddleware

Centralized error handling that:
- Generates unique request IDs
- Logs all requests and responses
- Handles all exception types consistently
- Adds request tracking headers

### RequestValidationMiddleware

Pre-processes requests to:
- Validate content length limits
- Check authentication requirements
- Perform basic request validation

## Logging Configuration

### Log Levels and Formats

The system supports multiple log formats:
- **Standard**: Human-readable format for console output
- **Structured**: JSON format for log aggregation systems
- **Detailed**: Includes request IDs and additional context

### Log Files

Logs are written to multiple files:
- `app.log`: General application logs
- `error.log`: Error-level logs only
- `requests.log`: Request/response logs

### Log Rotation

All log files use rotation:
- Maximum size: 10MB per file
- Backup count: 5-10 files
- Automatic compression of old files

## Configuration

### Environment Variables

```bash
# Logging configuration
LOG_LEVEL=INFO
LOG_DIR=./logs
DEBUG=false

# Monitoring configuration
ENABLE_METRICS=true
METRICS_RETENTION_HOURS=24
```

### Dependencies

Required packages:
- `psutil>=5.9.6`: System resource monitoring
- `fastapi>=0.104.1`: Web framework with middleware support
- `pydantic>=2.5.0`: Data validation and serialization

## API Examples

### Health Check

```bash
# Basic health check
curl -X GET "http://localhost:8000/api/health"

# Health check with metrics
curl -X GET "http://localhost:8000/api/health?include_metrics=true"

# Basic status (no auth required)
curl -X GET "http://localhost:8000/api/status"
```

### Metrics (Requires Authentication)

```bash
# Get system metrics
curl -X GET "http://localhost:8000/api/metrics" \
  -H "X-API-Key: your-api-key"

# Get metrics with recent errors
curl -X GET "http://localhost:8000/api/metrics?recent_errors=true" \
  -H "X-API-Key: your-api-key"

# Reset metrics
curl -X POST "http://localhost:8000/api/metrics/reset" \
  -H "X-API-Key: your-api-key"
```

### Error Response Examples

```bash
# File too large error
{
  "error": "FILE_TOO_LARGE",
  "message": "File size exceeds maximum limit",
  "details": {
    "max_size_mb": 10,
    "actual_size_mb": 15
  },
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-15T10:30:00Z",
  "path": "/api/review",
  "method": "POST"
}

# Authentication error
{
  "error": "AUTHENTICATION_FAILED",
  "message": "Invalid API key",
  "request_id": "550e8400-e29b-41d4-a716-446655440001",
  "timestamp": "2024-01-15T10:31:00Z",
  "path": "/api/review",
  "method": "POST"
}

# Rate limit error
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Too many requests",
  "details": {
    "limit": 10,
    "window": "1 minute"
  },
  "request_id": "550e8400-e29b-41d4-a716-446655440002",
  "timestamp": "2024-01-15T10:32:00Z",
  "path": "/api/review",
  "method": "POST",
  "retry_after": 60
}
```

## Benefits

1. **Consistent Error Handling**: All errors follow the same format and structure
2. **Request Traceability**: Every request has a unique ID for tracking
3. **Comprehensive Monitoring**: Detailed metrics and health information
4. **Operational Visibility**: Real-time system status and performance data
5. **Debugging Support**: Structured logging with request correlation
6. **External Integration**: Standard endpoints for monitoring systems
7. **Performance Tracking**: Response time and error rate monitoring
8. **Resource Management**: System resource usage monitoring and alerting

This system provides the foundation for reliable operation, debugging, and monitoring of the Code Review Assistant service.