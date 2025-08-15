import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
import sys

def setup_logger(name: str = "investment_advisor") -> logging.Logger:
    """
    Set up a comprehensive logger with file and console handlers
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Set log level
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, log_level))
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    log_file = os.getenv("LOG_FILE", "app.log")
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    return logger

def log_api_request(logger: logging.Logger, method: str, path: str, status_code: int, 
                   user_id: str = None, duration: float = None):
    """Log API request details"""
    user_info = f" (User: {user_id})" if user_id else ""
    duration_info = f" ({duration:.3f}s)" if duration else ""
    
    logger.info(f"API {method} {path} - {status_code}{user_info}{duration_info}")

def log_error(logger: logging.Logger, error: Exception, context: str = "", user_id: str = None):
    """Log error with context"""
    user_info = f" (User: {user_id})" if user_id else ""
    context_info = f" [{context}]" if context else ""
    
    logger.error(f"Error{context_info}{user_info}: {str(error)}", exc_info=True)

def log_security_event(logger: logging.Logger, event_type: str, details: str, user_id: str = None, 
                      ip_address: str = None):
    """Log security-related events"""
    user_info = f" (User: {user_id})" if user_id else ""
    ip_info = f" (IP: {ip_address})" if ip_address else ""
    
    logger.warning(f"SECURITY {event_type}{user_info}{ip_info}: {details}")

# Global logger instance
app_logger = setup_logger("investment_advisor")
