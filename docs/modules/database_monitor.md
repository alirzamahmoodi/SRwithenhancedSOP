# Database Monitor Module (`database_monitor.py`)

## Overview

Implements continuous monitoring of an Oracle database table (`TSTUDY`) to detect new studies that require transcription. It manages a processing queue and launches the main pipeline (`main.py`) as a subprocess for each detected study.

## Key Features & Workflow

1.  **Initialization (`__init__`)**: Stores configuration, initializes running state and a `queue.Queue`.
2.  **Polling (`start_monitoring`)**: 
    *   Establishes a connection to the Oracle database using credentials from `config`.
    *   Enters a loop that runs while `self.is_running` is True.
    *   Inside the loop:
        *   Queries the `TSTUDY` table for records with a specific status (e.g., `STUDYSTAT = 3010`).
        *   For each `study_key` found:
            *   Calls `database_operations.update_study_status` to create/update the record in MongoDB with status `received` (this prevents duplicate processing and makes the study visible on the dashboard immediately).
            *   Adds the `study_key` to the internal `queue.Queue`.
        *   Sleeps for the configured `poll_interval` (default 60 seconds) before the next poll.
3.  **Worker Thread (`worker`)**: 
    *   Runs in a separate thread (`threading.Thread`).
    *   Continuously tries to get a `study_key` from the `queue.Queue`.
    *   When a key is retrieved:
        *   Determines the path to `main.py` (handling both script and PyInstaller executable contexts).
        *   Launches `main.py <study_key>` using `subprocess.run`. 
        *   Includes basic error handling for the subprocess execution, logging failures and updating the MongoDB status to `error` as a fallback if the subprocess fails to start or report its own error.
    *   Calls `queue.task_done()` after processing.
4.  **Shutdown (`stop_monitoring`)**: Sets `self.is_running` to `False`, causing the polling loop and worker thread to exit gracefully.

## Integration Points

*   Initialized and started by `main.py` when run with the `--monitor` flag.
*   Requires Oracle DB connection details in `config.yaml` (`ORACLE_*`).
*   Requires MongoDB connection details in `config.yaml` (`MONGODB_*`) to interact with `database_operations`.
*   Calls `database_operations.update_study_status` to log the initial state to MongoDB.
*   Triggers the core processing pipeline in `main.py` via subprocess calls.

## Error Handling

*   Logs Oracle database connection/query errors during polling.
*   Includes basic error checking for the `subprocess.run` call in the worker.
*   Graceful shutdown on `KeyboardInterrupt` (Ctrl+C) via `main.py`.

## Dependencies

*   Standard libraries: `threading`, `queue`, `logging`, `os`, `sys`, `subprocess`, `time`.
*   `oracledb`: For connecting to the Oracle database.
*   `modules.database_operations`: For updating study status in MongoDB.

[Back to Module Index](main.md)