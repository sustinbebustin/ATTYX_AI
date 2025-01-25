import logging
import json
from datetime import datetime
from typing import Any, Dict
from functools import wraps
import sys
import asyncio

class CustomFormatter(logging.Formatter):
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def format(self, record):
        if isinstance(record.msg, (dict, list)):
            record.msg = json.dumps(record.msg)
        return super().format(record)

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(CustomFormatter())
        logger.addHandler(handler)
        
    return logger

def log_execution_time(logger: logging.Logger):
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            try:
                result = await func(*args, **kwargs)
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                logger.info({
                    "function": func.__name__,
                    "execution_time": execution_time,
                    "status": "success"
                })
                return result
            except Exception as e:
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                logger.error({
                    "function": func.__name__,
                    "execution_time": execution_time,
                    "status": "error",
                    "error": str(e)
                })
                raise
                
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            try:
                result = func(*args, **kwargs)
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                logger.info({
                    "function": func.__name__,
                    "execution_time": execution_time,
                    "status": "success"
                })
                return result
            except Exception as e:
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                logger.error({
                    "function": func.__name__,
                    "execution_time": execution_time,
                    "status": "error",
                    "error": str(e)
                })
                raise
                
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

class StructuredLogger:
    def __init__(self, name: str, level: int = logging.INFO):
        self.logger = setup_logger(name, level)
        
    def log_event(self, event_type: str, data: Dict[str, Any], level: int = logging.INFO):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "data": data
        }
        self.logger.log(level, log_entry)
        
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        }
        self.log_event("error", error_data, logging.ERROR)