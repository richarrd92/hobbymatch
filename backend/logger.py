import logging  
import sys    

def setup_logger(log_file="app.log", level=logging.INFO):
    """
    Configure and return a logger that outputs logs to both console and a file.

    Parameters:
    - log_file (str): Filename for the log file. Defaults to "app.log".
    - level (int): Logging level (e.g., logging.INFO, logging.DEBUG). Defaults to INFO.

    Returns:
    - logging.Logger: Configured root logger instance.

    Behavior:
    - Clears any existing handlers to prevent duplicate logging.
    - Sets a consistent log message format including timestamp and level.
    - Adds a console handler that outputs to stdout.
    - Adds a file handler that writes logs to the specified file.
    """

    logger = logging.getLogger()  # Get root logger
    logger.setLevel(level) # Set the logging threshold level

    # Remove existing handlers to avoid duplicate logs if this runs multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    # Define the log message format
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

    # Console handler: prints logs to stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler: writes logs to specified file
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Initialize and export a global logger instance for use across the app
logger = setup_logger()

# Suppress verbose SQLAlchemy engine logs, show only warnings and errors
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# Example usage if run as a standalone script
if __name__ == "__main__":
    logger.info("Logger initialized")
    try:
        1 / 0  # Deliberate ZeroDivisionError to demonstrate error logging
    except Exception as e:
        # Log the error with stack trace info for debugging
        logger.error(f"An error occurred: {e}", exc_info=True)
