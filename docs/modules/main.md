# Main Application Module (`main.py`)

## Purpose

Orchestrates the complete audio transcription processing pipeline. It serves as the main entry point, handling command-line arguments for different operational modes (single study vs. continuous monitoring), loading configuration, initializing database connections (MongoDB and potentially Oracle for monitoring), and coordinating calls to various modules to perform the transcription workflow.

## Core Function: `run_pipeline(study_key)`

This function executes the full processing workflow for a single study identified by `study_key`.

**Workflow:**

1.  **Update Status (Start):** Updates the study status to `processing_query` in MongoDB via `database_operations.update_study_status`.
2.  **Get Path:** Calls `query.process_study_key` to retrieve the potential DICOM file path from the Oracle database based on the `study_key`.
3.  **Connect to Share (Conditional):**
    *   Checks if the retrieved path is a UNC path (`\\server\share\...`).
    *   If it is, and if `SHARE_USERNAME`/`SHARE_PASSWORD` are configured, calls `smb_connect.connect_to_share` to establish an authenticated connection to the network share.
    *   If authentication fails, updates status to `error` in MongoDB and exits.
4.  **Update Status (Audio):** Updates status to `processing_audio` in MongoDB, storing the `dicom_path`.
5.  **Extract Audio:** Calls `extract_audio.extract_audio`, passing the file path. This step accesses the file system (potentially using the authenticated share connection).
6.  **Update Status (Transcribing):** Updates status to `transcribing` in MongoDB.
7.  **Transcribe:** Calls `transcribe.transcribe`, passing the path to the temporary audio file extracted in the previous step.
8.  **Handle Results:**
    *   If transcription is successful (`report_list` is generated):
        *   Calls `database_operations.save_transcription` to store the results in MongoDB.
        *   Updates status to `processing_complete` (or `processing_complete_sr` if SR encapsulation is enabled) in MongoDB.
        *   (Optional) Calls `encapsulate_text_as_enhanced_sr` if enabled.
        *   (Optional) Calls `store_transcribed_report` (legacy storage) if enabled.
    *   If transcription fails (`report_list` is empty or None):
        *   Updates status to `error` in MongoDB with an appropriate message.
9.  **Error Handling:** A `try...except` block wraps the main workflow. Catches specific errors like `FileNotFoundError` and general `Exception`. Updates status to `error` in MongoDB upon failure.
10. **Cleanup:** A `finally` block ensures temporary audio files are deleted.

## Core Function: `main()`

*   Parses command-line arguments (`STUDY_KEY` or `--monitor`).
*   Loads configuration from `config.yaml`.
*   Initializes logging using `logger_config.setup_logging`.
*   Establishes the initial MongoDB connection via `database_operations.connect_db`.
*   **Monitor Mode (`--monitor`):**
    *   Instantiates `DatabaseMonitor`.
    *   Calls `monitor.start_monitoring()`, which polls the Oracle DB and triggers `run_pipeline` (via subprocess) for new studies.
*   **Single Study Mode (`STUDY_KEY` provided):**
    *   Directly calls `run_pipeline(args.STUDY_KEY)`.

## Key Functionality

*   **Dual Operation Modes:** Supports processing single studies via CLI or continuously monitoring an Oracle database.
*   **Configuration Driven:** Behavior is controlled via `config.yaml`.
*   **Status Tracking:** Uses `database_operations` to log detailed status updates for each study in MongoDB.
*   **Network Authentication:** Integrates `smb_connect` to handle authentication for accessing files on network shares.
*   **Modular Orchestration:** Calls functions from various modules (`query`, `extract_audio`, `transcribe`, etc.) in sequence.
*   **Robust Error Handling:** Includes specific and general exception handling within the pipeline to log errors and update study status appropriately.

## Dependencies

*   Standard libraries: `sys`, `argparse`, `yaml`, `logging`, `subprocess`, `time`, `os`.
*   Project modules: `database_monitor`, `query`, `extract_audio`, `transcribe`, `store_transcribed_report`, `logger_config`, `database_operations`, `smb_connect`.
*   Third-party libraries via `environment.yml`: `oracledb` (used by monitor/query), `pymongo` (used by database_operations).

## Usage Examples

```bash
# Activate environment first
conda activate google-ai

# Single study processing
python main.py STUDY_2024_12345

# Monitor mode (service operation)
python main.py --monitor
```

## Cross References
- [System Architecture](../high_level/architecture.md)
- [Configuration Reference](../high_level/config_reference.md)
- [Installation Guide](../high_level/installation.md)
- [Module: database_operations](database_operations.md)
- [Module: smb_connect](smb_connect.md)
- [Module: query](query.md)
- [Module: database_monitor](database_monitor.md)