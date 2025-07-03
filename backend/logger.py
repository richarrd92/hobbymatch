import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logger(log_dir="logs", max_bytes=5 * 1024 * 1024, backup_count=5, level=logging.INFO):
    """
    Setup logger with console and rotating file handlers.
    - max_bytes: max file size before rotation (default 5MB)
    - backup_count: number of backup files to keep
    - log files named by current date and hour
    """

    # Create log directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Log filename format: app_YYYY-MM-DD_HH00.log
    log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y-%m-%d_%H00')}.log")

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(level)

    # Clear existing handlers to prevent duplication
    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Rotating file handler
    file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Global logger instance
logger = setup_logger()

if __name__ == "__main__":
    logger.info("Logger initialized")
    try:
        1 / 0
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
