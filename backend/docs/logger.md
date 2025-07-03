# How `logger.py` Works

This module provides a centralized logging utility for the HobbyMatch backend, supporting both console output and rotating log files.

### Core Function: `setup_logger()`

- Configures the root logger with:
  - Console logging (stdout)
  - Rotating file logging with automatic file rollover based on file size (default 5MB)
- Log files are stored in a configurable directory (`logs` by default).
- Log files are named with date and hour in the format:  
  `app_YYYY-MM-DD_HH00.log` (e.g., `app_2025-07-01_1400.log`)
- Keeps a configurable number of backup log files (default 5).
- Uses a consistent log format including timestamp, level, and message:

```
%(asctime)s [%(levelname)s] %(message)s
```

- Clears any existing handlers to avoid duplicate logs (useful during development with hot reload).

### Module-Level Logger Instance

- A global `logger` instance is created by default (`logger = setup_logger()`).
- This instance can be imported and used throughout the backend for consistent logging.

### Direct Script Execution

When run as a standalone script (`python logger.py`):
- Logs an informational message indicating logger initialization.
- Demonstrates error logging by deliberately triggering a division by zero error, logging the full stack trace (`exc_info=True`).

### Summary

This logging setup:
- Enables clean and consistent logging to both console and file.
- Supports automatic log file rotation to prevent oversized files.
- Organizes logs by date and hour for easy identification.
- Prevents duplicate logging handlers.
- Provides an easy-to-import global logger instance for uniform use across the app.

*This approach improves maintainability and debuggability of HobbyMatch backend logs.*
