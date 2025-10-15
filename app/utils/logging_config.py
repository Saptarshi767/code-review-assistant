"""
Logging configuration for the Code Review Assistant.
"""

import logging
import logging.config
import os
import sys
from datetime import datetime
from typing import Dict, Any


class RequestIDFilter(logging.Filter):
    """Filter to add request ID to log records."""
    
    def filter(self, record):
        # Try to get request ID from context
        request_id = getattr(record, 'request_id', None)
        if not request_id:
            # Try to get from thread local or other context
            request_id = 'no-request-id'
        
        record.request_id = request_id
        return True


class StructuredFormatter(logging.Formatter):
    """Structured JSON formatter for logs."""
    
    def format(self, record):
        # Create structured log entry
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add request ID if available
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        
        # Add extra fields from the record
        extra_fields = [
            'method', 'path', 'status_code', 'response_time_ms',
            'user_agent', 'ip_address', 'content_length', 'error_type',
            'query_params', 'traceback'
        ]
        
        for field in extra_fields:
            if hasattr(record, field):
                log_entry[field] = getattr(record, field)
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Convert to JSON string
        import json
        return json.dumps(log_entry, default=str)


def get_logging_config() -> Dict[str, Any]:
    """Get logging configuration based on environment."""
    
    # Determine log level from environment
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Determine if we're in development mode
    debug_mode = os.getenv('DEBUG', 'false').lower() == 'true'
    
    # Handle log directory for serverless environments
    if os.environ.get('VERCEL'):
        log_dir = '/tmp/logs'
    else:
        log_dir = os.getenv('LOG_DIR', './logs')
    
    # Create logs directory if it doesn't exist (only if writable)
    try:
        os.makedirs(log_dir, exist_ok=True)
        file_logging_enabled = True
    except OSError:
        # In read-only environments, disable file logging
        file_logging_enabled = False
    
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'request_id': {
                '()': RequestIDFilter,
            },
        },
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s (%(filename)s:%(lineno)d)',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s [%(request_id)s]: %(message)s (%(filename)s:%(lineno)d)',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'structured': {
                '()': StructuredFormatter,
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': log_level,
                'formatter': 'detailed' if debug_mode else 'standard',
                'filters': ['request_id'],
                'stream': sys.stdout
            }
        },
        'loggers': {
            # Application loggers
            'app': {
                'level': log_level,
                'handlers': ['console'],
                'propagate': False
            },
            'request_logger': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate': False
            },
            # FastAPI and Uvicorn loggers
            'uvicorn': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate': False
            },
            'uvicorn.access': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate': False
            },
            'fastapi': {
                'level': log_level,
                'handlers': ['console'],
                'propagate': False
            }
        },
        'root': {
            'level': log_level,
            'handlers': ['console']
        }
    }
    
    # Add file handlers only if file logging is enabled
    if file_logging_enabled:
        config['handlers'].update({
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': log_level,
                'formatter': 'structured',
                'filters': ['request_id'],
                'filename': os.path.join(log_dir, 'app.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'structured',
                'filters': ['request_id'],
                'filename': os.path.join(log_dir, 'error.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8'
            },
            'request_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'INFO',
                'formatter': 'structured',
                'filters': ['request_id'],
                'filename': os.path.join(log_dir, 'requests.log'),
                'maxBytes': 10485760,  # 10MB
                'backupCount': 10,
                'encoding': 'utf8'
            }
        })
        
        # Update loggers to include file handlers
        config['loggers']['app']['handlers'].extend(['file'])
        config['loggers']['request_logger']['handlers'].extend(['request_file'])
        config['loggers']['uvicorn.access']['handlers'].extend(['request_file'])
        config['loggers']['fastapi']['handlers'].extend(['file'])
        config['root']['handlers'].extend(['file', 'error_file'])
    
    return config


def setup_logging():
    """Setup logging configuration for the application."""
    config = get_logging_config()
    logging.config.dictConfig(config)
    
    # Set up logger for this module
    logger = logging.getLogger(__name__)
    logger.info("Logging configuration initialized")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(name)