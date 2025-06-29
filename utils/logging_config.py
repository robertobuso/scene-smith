"""
Logging configuration for SceneSmith.
"""

import os
import logging
from typing import Optional

def setup_logging(log_level: Optional[str] = None, log_file: Optional[str] = None) -> None:
    """Setup logging configuration for SceneSmith."""
    
    # Get configuration from environment
    level = log_level or os.getenv("LOG_LEVEL", "INFO")
    file_path = log_file or os.getenv("LOG_FILE", "scene_smith.log")
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # File handler
    try:
        file_handler = logging.FileHandler(file_path)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not setup file logging: {e}")
    
    # Console handler (only for warnings and errors to avoid cluttering CLI output)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Set specific logger levels
    logging.getLogger("crewai").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    logging.info("Logging configured successfully")
