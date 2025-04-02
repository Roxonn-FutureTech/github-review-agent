import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
import json
import uuid
from typing import Optional

class StructuredLogger(logging.Logger):
    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, **kwargs):
        if extra is None:
            extra = {}
        if 'correlation_id' not in extra:
            extra['correlation_id'] = getattr(self, 'correlation_id', str(uuid.uuid4()))
        super()._log(level, msg, args, exc_info, extra, stack_info)

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'correlation_id': getattr(record, 'correlation_id', 'unknown')
        }
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_data)

def setup_logging(
    log_dir: str = "logs",
    log_level: Optional[str] = None,
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Configure logging for the AI engine with rotation and structured output.
    
    Args:
        log_dir: Directory to store log files
        log_level: Override default log level (reads from ENV if None)
        max_bytes: Maximum size of each log file
        backup_count: Number of backup files to keep
    """
    
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Get log level from environment or use default
    log_level = log_level or os.getenv('LOG_LEVEL', 'INFO')
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Generate log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"ai_engine_{timestamp}.log")
    
    # Register custom logger class
    logging.setLoggerClass(StructuredLogger)
    
    # Create logger
    logger = logging.getLogger("ai_engine")
    logger.setLevel(numeric_level)
    
    # Clear any existing handlers
    logger.handlers = []
    
    # Create rotating file handler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setFormatter(JsonFormatter())
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(correlation_id)s: %(message)s'
    ))
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info("Logging system initialized", extra={
        'correlation_id': str(uuid.uuid4()),
        'log_level': log_level,
        'log_file': log_file
    })
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger with a new correlation ID."""
    logger = logging.getLogger(name)
    logger.correlation_id = str(uuid.uuid4())
    return logger
