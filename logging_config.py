"""
Logging configuration for Claude Memory System
"""
import logging
import logging.handlers
import os
import sys
from pathlib import Path

def setup_logging(name: str = 'claude_memory', level: str = None) -> logging.Logger:
    """
    Setup centralized logging for the application
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Configured logger instance
    """
    # Get log level from environment or default to INFO
    log_level = level or os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log directory exists or can be created)
    log_dir = Path(os.getenv('LOG_DIR', 'logs'))
    try:
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / f'{name}.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    except (PermissionError, OSError) as e:
        # If we can't create log files, continue with console only
        logger.warning(f"Could not setup file logging: {e}")
    
    return logger

def get_logger(name: str = None) -> logging.Logger:
    """Get a logger instance"""
    if name is None:
        name = 'claude_memory'
    
    # Return existing logger or create new one
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logging(name)
    return logger