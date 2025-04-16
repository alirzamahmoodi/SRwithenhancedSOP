# Report Storage Module (Oracle) (`store_transcribed_report.py`)

## Purpose

This module is responsible for persisting the final transcribed reports **into the Oracle database** and updating associated study statuses within that specific database schema. It interacts with tables like `TREPORT`, `TSTUDY`, and potentially `TREPORTTEXT` to store the report and mark the study as complete (e.g., `REPORT_STAT = 4010`) within the Oracle system.

**Note:** This module handles *Oracle persistence*. The primary storage for dashboard monitoring and general results is handled by `database_operations.py` writing to MongoDB.

## Class: `StoreTranscribedReport`

*   Handles the connection and logic for storing reports in the Oracle database.
*   Initialized with the application `config` dictionary.

## Main Method: `store_transcribed_report(self, study_key, report_list)`

*   **Purpose:** Executes the workflow to store the transcription (`report_list`) associated with the `study_key` into the configured Oracle tables.
*   **Parameters:**
    *   `study_key` (str): Unique study identifier.
    *   `report_list` (str or list): The transcribed text report.
*   **Raises:**
    *   `oracledb.DatabaseError`: For Oracle connection or transaction failures.
    *   Potential errors related to data parsing or unexpected database function results.
*   **Workflow:**
    1.  Establishes a connection to the Oracle database.
    2.  Parses the input `report_list`:
        *   If it's a string, attempts to parse it as JSON.
        *   Expects the result to be a list containing a single dictionary (e.g., `[{"Reading": "...", "Conclusion": "..."}]`).
        *   Extracts the "Reading" and "Conclusion" text from the dictionary.
    3.  Retrieves the specific `REPORT_KEY` from `TREPORT` for the given `study_key` where `REPORT_STAT` was initially 3010.
    4.  Calls the Oracle function `DEB_TREPORT.F_GET_TEXTKEY`.
    5.  Calls the Oracle function `DEB_TREPORT.F_INSERT_TEXT` with the report details (Reading, Conclusion).
    6.  Retrieves `INSTITUTION_KEY` and `SRC_PATIENT_ID` from `TSTUDY`.
    7.  Calls the Oracle function `DEB_TREPORT.F_UPDATE` with various parameters including keys and the new status (4010).
    8.  Explicitly updates `TREPORT` table, setting `REPORT_STAT` to 4010 for the retrieved `REPORT_KEY`.
    9.  Explicitly updates `TSTUDY` table, setting `STUDYSTAT` to 4010 for the `study_key`.
    10. Commits the transaction.
    11. Handles errors by attempting a rollback and logging.
    12. Closes cursor and connection in a `finally` block.

## Key Functionality

*   **Oracle Integration:** Interacts directly with the Oracle schema for final report storage.
*   **Status Updates (Oracle):** Manages specific status codes within the Oracle `TREPORT` table.
*   **Transaction Management:** Ensures atomic updates across relevant Oracle tables.

## Configuration Requirements

Relies on Oracle connection details in `config.yaml`:

*   `ORACLE_HOST`
*   `ORACLE_PORT`
*   `ORACLE_SERVICE_NAME`
*   `ORACLE_USERNAME`
*   `ORACLE_PASSWORD`

Execution of this module is controlled by the following setting in `config.yaml`:

*   `STORE_TRANSCRIBED_REPORT`: Set to `"ON"` to enable calling this module from `main.py`. Set to `"OFF"` to disable.

## Error Handling

*   Catches and logs database errors during connection or transactions.
*   May handle specific data format errors if parsing `report_list`.

## Dependencies

*   `oracledb`: For Oracle database connectivity.
*   `logging`: For logging operations and errors.
*   `json`: For parsing the report list if provided as a string.
*   `datetime`, `traceback`: Standard library utilities.

## Usage Example

```python
# Within main.py's run_pipeline function, typically called after successful transcription
if config.get('STORE_TRANSCRIBED_REPORT', 'OFF') == 'ON':
    try:
        store_module = StoreTranscribedReport(config)
        store_module.store_transcribed_report(study_key, report_list)
        logging.info(f"Stored report in Oracle for study {study_key}")
    except Exception as e:
        logging.error(f"Failed during Oracle report storage for {study_key}: {e}")
        # Optionally update MongoDB status to reflect this specific failure
        # db_ops.update_study_status(config, study_key, "error", error_message=f"Oracle storage failed: {e}")
```

## Related Documents
- [System Architecture](../high_level/architecture.md)
- [Configuration Reference](../high_level/config_reference.md)
- [Main Workflow](main.md)
- [Module: database_operations](database_operations.md)