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
MODEL_NAME: "gemini-2.0-flash" # Or the specific model you intend to use

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

# ----------------- Core Service Operation -----------------
# Controls behavior of the main transcription pipeline (main.py)
ENCAPSULATE_TEXT_AS_ENHANCED_SR: "OFF" # Enable SR DICOM generation ("ON"/"OFF")
STORE_TRANSCRIBED_REPORT: "ON"         # Enable legacy storage via store_transcribed_report.py ("ON"/"OFF") - Review necessity vs MongoDB
PRINT_GEMINI_OUTPUT: "ON"              # Print transcription results to console ("ON"/"OFF")

# ----------------- Logging Configuration -----------------
# Defines different logging levels used by logger_config.py
LOGGING_LEVELS:
  basic: "INFO"    # Default level for general logging
  detailed: "DEBUG"  # Level for detailed diagnostic logs
  error: "ERROR"     # Level for error-specific logs

# --- Deprecated/Replaced Keys (Example) ---
# These might be leftover from previous versions and can likely be removed
# LONGTERM_USERNAME: "persiangulfadmin" # Replaced by SHARE_USERNAME or unused
# LONGTERM_PASSWORD: "secure_password"  # Replaced by SHARE_PASSWORD or unused
```

## Configuration Parameters Table

| Section         | Key                           | Required | Purpose                                                              | Notes / Example Values                                           |
|-----------------|-------------------------------|----------|----------------------------------------------------------------------|------------------------------------------------------------------|
| AI Services     | `GEMINI_API_KEY`              | Yes      | Authentication key for the transcription API service.                | String (e.g., `AIzaSy...`)                                       |
| AI Services     | `MODEL_NAME`                  | Yes      | Specific model to use for transcription.                             | String (e.g., `gemini-2.0-flash`)                                |
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
| Core Service    | `ENCAPSULATE_TEXT_AS_ENHANCED_SR` | Yes      | Enable/disable DICOM Enhanced SR generation.                       | `"ON"` / `"OFF"`                                                 |
| Core Service    | `STORE_TRANSCRIBED_REPORT`    | Yes      | Enable/disable legacy report storage (review relevance).           | `"ON"` / `"OFF"`                                                 |
| Core Service    | `PRINT_GEMINI_OUTPUT`         | Yes      | Print transcription results directly to console.                   | `"ON"` / `"OFF"`                                                 |
| SR Generation   | `SR_OUTPUT_FOLDER`            | Yes*     | Directory to save generated Enhanced SR DICOM files.               | String (Path, *Required if `ENCAPSULATE_TEXT_AS_ENHANCED_SR` is ON) |
| Logging         | `LOGGING_LEVELS`              | Yes      | Dictionary defining logging levels for different loggers.            | Dict (e.g., `{basic: INFO, detailed: DEBUG, error: ERROR}`)     |

## Configuration Flow
```