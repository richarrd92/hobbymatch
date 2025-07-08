import logging  
import sys    

# Sets up a logger that writes to both console and file.
def setup_logger(log_file="app.log", level=logging.INFO):

    logger = logging.getLogger()
    logger.setLevel(level)

    # Clear existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    # Define consistent log format
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (log file)
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Create a global logger instance
logger = setup_logger()

# Example usage
if __name__ == "__main__":
    logger.info("Logger initialized")
    try:
        1 / 0  # Simulate an error
    except Exception as e:
        # Log error with traceback
        logger.error(f"An error occurred: {e}", exc_info=True)
