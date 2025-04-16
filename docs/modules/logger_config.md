# Logger Configuration Module (`logger_config.py`)

## Overview

Sets up centralized logging for the application. Configures a rotating file handler (`app.log`) and a console handler based on the `LOGGING_LEVELS` dictionary provided in `config.yaml`.

## Key Features

*   **Configuration via `config.yaml`:** Reads the `LOGGING_LEVELS` dictionary.
*   **File Logging:** Logs messages to `app.log` (hardcoded filename).
*   **Console Logging:** Logs messages to the standard output/console (stdout).
*   **Standard Formatting:** Applies a consistent format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`.
*   **Rotation:** Implements file rotation using `logging.handlers.RotatingFileHandler` (5MB max size, 2 backups).
*   **Multiple Levels:** Sets up different logging levels (`basic`, `detailed`, `error`) based on the `LOGGING_LEVELS` config, allowing different verbosity for different parts of the application (though modules need to request specific loggers like `logging.getLogger('detailed')` to use non-basic levels).

## Function: `setup_logging(config_path='config.yaml', log_file='app.log')`

*   **Purpose:** Initializes the logging system for the application.
*   **Arguments:**
    *   `config_path` (str): Path to the configuration file (defaults to `config.yaml`).
    *   `log_file` (str): Path to the log file (defaults to `app.log`).
*   **Workflow:**
    1.  Loads the configuration from `config_path` using `yaml`.
    2.  Retrieves the `LOGGING_LEVELS` dictionary from the config, providing defaults if keys are missing.
    3.  Converts level names (e.g., "INFO") to `logging` constants (e.g., `logging.INFO`).
    4.  Defines a `logging.Formatter`.
    5.  Creates a `logging.handlers.RotatingFileHandler` for `log_file` with rotation parameters.
    6.  Creates a `logging.StreamHandler` for console output (stdout).
    7.  Applies the formatter to both handlers.
    8.  Clears any existing handlers from the root logger.
    9.  Configures the root logger using `logging.basicConfig` with the `basic` level and both handlers.
    10. Sets specific levels for loggers named `detailed` and `error` based on the config.

## Integration Points

*   The `setup_logging()` function is called once at the beginning of `main.py`.
*   Other modules typically use `logging.getLogger(__name__)` (inheriting the `basic` level) or `logging.getLogger('detailed')` or `logging.getLogger('error')` for specific levels.

## Configuration (`config.yaml`)

Relies on this dictionary:

```yaml
# ----------------- Logging Configuration -----------------
LOGGING_LEVELS:
  basic: "INFO"    # Level for root logger (console and file)
  detailed: "DEBUG"  # Level for getLogger('detailed')
  error: "ERROR"     # Level for getLogger('error')
```

## Dependencies

*   `logging` (standard library, including `logging.handlers`)
*   `yaml` (for loading config)
*   `sys` (for `sys.stdout`)

[Back to Module Index](main.md)