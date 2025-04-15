# System Logging and Debugging Guide

## Logging Architecture

The application utilizes Python's built-in `logging` module, configured centrally by `modules/logger_config.py`.

*   **Configuration:** Primarily driven by the `LOGGING_LEVELS` dictionary in `config.yaml`. This dictionary specifies the logging level (e.g., "INFO", "DEBUG") for different logger categories (e.g., `basic`, `detailed`, `error`).
*   **Outputs:** 
    *   **File:** Logs messages to a hardcoded file named `app.log` in the project root. The level for file logging is determined by the `basic` entry in the `LOGGING_LEVELS` dictionary.
    *   **Console:** Logs messages to standard output (the terminal). The level for console output is also determined by the `basic` entry in the `LOGGING_LEVELS` dictionary.
*   **Levels:** The `LOGGING_LEVELS` settings control the minimum severity of messages captured. For example, the `basic` level applies to the root logger and general output, while `detailed` might be used for specific verbose modules (though this requires modules to explicitly get the `detailed` logger).
*   **Format:** Log messages typically include timestamp, log level, logger name (e.g., `root`, `detailed`), and the message itself.
*   **Rotation:** File rotation (5MB limit, 2 backups) is implemented using `RotatingFileHandler` in `logger_config.py`. This is not configurable via `config.yaml`.

## Key Log Locations and Interpretation

*   **`app.log`:** This is the primary file for detailed debugging. To capture the most information, ensure the `basic` and `detailed` levels in `config.yaml`'s `LOGGING_LEVELS` are set to `"DEBUG"`.
*   **Console Output:** Provides real-time feedback, typically reflecting the `basic` logging level (`"INFO"` by default).

## Interpreting Common Log Messages

*(Note: Specific messages depend on the implementation in each module. This is a general guide.)*

| Module                 | Level   | Example Message Fragment                        | Possible Meaning                                                        |
|------------------------|---------|-------------------------------------------------|-------------------------------------------------------------------------|
| **Root/Main**          | INFO    | `Starting database monitor mode...`             | Application started with `--monitor` flag.                                |
|                        | INFO    | `Successfully connected to MongoDB database...` | Initial connection to MongoDB succeeded.                                |
|                        | INFO    | `DICOM file path: \\server\share\...`           | Path constructed by `query.py`.                                         |
|                        | INFO    | `Attempting network share connection...`        | `smb_connect` is trying to authenticate to a UNC path.                  |
|                        | INFO    | `Network share connection successful...`        | Authentication to share succeeded or connection already existed.        |
|                        | INFO    | `Audio extracted and saved to: ... .wav`        | `extract_audio` successfully created the temporary WAV file.            |
|                        | INFO    | `Transcription saved for study ...`             | `database_operations` saved results to MongoDB `transcriptions` collection. |
|                        | INFO    | `Updated study ... status to ...`               | `database_operations` updated the status in MongoDB `studies` collection. |
|                        | INFO    | `Temporary audio file deleted...`             | Successful cleanup in `main.py`'s `finally` block.                     |
|                        | WARNING | `UNC path detected ... but SHARE_USERNAME...`   | UNC path needs authentication, but credentials missing in `config.yaml`.  |
|                        | WARNING | `Connection to ... likely already exists...`    | `smb_connect` found an existing (possibly conflicting) connection.        |
|                        | WARNING | `Failed to delete temporary audio file...`      | Cleanup failed, temporary file might remain.                            |
|                        | ERROR   | `Failed to authenticate to network share...`    | `smb_connect` failed (check credentials, path, permissions).            |
|                        | ERROR   | `Pipeline error (FileNotFound)...`              | File access failed after path construction/auth (check path, permissions).|
|                        | ERROR   | `Pipeline error for study key ...: ...`       | General error during `run_pipeline`. Check message/traceback.           |
| **database_monitor**   | INFO    | `Connected to Oracle database for monitoring.`  | Monitor successfully connected to Oracle.                               |
|                        | INFO    | `Detected study ... Adding to queue.`           | New study found in Oracle.                                              |
|                        | INFO    | `Added study ... to processing queue.`          | MongoDB status updated to 'received', key added to queue.               |
|                        | INFO    | `Processing study key from queue: ...`          | Worker thread picked up a study.                                        |
|                        | INFO    | `Subprocess for ... completed successfully.`    | `main.py <study_key>` subprocess finished without error code.           |
|                        | ERROR   | `Database connection failed: ...`             | Monitor could not connect to Oracle.                                    |
|                        | ERROR   | `Error during monitoring query: ...`          | Error executing the polling query against Oracle.                       |
|                        | ERROR   | `Subprocess for ... failed with code ...`       | `main.py <study_key>` subprocess exited with an error. Check stderr.    |
| **query**              | INFO    | `Creating DSN for Oracle connection.`           | Preparing Oracle connection string.                                     |
|                        | INFO    | `Connecting to Oracle database.`                | Attempting connection.                                                  |
|                        | INFO    | `Constructed potential DICOM path: ...`         | Path string successfully built.                                         |
|                        | ERROR   | `No TREPORT record found...`                  | Missing data in Oracle required for path construction.                  |
| **smb_connect**        | INFO    | `Attempting connection to network share: ...`   | Starting authentication attempt.                                        |
|                        | INFO    | `Successfully established connection to ...`    | `WNetAddConnection2` call succeeded.                                    |
|                        | ERROR   | `Authentication failed for ...`                 | Bad username/password (Error 1326).                                     |
|                        | ERROR   | `Network path not found: ...`                   | Bad server/share name (Error 53).                                       |
| **extract_audio**      | INFO    | `Audio extracted and saved to: ...`             | Success.                                                                |
|                        | ERROR   | `FileNotFoundError: ...`                        | Cannot access the input DICOM path provided by `main.py`.               |
|                        | ERROR   | `DICOM does not contain WaveformSequence`       | Input file is missing required audio data.                              |
| **transcribe**         | INFO    | *(Specific to API)*                             | Successful steps in API interaction.                                    |
|                        | ERROR   | *(Specific to API)*                             | API authentication, connection, or processing errors.                   |
| **database_operations**| INFO    | `Successfully connected to MongoDB...`          | Initial connection established.                                         |
|                        | INFO    | `Created new study record for ...`            | First status update for a study (upsert).                             |
|                        | INFO    | `Updated study ... status to ...`               | Subsequent status update.                                               |
|                        | INFO    | `Transcription saved for study ...`             | Result saved.                                                           |
|                        | ERROR   | `Could not connect to MongoDB: ...`             | Initial connection failed.                                              |
|                        | ERROR   | `Database connection not available...`          | Attempted DB operation when connection is down.                         |
|                        | ERROR   | `Failed to update status for study ...`       | Error during MongoDB `update_one`.                                      |
|                        | ERROR   | `Failed to save transcription for study ...`    | Error during MongoDB `insert_one`.                                      |

## Debugging Scenarios

**Scenario 1: File Not Found on Network Share**
*   **Check Logs For:**
    *   `query`: `Constructed potential DICOM path: \\server\share\...` (Path looks correct?)
    *   `main`: `Attempting network share connection...` (Did it try?)
    *   `smb_connect`: Any errors like `Authentication failed` or `Network path not found`? (Credentials/Path issue?)
    *   `main`: `Pipeline error (FileNotFound)...` (If auth seemed okay, does the *specific file* exist? Permissions on the file itself?)
*   **Actions:** Verify share path, credentials in `config.yaml`, user permissions on the share/file, file existence.

**Scenario 2: MongoDB Connection Failure**
*   **Check Logs For:**
    *   `database_operations`: `Could not connect to MongoDB: ...` (Check error details - refused? timeout?)
    *   Subsequent `database_operations`: `Database connection not available...`
*   **Actions:** Ensure MongoDB server is running, accessible from where the script runs, `MONGODB_URI` in `config.yaml` is correct, check firewalls.

**Scenario 3: Oracle Connection Failure (Monitor)**
*   **Check Logs For:**
    *   `database_monitor`: `Database connection failed: ...`
*   **Actions:** Ensure Oracle DB is running, accessible, `ORACLE_*` settings in `config.yaml` are correct, check firewalls, check Oracle client setup if not using thin client.

**Scenario 4: Transcription API Error**
*   **Check Logs For:**
    *   `transcribe`: Errors mentioning API keys, authentication, connection timeouts, service unavailable, specific API error codes.
*   **Actions:** Verify API key in `config.yaml`, check network connectivity to the API endpoint, check API service status dashboard.

## Log Configuration (`config.yaml`)

```yaml
# ----------------- Logging Configuration -----------------
# Defines different logging levels used by logger_config.py
LOGGING_LEVELS:
  basic: "INFO"    # Default level for general logging (console/file)
  detailed: "DEBUG"  # Level for detailed diagnostic logs (if used by module)
  error: "ERROR"     # Level for error-specific logs (if used by module)
```

**To Enable Debug Logging:** Change the `basic` level (and potentially `detailed`) to `"DEBUG"` in `config.yaml`'s `LOGGING_LEVELS` section and restart the application.

## Complete Log Statements Catalog

### 1. Main Application (main.py)
<mcsymbol name="main" filename="main.py" path="e:\SRwithenhancedSOP\main.py" startline="1" type="function"></mcsymbol>

| Log Level | Statement | Purpose | Module |
|-----------|-----------|---------|--------|
| INFO | `"Starting database monitor mode..."` | Monitor mode activation | Main |
| INFO | `"Processing study key from queue: {study_key}"` | Queue processing | Main |
| ERROR | `"Error processing study key {study_key}: {err}"` | Study key failures | Main |
| WARNING | `"Failed to delete temporary audio file {audio_path}"` | Cleanup issues | Main |

### 2. Database Monitor (database_monitor.py)
<mcsymbol name="DatabaseMonitor" filename="database_monitor.py" path="e:\SRwithenhancedSOP\modules\database_monitor.py" startline="10" type="class"></mcsymbol>

| Log Level | Statement | Purpose | Module |
|-----------|-----------|---------|--------|
| DEBUG | `"Database cursor has been closed."` | Connection cleanup | DB Monitor |
| INFO | `"Connected to Oracle database for monitoring."` | DB connection success | DB Monitor |
| ERROR | `"Database connection failed: {e}"` | Connection failures | DB Monitor |

### 3. Query Processor (query.py)
<mcsymbol name="process_study_key" filename="query.py" path="e:\SRwithenhancedSOP\modules\query.py" startline="10" type="function"></mcsymbol>

| Log Level | Statement | Purpose | Module |
|-----------|-----------|---------|--------|
| DEBUG | `"DSN: {dsn}"` | Connection string debug | Query |
| ERROR | `"No TREPORT record found..."` | Missing database records | Query |
| WARNING | `"Error on attempt {attempt+1} reading file"` | File read retries | Query |

### 4. Audio Extraction (extract_audio.py)
<mcsymbol name="ExtractAudio.extract_audio" filename="extract_audio.py" path="e:\SRwithenhancedSOP\modules\extract_audio.py" startline="12" type="function"></mcsymbol>

| Log Level | Statement | Purpose | Module |
|-----------|-----------|---------|--------|
| DEBUG | `"Applying long path prefix for Windows"` | Windows path handling | Audio |
| ERROR | `"DICOM does not contain WaveformSequence"` | Invalid DICOM files | Audio |
| INFO | `"Audio extracted and saved to: {wav_path}"` | Success notification | Audio |

### 5. Transcription Engine (transcribe.py)
<mcsymbol name="Transcribe.transcribe" filename="transcribe.py" path="e:\SRwithenhancedSOP\modules\transcribe.py" startline="18" type="function"></mcsymbol>

| Log Level | Statement | Purpose | Module |
|-----------|-----------|---------|--------|
| DEBUG | `"Audio file uploaded successfully..."` | API upload success | Transcribe |
| CRITICAL | `"Google Cloud service unavailable"` | API outages | Transcribe |
| ERROR | `"Invalid DICOM file: {dcm_path}"` | File validation | Transcribe |

### 6. Report Storage (store_transcribed_report.py)
<mcsymbol name="StoreTranscribedReport.store_transcribed_report" filename="store_transcribed_report.py" path="e:\SRwithenhancedSOP\modules\store_transcribed_report.py" startline="12" type="function"></mcsymbol>

| Log Level | Statement | Purpose | Module |
|-----------|-----------|---------|--------|
| DEBUG | `"Retrieved INSTITUTION_KEY..."` | DB record retrieval | Storage |
| INFO | `"TREPORTTEXT record inserted..."` | Success confirmation | Storage |
| ERROR | `"Failed to parse report_list"` | Data validation | Storage |

### 7. SR Encapsulation (encapsulate_text_as_enhanced_sr.py)
<mcsymbol name="EncapsulateTextAsEnhancedSR.encapsulate_text_as_enhanced_sr" filename="encapsulate_text_as_enhanced_sr.py" path="e:\SRwithenhancedSOP\modules\encapsulate_text_as_enhanced_sr.py" startline="12" type="function"></mcsymbol>

| Log Level | Statement | Purpose | Module |
|-----------|-----------|---------|--------|
| INFO | `"Encapsulating text as Enhanced SR..."` | Process start | SR Encapsulation |
| DEBUG | `"DICOM file read successfully"` | File validation | SR Encapsulation |
| ERROR | `"Failed to write WAV file"` | Output failures | SR Encapsulation |