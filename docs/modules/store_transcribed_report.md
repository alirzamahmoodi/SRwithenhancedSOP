# Report Storage Module

## Purpose
Persists transcribed reports to Oracle database and updates study statuses. Maintains audit trails and ensures data integrity across multiple database tables.

## Class Overview
```python
class StoreTranscribedReport:
    """
    <mcsymbol name="StoreTranscribedReport" filename="store_transcribed_report.py" path="e:\SRwithenhancedSOP\store_transcribed_report.py" startline="3" type="class"></mcsymbol>
    Handles final storage of structured reports in PACS database
    
    Args:
        config (dict): Database connection parameters
    """
```

## Main Method
```python
def store_transcribed_report(self, study_key: str, report_list: str) -> None:
    """
    <mcsymbol name="StoreTranscribedReport.store_transcribed_report" filename="store_transcribed_report.py" path="e:\SRwithenhancedSOP\store_transcribed_report.py" startline="9" type="function"></mcsymbol>
    Executes complete storage workflow
    
    Parameters:
        study_key (str): Unique study identifier
        report_list (str): JSON-formatted transcription results
    
    Raises:
        DatabaseError: Connection/transaction failures
        JSONDecodeError: Invalid transcription format
    """
```

## Key Functionality
1. **Transaction Management**
   - Atomic updates across TREPORT/TSTUDY/TREPORTTEXT
   - Database function wrappers (F_INSERT_TEXT, F_UPDATE)
   - Automatic connection pooling

2. **Data Handling**
   - JSON report parsing
   - Institution-specific key management
   - Audit timestamp generation

3. **Status Workflow**
   - REPORT_STAT transitions (4010 = stored and 3010 = dictated)
   - STUDYSTAT updates
   - Cross-table consistency checks

## Configuration Requirements
```yaml
# From <mcfile name="config.yaml" path="e:\SRwithenhancedSOP\config.yaml"></mcfile>
database:
  oracle_host: "OracleServerUrl"
  oracle_service_name: "persiangulf"
  oracle_username: "dodeulbyeol"
  oracle_password: "secure_password"
```

## Error Handling
| Error Type            | Frequency | Resolution                      |
|-----------------------|-----------|---------------------------------|
| `JSONDecodeError`      | Medium    | Validate transcription output   |
| `DatabaseError`       | High      | Check connection parameters     |
| `IndexError`          | Low       | Verify report structure         |

## Dependencies
```text
- oracledb: Database connectivity
- json: Report parsing
- logging: Transaction auditing
```

## Usage Example
```python
from store_transcribed_report import StoreTranscribedReport

storage = StoreTranscribedReport(config)
storage.store_transcribed_report("STUDY_2024_12345", json_report)
```

## Related Documents
- [Database Configuration](high_level/config_reference.md)
- [Main Workflow](modules/main.md)
```