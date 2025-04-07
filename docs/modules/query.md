# Database Query Module

## Purpose
Handles database interactions and path resolution for DICOM studies. Provides critical linkage between study keys and physical file locations in PACS storage.

## Main Function
```python
def process_study_key(config, study_key):
    """
    <mcsymbol name="process_study_key" filename="query.py" path="e:\SRwithenhancedSOP\query.py" startline="9" type="function"></mcsymbol>
    Resolves study key to physical file location through database queries
    
    Parameters:
        config (dict): Application configuration
        study_key (str): Unique study identifier
        
    Returns:
        str: Full UNC path to DICOM file
    
    Raises:
        DatabaseError: Connection/query failures
        FileNotFoundError: Missing DICOM file
    """
```

## Key Functionality
1. **Database Connectivity**
   - DSN construction from configuration
   - Connection pooling management
   - Secure credential handling

2. **Query Chain**
   ```mermaid
   graph TD
     A[Study Key] --> B(TREPORT)
     B --> C(REPORT_KEY)
     C --> D(TDICTATION)
     D --> E(LSTORAGE_KEY)
     E --> F(TSTORAGE)
     F --> G(UNC Path)
   ```

3. **Path Construction**
   - Storage share resolution
   - Windows UNC path assembly
   - Filesystem validation

## Configuration Requirements
```yaml
# From <mcfile name="config.yaml" path="e:\SRwithenhancedSOP\config.yaml"></mcfile>
database:
  oracle_host: "OracleServerUrl"
  oracle_port: 1521
  oracle_service_name: "persiangulf"
  oracle_username: "dodeulbyeol"
  oracle_password: "secure_password"
```

## Error Handling
| Error Code | Trigger Condition | Resolution Action |
|------------|--------------------|-------------------|
| DB-001 | Missing TREPORT entry | Validate study completion status |
| DB-002 | TDICTATION mismatch | Check dictation workflow steps |
| FS-001 | Path not found | Verify storage share availability |

## Dependencies
```text
- oracledb: Oracle database access
- os: Path construction
- logging: Operational tracking
```

## Usage Example
```python
from query import process_study_key

dicom_path = process_study_key(config, "STUDY_2024_12345")
```

## Related Documents
- [System Architecture](high_level/architecture.md)
- [Database Configuration](high_level/config_reference.md)
- [Main Workflow](modules/main.md)
```