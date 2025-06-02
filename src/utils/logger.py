import logging
import os
from pathlib import Path

def setup_logger(name='trading_signal_ai', log_file='logs/pipeline.log', level=logging.INFO):
    """
    Set up a logger with file and console handlers
    
    Args:
        name (str): Logger name
        log_file (str): Path to the log file
        level (int): Logging level
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create directory for log file if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Create handlers
    file_handler = logging.FileHandler(log_file)
    console_handler = logging.StreamHandler()
    
    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Create a default logger instance
logger = setup_logger()
