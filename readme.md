# Audio Transcriber Service with Enhanced SR and Dashboard

This project provides a service to monitor for medical studies, extract associated audio dictations, transcribe them, store the results, and optionally generate DICOM Enhanced Structured Reports (SR). It now includes a web dashboard to monitor the status of processing.

# Documentation Structure

The detailed documentation is located within the `docs/` directory:

```bash
SRwithenhancedSOP/
├── docs/
│   ├── high_level/
│   │   ├── architecture.md  # Overall system design
│   │   ├── installation.md  # Detailed setup instructions
│   │   ├── logging.md       # Logging configuration
│   │   └── config_reference.md # Details on config.yaml options
│   │   └── dashboard.md    # (NEW) Info about the web dashboard
│   ├── modules/
│   │   ├── main.md
│   │   ├── query.md
│   │   ├── extract_audio.md
│   │   ├── transcribe.md
│   │   ├── database_monitor.md
│   │   ├── store_transcribed_report.md # (Review relevance)
│   │   ├── encapsulate_text_as_enhanced_sr.md
│   │   ├── logger_config.md
│   │   ├── database_operations.md # (NEW) MongoDB interactions
│   │   └── smb_connect.md         # (NEW) Network share connections
│   └── ...
├── dashboard/             # Django dashboard project
├── modules/               # Core processing modules
├── config.yaml            # Main configuration file
├── environment.yml        # Conda environment definition
├── main.py                # Main application entry point
└── readme.md              # This file
```
*(Structure slightly simplified for readability)*

# Installation and Setup

See `docs/high_level/installation.md` for detailed steps. A summary:

1.  **Prerequisites:**
    *   Install Miniconda or Anaconda.
    *   Install MongoDB and ensure the server is running.
2.  **Create/Update Conda Environment:**
    ```bash
    # If creating for the first time:
    conda env create -f environment.yml
    # If updating an existing environment:
    conda env update --file environment.yml --prune
    ```
3.  **Activate Environment:**
    ```bash
    conda activate google-ai
    ```
4.  **Configure `config.yaml`:**
    *   Set `ORACLE_*` parameters for database monitoring.
    *   Set `MONGODB_*` parameters for data storage.
    *   Set `SHARE_*` parameters if accessing files on authenticated network shares.
    *   Configure transcription service details (API keys, etc. - *specific keys depend on `modules/transcribe.py` implementation*).
    *   Set `DJANGO_SECRET_KEY` for the dashboard.
5.  **Set up Django Dashboard:**
    ```bash
    cd dashboard
    python manage.py migrate
    python manage.py createsuperuser
    cd ..
    ```
6.  **(Optional) Build Executable:**
    ```bash
    pip install pyinstaller # If not already installed via environment.yml
    pyinstaller PG_Transcriber.spec
    ```
    *Note: If building, ensure `config.yaml` is placed correctly relative to the executable as described in the Run Instructions.*

# Run Instructions

1.  **Ensure Prerequisites are Running:**
    *   MongoDB server must be running.
    *   Oracle database (if using monitor mode) must be accessible.
2.  **Activate Environment:**
    ```bash
    conda activate google-ai
    ```
3.  **Start the Django Dashboard (Optional, in a separate terminal):**
    ```bash
    cd dashboard
    python manage.py runserver
    ```
    Access the dashboard at `http://127.0.0.1:8000/` and the admin interface at `http://127.0.0.1:8000/admin/`.
4.  **Start the Transcriber Service (in a separate terminal):**
    *   **Monitor Mode (Recommended):** Listens for new studies via Oracle DB.
        ```bash
        python main.py --monitor
        ```
    *   **Single Study Mode:** Processes a specific study key.
        ```bash
        python main.py <STUDY_KEY>
        ```
    *   **Using Built Executable (if built):**
        ```bash
        cd dist/ # Or wherever the build output is
        # Ensure config.yaml is in this directory
        PG_Transcriber.exe --monitor
        # OR
        PG_Transcriber.exe <STUDY_KEY>
        ```

--- 

