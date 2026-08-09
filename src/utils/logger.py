import logging
import os
import sys
from pathlib import Path

# 1. Define the root directory of the project
# This navigates up two levels from src/utils/logger.py to reach the root folder
BASE_DIR = Path(__file__).resolve().parents[2]

# 2. Define the path for the log directory and the log file
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "app.log"

# Create the 'logs' directory automatically if it does not exist yet
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(logger_name: str) -> logging.Logger:
    """
    Creates and configures a custom logger for the application.
    
    Args:
        logger_name (str): The name of the module calling the logger (usually __name__).
        
    Returns:
        logging.Logger: A fully configured logger object.
    """
    # Initialize the logger with the specific module name
    logger = logging.getLogger(logger_name)
    
    # Set the global logging level to INFO (captures INFO, WARNING, ERROR, CRITICAL)
    logger.setLevel(logging.INFO)

    # Prevent duplicate log messages if the logger is instantiated multiple times
    if logger.hasHandlers():
        return logger

    # 3. Create Handlers
    # Console handler: Outputs logs to the terminal
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # File handler: Saves logs to the app.log file with UTF-8 encoding
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.INFO)

    # 4. Define the Log Format
    # Example output: "2026-08-09 15:30:45 - entrypoint.api - INFO - Model loaded successfully"
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Attach the formatter to both handlers
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # 5. Add the handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger