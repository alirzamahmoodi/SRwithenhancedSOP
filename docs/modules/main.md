
# Main Application Module

## Purpose
Orchestrates the complete Enhanced SR processing pipeline. Handles both CLI and monitoring modes, manages database connections, and coordinates all system components.

## Class Overview
```python
class DatabaseMonitor:
    """
    <mcsymbol name="DatabaseMonitor" filename="main.py" path="e:\SRwithenhancedSOP\main.py" startline="35" type="class"></mcsymbol>
    Continuous database watcher for new studies
    
    Args:
        config (dict): Application configuration
    """
    
    def start_monitoring(self):
        """
        <mcsymbol name="DatabaseMonitor.start_monitoring" filename="main.py" path="e:\SRwithenhancedSOP\main.py" startline="66" type="function"></mcsymbol>
        Initiates polling of TREPORT table for studies needing processing
        """
```

## Core Functions
```python
def run_pipeline(study_key: str) -> None:
    """
    <mcsymbol name="run_pipeline" filename="main.py" path="e:\SRwithenhancedSOP\main.py" startline="113" type="function"></mcsymbol>
    Executes full processing workflow for a single study
    
    Workflow:
    1. Path resolution via <mcsymbol name="process_study_key" filename="query.py" path="e:\SRwithenhancedSOP\query.py" startline="9" type="function"></mcsymbol>
    2. Audio extraction using <mcsymbol name="ExtractAudio.extract_audio" filename="extract_audio.py" path="e:\SRwithenhancedSOP\extract_audio.py" startline="12" type="function"></mcsymbol>
    3. AI transcription via <mcsymbol name="Transcribe.transcribe" filename="transcribe.py" path="e:\SRwithenhancedSOP\transcribe.py" startline="18" type="function"></mcsymbol>
    4. Result storage with <mcsymbol name="StoreTranscribedReport.store_transcribed_report" filename="store_transcribed_report.py" path="e:\SRwithenhancedSOP\store_transcribed_report.py" startline="9" type="function"></mcsymbol>
    """
```

## Key Functionality
1. **Operation Modes**
   - **CLI Mode**: Process single studies via command line
   - **Monitor Mode**: Continuous database polling (REPORT_STAT=3010)
   - Self-reloading architecture for compiled EXEs

2. **Resource Management**
   - Oracle connection pooling
   - Thread-safe queue processing
   - Temporary file cleanup

3. **Deployment Features**
   - PyInstaller compatibility
   - Cross-environment path resolution
   - Config-driven Oracle client initialization

## Configuration Requirements
```yaml
# From <mcfile name="config.yaml" path="e:\SRwithenhancedSOP\config.yaml"></mcfile>
oracle:
  host: "OracleServerUrl"                # Database server address
  port: 1521                        # Listener port
  service_name: "persiangulf"            # TNS service name
  username: "dodeulbyeol"            # Application account
  password: "secure_password"       # Credential

monitor:
  poll_interval: 60                 # Seconds between DB checks
```

## Error Handling
| Error Scope         | Recovery Mechanism                |
|---------------------|------------------------------------|
| Database Connection | Exponential backoff retries       |
| Subprocess Failures | Queue requeuing with attempt log  |
| File System Errors  | Network share reconnection logic  |
| API Timeouts        | Circuit breaker pattern           |

## Dependencies
```text
- oracledb: Database connectivity
- pyinstaller: Executable packaging
- threading: Concurrent processing
- argparse: CLI interface management
```

## Usage Examples
```bash
# Single study processing
python main.py STUDY_2024_12345

# Monitor mode (service operation)
python main.py --monitor

# Compiled executable usage
audio_transcriber.exe --monitor
```

## Module Components
- [Database Monitor](database_monitor.md)
- [Logger Configuration](logger_config.md)
- [Encapsulate SR](encapsulate_text_as_enhanced_sr.md)
- [Query Processing](query.md)
- [Audio Extraction](extract_audio.md)
- [Transcription Engine](transcribe.md)
- [Report Storage](store_transcribed_report.md)

## Cross References
- [System Architecture](../high_level/architecture.md)
- [Configuration Reference](../high_level/config_reference.md)
- [Installation Guide](../high_level/installation.md)
```