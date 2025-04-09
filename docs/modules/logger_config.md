# Logger Configuration Module (`logger_config.py`)

## Overview

Sets up centralized logging for the application. Configures a file handler (with rotation) and a console handler based on settings provided in `config.yaml`.

## Key Features

*   **Configuration via `config.yaml`:** Reads `LOG_LEVEL` and `LOG_FILE` from the config.
*   **File Logging:** Logs messages to the specified `LOG_FILE`.
*   **Console Logging:** Logs messages to the standard output/console.
*   **Standard Formatting:** Applies a consistent format to log messages, including timestamp, level, and message.
*   **(Potential) Rotation:** The implementation *may* include file rotation (e.g., using `logging.handlers.RotatingFileHandler`), although this needs to be verified in the code itself. The previous documentation mentioned it, but the current config keys (`LOG_LEVEL`, `LOG_FILE`) don't explicitly define rotation parameters.

## Function: `setup_logging()`

*   **Purpose:** Initializes the root logger for the application.
*   **Arguments:** Takes an optional `config` dictionary (though the current implementation might load `config.yaml` internally - check code).
*   **Workflow:**
    1.  Reads `LOG_LEVEL` and `LOG_FILE` from the configuration.
    2.  Creates a `logging.FileHandler` for the specified `LOG_FILE`.
    3.  Creates a `logging.StreamHandler` for console output.
    4.  Defines a `logging.Formatter` for consistent message appearance.
    5.  Applies the formatter to both handlers.
    6.  Adds both handlers to the root logger.
    7.  Sets the overall level of the root logger based on `LOG_LEVEL`.

## Integration Points

*   The `setup_logging()` function is typically called once at the very beginning of `main.py` before any other significant operations.
*   All other modules can then get the logger instance using `logging.getLogger(__name__)` and will inherit the configured handlers and level.

## Configuration (`config.yaml`)

Relies on these keys:

```yaml
# ----------------- Logging Configuration -----------------
LOG_LEVEL: "INFO" # Overall logging level (e.g., DEBUG, INFO, WARNING, ERROR)
LOG_FILE: "app.log" # Path to the log file (relative to project root)
```

## Dependencies

*   `logging` (standard library)
*   `yaml` (for loading config, if done internally)
*   `os` (potentially for path manipulation)

[Back to Module Index](main.md)