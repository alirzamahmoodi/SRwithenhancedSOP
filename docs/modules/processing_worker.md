# Processing Worker Module (`processing_worker.py`)

## Overview

This module contains the core logic for processing a single DICOM study through the entire transcription pipeline. It is designed to be called directly by other parts of the application (like the `DatabaseMonitor`) after a specific `study_key` has been identified for processing.

## Core Function: `process_study(config, study_key)`

This function executes the full processing workflow for a single study identified by `study_key`, using configuration parameters passed via the `config` dictionary.

**Workflow:**

1.  **Initialization:** Gets a logger instance.
2.  **Update Status (Start):** Updates the study status to `processing_query` in MongoDB via `database_operations.update_study_status`.
3.  **Get Path:** Calls `query.process_study_key` to retrieve the potential DICOM file path from the Oracle database based on the `study_key`. Validates the path.
4.  **Connect to Share (Conditional):**
    *   Checks if the retrieved path is a UNC path (`\\server\share\...`).
    *   If it is, and if `SHARE_USERNAME`/`SHARE_PASSWORD` are configured, calls `smb_connect.connect_to_share` to establish an authenticated connection to the network share.
    *   If authentication fails, updates status to `error` in MongoDB and exits the function.
5.  **Update Status (Audio):** Updates status to `processing_audio` in MongoDB, storing the `dicom_path`.
6.  **Initialize Components:** Creates instances of `ExtractAudio`, `Transcribe`, and potentially `EncapsulateTextAsEnhancedSR` and `StoreTranscribedReport` using the provided `config`.
7.  **Extract Audio:** Calls `extract_audio.extract_audio`, passing the file path. This step accesses the file system (potentially using the authenticated share connection). If extraction fails, updates status to `error` and exits.
8.  **Update Status (Transcribing):** Updates status to `transcribing` in MongoDB.
9.  **Transcribe:** Calls `transcribe.transcribe`, passing the DICOM path and the path to the temporary audio file extracted in the previous step. Receives a dictionary (`transcription_dict`) or `None`.
10. **Handle Results:**
    *   If transcription is successful (`transcription_dict` is valid):
        *   Calls `database_operations.save_transcription` to store the results (the dictionary) in MongoDB.
        *   Updates status to `processing_complete` in MongoDB.
        *   (Optional) Calls `encapsulate_text_as_enhanced_sr` if enabled (`config['ENCAPSULATE_TEXT_AS_ENHANCED_SR'] == 'ON'`). Updates the MongoDB transcription record with the `sr_path` and updates status to `processing_complete_sr`.
        *   (Optional) Calls `store_transcribed_report` (legacy storage) if enabled (`config['STORE_TRANSCRIBED_REPORT'] == 'ON'`). **Note:** It currently wraps `transcription_dict` in a list (`[transcription_dict]`) for this call, assuming the legacy function expects a list.
    *   If transcription fails (`transcription_dict` is None or invalid):
        *   Updates status to `error` in MongoDB with an appropriate message.
        *   Exits the function.
11. **Error Handling:** A `try...except` block wraps the main workflow. Catches specific errors like `FileNotFoundError` and general `Exception`. Updates status to `error` in MongoDB upon failure.
12. **Cleanup:** A `finally` block ensures the temporary audio file created during extraction is deleted (`os.remove`).

## Integration Points

*   Called directly by `modules.database_monitor.start_monitoring` for each study key found.
*   Receives `config` and `study_key` as arguments.
*   Relies on configuration values from the `config` dictionary for database connections, API keys, optional feature flags, share credentials, etc.
*   Uses various other modules for specific tasks:
    *   `modules.database_operations` (DB interactions)
    *   `modules.smb_connect` (Network share authentication)
    *   `modules.query` (Get DICOM path from Oracle)
    *   `modules.extract_audio` (Get audio from DICOM)
    *   `modules.transcribe` (Call transcription API)
    *   `modules.encapsulate_text_as_enhanced_sr` (Optional SR creation)
    *   `modules.store_transcribed_report` (Optional legacy storage)

## Error Handling

*   Specific checks for path validity and audio extraction failure.
*   Authentication failures for network shares are caught and logged.
*   General `try...except` blocks catch other exceptions during the process.
*   All caught errors should result in the study status being updated to `error` in MongoDB via `database_operations.update_study_status`.

## Dependencies

*   Standard libraries: `logging`, `os`, `sys`.
*   Project modules: `database_operations`, `smb_connect`, `query`, `extract_audio`, `transcribe`, `store_transcribed_report`, `encapsulate_text_as_enhanced_sr`.

## Cross References
- [System Architecture](../high_level/architecture.md)
- [Module: database_monitor](database_monitor.md)
- [Module: database_operations](database_operations.md) 