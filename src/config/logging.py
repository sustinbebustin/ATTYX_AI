import logging
import logging.config
import structlog
from typing import Dict, Any

from .settings import get_settings

def setup_logging() -> None:
    """Configure logging for the application"""
    settings = get_settings()
    
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": structlog.processors.JSONRenderer(),
            },
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
            },
            "json_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "logs/attyx_ai.json",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "formatter": "json",
            },
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["console", "json_file"],
                "level": settings.LOG_LEVEL,
            },
            "attyx_ai": {
                "handlers": ["console", "json_file"],
                "level": settings.LOG_LEVEL,
                "propagate": False,
            },
        },
    }
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Apply configuration
    logging.config.dictConfig(logging_config)