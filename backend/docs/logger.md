# How `logger.py` Works

This module provides a centralized logging utility for Python applications, supporting both console output and basic file logging.

### Core Function: `setup_logger()`

- Configures the root logger with:
  - Console logging (stdout)
  - File logging to a specified filename (`app.log` by default)
- Log file is saved in the current working directory (or wherever specified via `log_file`).
- Uses a consistent log format including timestamp, level, and message:

```
%(asctime)s [%(levelname)s] %(message)s
```

- Clears any existing handlers to avoid duplicate logs (useful during development with hot reload).

### Module-Level Logger Instance

- A global `logger` instance is created by default (`logger = setup_logger()`).
- This instance can be imported and used throughout the application for consistent logging.

### Direct Script Execution

When run as a standalone script (`python logger.py`):
- Logs an informational message indicating logger initialization.
- Demonstrates error logging by deliberately triggering a division by zero error, logging the full stack trace (`exc_info=True`).

### Summary

This logging setup:
- Enables clean and consistent logging to both console and a flat log file.
- Keeps implementation simple and lightweight.
- Prevents duplicate logging handlers.
- Provides an easy-to-import global logger instance for uniform use across the project.

*This approach improves visibility and maintainability in small to medium Python apps.*
