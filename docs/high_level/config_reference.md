# Configuration Reference

## Environment Setup (`environment.yml`)
```yaml
name: google-ai
channels:
  - defaults
  - conda-forge
dependencies:
  - python=3.11
  - oracledb=2.5.1    # Oracle DB connectivity
  - pip:
      - google-generativeai  # Core AI integration
      - pydicom             # DICOM processing
      - pynetdicom         # DICOM network ops
      - numpy              # Audio processing
      - cryptography       # Security functions
      - pywin32            # Windows integration
```

## Runtime Configuration (`config.yaml`)
```yaml
# ----------------- AI Services (Example: Gemini) -----------------
# Configure based on the needs of modules/transcribe.py
GEMINI_API_KEY: "your_api_key"  # Replace with your actual API key
MODEL_NAME: "gemini-1.5-flash" # Or the specific model you intend to use

# ----------------- Oracle DB (Monitor Source) -----------------
ORACLE_HOST: "172.31.100.60" # IP address or hostname of the Oracle server
ORACLE_PORT: 1521             # Port Oracle listener is running on
ORACLE_SERVICE_NAME: "persiangulf" # Oracle Service Name
ORACLE_USERNAME: "dodeulbyeol"  # Username for Oracle DB connection
ORACLE_PASSWORD: "secure_password" # Password for Oracle DB connection
# Optional: If using Oracle Instant Client path explicitly
# ORACLE_CLIENT_PATH: "C:/path/to/instantclient_XX_Y"

# ----------------- MongoDB (Application State & Results) -----------------
MONGODB_URI: "mongodb://localhost:27017/" # MongoDB connection string URI
MONGODB_DATABASE: "audio_transcriber_db"  # Name of the database to use in MongoDB
# Optional: Add MongoDB credentials if authentication is enabled
# MONGODB_USER: "myuser"
# MONGODB_PASSWORD: "mypassword"
# MONGODB_AUTH_SOURCE: "admin" # Or the relevant auth database
# MONGODB_AUTH_MECHANISM: "SCRAM-SHA-1"

# ----------------- Network Share Configuration (Optional) -----------------
# Credentials for accessing UNC paths (e.g., \\server\share\...) if needed
SHARE_USERNAME: ".\\persiangulfadmin" # Username (e.g., DOMAIN\\user, .\\user)
SHARE_PASSWORD: "Raoufsoft1003"      # Password for the network share user

# ----------------- Django Web Dashboard -----------------
# SECURITY WARNING: Keep the secret key used in production secret!
# Generate using: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
DJANGO_SECRET_KEY: "django-insecure-placeholder-replace-me-in-production"

# SECURITY WARNING: don't run with debug turned on in production!
DJANGO_DEBUG: True # Set to False for production

# Hosts/domain names that are allowed to access the dashboard
DJANGO_ALLOWED_HOSTS: [] # E.g., ["localhost", "127.0.0.1", "mydashboard.example.com"]

# ----------------- Core Service Operation -----------------
# Controls behavior of the main transcription pipeline (main.py)
ENCAPSULATE_TEXT_AS_ENHANCED_SR: "OFF" # Enable SR DICOM generation ("ON"/"OFF")
STORE_TRANSCRIBED_REPORT: "ON"         # Enable legacy storage via store_transcribed_report.py ("ON"/"OFF") - Review necessity vs MongoDB
PRINT_GEMINI_OUTPUT: "ON"              # Print transcription results to console ("ON"/"OFF")

# ----------------- Monitoring Service -----------------
# Controls behavior of modules/database_monitor.py
poll_interval: 60 # Seconds between checking Oracle DB for new studies

# ----------------- Logging Configuration -----------------
# Basic logging setup. See docs/high_level/logging.md for advanced configuration.
LOG_LEVEL: "INFO" # Overall logging level (e.g., DEBUG, INFO, WARNING, ERROR)
LOG_FILE: "app.log" # Path to the log file (relative to project root)

# --- Deprecated/Replaced Keys (Example) ---
# These might be leftover from previous versions and can likely be removed
# LONGTERM_USERNAME: "persiangulfadmin" # Replaced by SHARE_USERNAME
# LONGTERM_PASSWORD: "secure_password"  # Replaced by SHARE_PASSWORD
# LOGGING_LEVELS:
#   basic: "INFO"
#   detailed: "DEBUG"
#   error: "ERROR"
```

## Configuration Parameters Table

| Section         | Key                           | Required | Purpose                                                              | Notes / Example Values                                           |
|-----------------|-------------------------------|----------|----------------------------------------------------------------------|------------------------------------------------------------------|
| AI Services     | `GEMINI_API_KEY`              | Yes      | Authentication key for the transcription API service.                | String (e.g., `AIzaSy...`)                                       |
| AI Services     | `MODEL_NAME`                  | Yes      | Specific model to use for transcription.                             | String (e.g., `gemini-1.5-flash`)                                |
| Oracle DB       | `ORACLE_HOST`                 | Yes      | Hostname or IP of the Oracle database server.                        | String (e.g., `172.31.100.60`, `oradb.internal`)                 |
| Oracle DB       | `ORACLE_PORT`                 | Yes      | Port number for the Oracle listener.                                 | Integer (e.g., `1521`)                                           |
| Oracle DB       | `ORACLE_SERVICE_NAME`         | Yes      | Oracle Service Name for the target database.                         | String (e.g., `persiangulf`, `orclpdb`)                          |
| Oracle DB       | `ORACLE_USERNAME`             | Yes      | Username for connecting to Oracle.                                   | String                                                           |
| Oracle DB       | `ORACLE_PASSWORD`             | Yes      | Password for the Oracle user.                                        | String                                                           |
| Oracle DB       | `ORACLE_CLIENT_PATH`          | No       | Path to Oracle Instant Client libs (if not using included thin client). | String (Path)                                                    |
| MongoDB         | `MONGODB_URI`                 | Yes      | Connection string for MongoDB.                                       | String (e.g., `mongodb://user:pass@host:port/`, `mongodb://localhost:27017/`) |
| MongoDB         | `MONGODB_DATABASE`            | Yes      | Name of the database to use within MongoDB.                          | String (e.g., `audio_transcriber_db`)                            |
| Network Share   | `SHARE_USERNAME`              | No       | Username to authenticate to network shares (UNC paths).              | String (e.g., `DOMAIN\\user`, `.\user`, `user@domain.com`)       |
| Network Share   | `SHARE_PASSWORD`              | No       | Password for the network share user.                                 | String                                                           |
| Django          | `DJANGO_SECRET_KEY`           | Yes      | Secret key for Django cryptographic signing. **Keep secret!**      | Long random string                                               |
| Django          | `DJANGO_DEBUG`                | Yes      | Enables/disables Django debug mode (tracebacks, etc.).               | `True` / `False`                                                 |
| Django          | `DJANGO_ALLOWED_HOSTS`        | Yes      | List of allowed hostnames/IPs for accessing the dashboard.           | List of strings (e.g., `["localhost", "1.2.3.4"]`)             |
| Core Service    | `ENCAPSULATE_TEXT_AS_ENHANCED_SR` | Yes      | Enable/disable DICOM Enhanced SR generation.                       | `"ON"` / `"OFF"`                                                 |
| Core Service    | `STORE_TRANSCRIBED_REPORT`    | Yes      | Enable/disable legacy report storage (review relevance).           | `"ON"` / `"OFF"`                                                 |
| Core Service    | `PRINT_GEMINI_OUTPUT`         | Yes      | Print transcription results directly to console.                   | `"ON"` / `"OFF"`                                                 |
| Monitoring      | `poll_interval`               | Yes      | How often (in seconds) the monitor checks Oracle for new studies.    | Integer (e.g., `60`)                                             |
| Logging         | `LOG_LEVEL`                   | Yes      | Minimum level of logs to record (DEBUG, INFO, WARNING, ERROR).       | String (e.g., `"INFO"`)                                        |
| Logging         | `LOG_FILE`                    | Yes      | Name/path for the log file.                                          | String (e.g., `"app.log"`, `"logs/service.log"`)               |

## Configuration Flow
```mermaid
graph TD
    A[Start] --> B{Mode Check}
    B -->|Monitor| C[Database Polling]
    B -->|CLI| D[Single Study Processing]
    C --> E[Config.yaml Settings]
    D --> E
    E --> F[Load Environment]
    F --> G[Initialize Components]
```

## Related Documents
- [Installation Instructions](../high_level/installation.md)
- [Main Application Workflow](../modules/main.md)