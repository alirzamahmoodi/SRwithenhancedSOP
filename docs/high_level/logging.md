
# System Debugging Guide

## Logging Architecture
- **Three-tier logging**: Basic (INFO), Detailed (DEBUG), Error (ERROR)
- **Rotation**: 5MB file size with 2 backups
- **Outputs**: Combined file (app.log) + console

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

## Debugging Scenarios

**Scenario 1: Missing DICOM Audio**
```log
ERROR - extract_audio - DICOM does not contain WaveformSequence
DEBUG - extract_audio - Applying long path prefix for Windows
```
**Solution:** Verify DICOM contains waveform data, check Windows path length

**Scenario 2: Database Connection Issues**
```log
ERROR - database_monitor - Database connection failed: ORA-12541
INFO - query - Creating DSN for Oracle connection
```
**Solution:** Validate Oracle credentials in config.yaml, check network connectivity

## Log Configuration Reference
```yaml
LOGGING_LEVELS:
  basic: INFO    # Console level
  detailed: DEBUG # File logging
  error: ERROR   # Critical alerts
```

**Trace Enablement:** 
```python
# Enable full debug tracing
logging.getLogger('detailed').setLevel(logging.DEBUG)
logging.getLogger().setLevel(logging.DEBUG)
```

**Audit Trail Fields:**
- Timestamp
- Module name
- Study key (where applicable)
- File paths
- Database keys