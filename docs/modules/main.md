# Main Application Module (`main.py`)

## Purpose

Serves as the main entry point for launching the transcription service in **monitoring mode**. It handles command-line arguments (expecting `--monitor`), loads the central configuration, initializes logging, establishes initial database connections, and starts the `DatabaseMonitor` service.

## Core Function: `main()`

*   Loads configuration from `config.yaml` using `load_config`.
*   Initializes logging using `logger_config.setup_logging`, driven by settings in the loaded `config`.
*   Establishes the initial MongoDB connection via `database_operations.connect_db` (if not handled lazily later).
*   Parses command-line arguments using `argparse`. It **only** accepts the `--monitor` flag.
*   **Monitor Mode (`--monitor`):**
    *   Instantiates `DatabaseMonitor`, passing the loaded `config`.
    *   Calls `monitor.start_monitoring()`. This function contains the main loop that polls the Oracle DB and *directly calls* the `processing_worker.process_study` function for each new study.
    *   Includes error handling for `KeyboardInterrupt` (to gracefully stop the monitor) and other exceptions.
*   **No other modes:** If `--monitor` is not provided, it prints an error message and exits.

## Key Functionality

*   **Single Entry Point:** Provides the standard way to start the service (`python main.py --monitor`).
*   **Configuration Loading:** Ensures configuration is loaded centrally from `config.yaml`.
*   **Logging Initialization:** Sets up the application-wide logging.
*   **Monitor Initiation:** Creates and starts the `DatabaseMonitor` instance, which performs the actual work.

## Removed Functionality

*   The `run_pipeline` function (which contained the per-study processing logic) has been moved to `modules/processing_worker.py`.
*   The ability to process a single study via command-line argument (`python main.py <STUDY_KEY>`) has been removed. Processing is now initiated solely by the `DatabaseMonitor` finding studies in the Oracle DB.

## Dependencies

*   Standard libraries: `sys`, `argparse`, `yaml`, `logging`, `os`.
*   Project modules: `modules.database_monitor`, `modules.logger_config`, `modules.database_operations`.
*   Third-party libraries via `environment.yml`: `oracledb`, `cryptography` (may still be needed for Oracle connection initialization if `init_oracle_client` is used).

## Usage Example

```bash
# Activate environment first
conda activate google-ai

# Start the service in monitor mode
python main.py --monitor
```

## Cross References
- [System Architecture](../high_level/architecture.md)
- [Installation Guide](../high_level/installation.md)
- [Configuration Reference](../high_level/config_reference.md)
- [Module: database_monitor](database_monitor.md)
- [Module: processing_worker](processing_worker.md)
- [Module: logger_config](logger_config.md)
- [Module: database_operations](database_operations.md)