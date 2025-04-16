# Database Monitor Module (`database_monitor.py`)

## Overview

Implements continuous monitoring of an Oracle database table (`TSTUDY`) to detect new studies that require transcription. When a new study is found, it directly calls the processing worker function to handle the transcription pipeline for that study.

## Key Features & Workflow

1.  **Initialization (`__init__`)**: Stores configuration, initializes running state (`self.is_running`), polling interval (`self.poll_interval` from config or default), and a set (`self.attempted_studies`) to track studies processed during the current run to avoid reprocessing the same key immediately after an error or restart.
2.  **Monitoring Loop (`start_monitoring`)**: 
    *   Establishes connections to Oracle and ensures the MongoDB connection is available (via `db_ops.get_db`).
    *   Enters a loop that runs while `self.is_running` is True.
    *   Inside the loop:
        *   Queries the `TSTUDY` table for records with a specific status (e.g., `STUDYSTAT = 3010`).
        *   For each `study_key` found that hasn't been attempted in this run:
            *   Calls `database_operations.update_study_status` to create/update the record in MongoDB with status `received` (this prevents duplicate processing if the monitor restarts quickly and makes the study visible on the dashboard immediately).
            *   Adds `study_key` to `self.attempted_studies`.
            *   **Directly calls** `processing_worker.process_study(self.config, study_key)`.
            *   The loop **waits** for `process_study` to complete before checking Oracle again or proceeding to the next study key found in the current batch.
            *   Includes basic error handling around the call to `process_study` itself, logging critical errors and updating the study status to `error` as a last resort.
        *   Sleeps for the configured `poll_interval` (checking `self.is_running` periodically) before starting the next polling cycle.
3.  **Shutdown (`stop_monitoring`)**: Sets `self.is_running` to `False`, causing the polling loop to exit gracefully after its current cycle and sleep interval.

## Integration Points

*   Initialized and started by `main.py` when run with the `--monitor` flag.
*   Requires Oracle DB connection details in `config.yaml` (`ORACLE_*`).
*   Requires MongoDB connection details in `config.yaml` (`MONGODB_*`) to interact with `database_operations`.
*   Calls `database_operations.update_study_status` to log the initial state (`received`) to MongoDB.
*   Directly calls `processing_worker.process_study` to trigger the core processing pipeline.

## Error Handling

*   Logs Oracle database connection/query errors during polling.
*   Logs MongoDB connection errors before starting the loop.
*   Includes basic error checking for the direct call to `processing_worker.process_study`.
*   Graceful shutdown on `KeyboardInterrupt` (Ctrl+C) via `main.py`.

## Dependencies

*   Standard libraries: `threading` (though not actively used for workers now), `logging`, `os`, `sys`, `time`.
*   `oracledb`: For connecting to the Oracle database.
*   `modules.database_operations`: For updating study status in MongoDB.
*   `modules.processing_worker`: Contains the function (`process_study`) that executes the pipeline.

## Cross References
- [Module: main](main.md)
- [Module: processing_worker](processing_worker.md)
- [Module: database_operations](database_operations.md)