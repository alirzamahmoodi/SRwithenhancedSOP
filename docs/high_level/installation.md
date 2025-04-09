# Installation Guide

This guide covers setting up the development environment and optionally building the application for deployment.

## System Requirements
- Windows 10/11 or Windows Server 2019/22/25 64-bit
- Anaconda or Miniconda
- Oracle Instant Client 19c+ (if not using thin client, which is included in the oracledb package)
- 4GB+ free disk space
- Access to an Oracle database (for monitor mode)
- MongoDB Server installed and running
- Git (for cloning the repository)
- Network access to transcription services (e.g., Google Gemini API) if used
- Network access to the Oracle DB and MongoDB
- Permissions to access network shares if DICOM files are stored there

## Development Setup Steps

1. **Clone Repository (If not already done):**
```bash
git clone https://github.com/alirzamahmoodi/SRwithenhancedSOP.git
cd SRwithenhancedSOP
```

2. **Create or Update Conda Environment:**
Navigate to the repository root (`SRwithenhancedSOP`).
```bash
# If creating the environment for the first time:
conda env create -f environment.yml

# If updating the environment after pulling changes or modifying environment.yml:
conda env update --file environment.yml --prune
```
This installs all necessary Python packages including Django, Pymongo, Djongo, Oracle drivers, etc.

3. **Activate Environment:**
Activate the environment every time you open a new terminal to work on the project.
```bash
conda activate google-ai
```
*(You should see `(google-ai)` prepended to your terminal prompt)*

4. **Configure `config.yaml`:**
Edit the `config.yaml` file in the project root. Fill in the necessary details:
- `ORACLE_HOST`, `ORACLE_PORT`, `ORACLE_SERVICE_NAME`, `ORACLE_USERNAME`, `ORACLE_PASSWORD`: For connecting to the Oracle database (used by the monitor).
- `MONGODB_URI`, `MONGODB_DATABASE`: For connecting to your MongoDB instance.
- `SHARE_USERNAME`, `SHARE_PASSWORD`: If the DICOM files reside on network shares requiring authentication (e.g., `\\server\share\path`).
- Transcription Service Details: API keys or other settings required by `modules/transcribe.py` (e.g., `GEMINI_API_KEY`).
- `DJANGO_SECRET_KEY`: Generate a strong random key (e.g., using `python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\"`) and place it here. **Do not commit the real secret key to version control.**
- `DJANGO_ALLOWED_HOSTS`: For development, `[]` might be okay, but for deployment, list the hostnames/IPs the dashboard will be accessed from.
- Review other options like `ENCAPSULATE_TEXT_AS_ENHANCED_SR`, `STORE_TRANSCRIBED_REPORT`, `PRINT_GEMINI_OUTPUT`.
*Refer to `config_reference.md` for details on all options.*

5. **Set Up Django Database:**
Navigate into the `dashboard` directory and run the migration commands.
```bash
cd dashboard
python manage.py migrate
```
This sets up the necessary collections/structures in MongoDB that Django uses.

6. **Create Django Admin User:**
While still in the `dashboard` directory, create a user to access the Django admin interface.
```bash
python manage.py createsuperuser
```
Follow the prompts.

7. **Return to Root Directory:**
```bash
cd ..
```

8. **Verify Setup (Optional):**
- Check Python package versions:
```bash
pip show django pymongo djongo oracledb
```
- Test MongoDB connection (requires `pymongo` installed and server running):
```bash
python -c \"import yaml; from pymongo import MongoClient; cfg=yaml.safe_load(open(\'config.yaml\')); client=MongoClient(cfg[\'MONGODB_URI\'], serverSelectionTimeoutMS=5000); client.admin.command(\'ping\'); print(\'MongoDB connection successful!\')\"
```
- Test Oracle connection (requires `oracledb` installed and DB accessible):
```bash
python -c \"import yaml; import oracledb; cfg=yaml.safe_load(open(\'config.yaml\')); dsn=oracledb.makedsn(cfg[\'ORACLE_HOST\'], cfg[\'ORACLE_PORT\'], service_name=cfg[\'ORACLE_SERVICE_NAME\']); conn=oracledb.connect(user=cfg[\'ORACLE_USERNAME\'], password=cfg[\'ORACLE_PASSWORD\'], dsn=dsn); print(\'Oracle connection successful! Version:\', conn.version); conn.close()\"
```

Now you are ready to run the application. See `readme.md` or the detailed Run section below.

## Running the Application (Development)

1. Ensure MongoDB server is running.
2. Ensure the `google-ai` Conda environment is active.
3. **Start Django Dashboard (Optional, Terminal 1):**
```bash
cd dashboard
python manage.py runserver
```
4. **Start Transcriber Service (Terminal 2):**
```bash
# Monitor mode
python main.py --monitor
# OR Single study mode
python main.py <SPECIFIC_STUDY_KEY>
```

## Building for Deployment (Optional)

1. **Install PyInstaller:**
Make sure PyInstaller is installed in your activated environment (`pip install pyinstaller`).

2. **Build Executable:**
Run PyInstaller using the provided spec file.
```bash
pyinstaller audio_transcriber.spec
```
The output will be in the `dist/audio_transcriber` directory.

3. **Prepare Deployment Package:**
- Copy the entire `dist/audio_transcriber` directory to the target server.
- **Crucially, copy the `config.yaml` file** into the *same directory* as `audio_transcriber.exe` on the target server.
- Ensure the target server has any necessary runtime dependencies (like Oracle Instant Client if not bundled, though `python-oracledb` often includes a thin client).

4. **Running the Built Executable:**
On the target server, open Command Prompt, navigate to the deployment directory, and run:
```bash
audio_transcriber.exe --monitor
# OR
audio_transcriber.exe <SPECIFIC_STUDY_KEY>
```
*(Note: The Django dashboard is **not** included in this build process and would need separate deployment if required in production, e.g., using Gunicorn/Nginx/Daphne).*

## Troubleshooting
- **`ModuleNotFoundError`:** Ensure the `google-ai` Conda environment is activated.
- **MongoDB Connection Errors:** Verify the MongoDB server is running and accessible. Check `MONGODB_URI` in `config.yaml`. Check firewalls.
- **Oracle Connection Errors:** Verify Oracle database accessibility. Check `ORACLE_*` settings in `config.yaml`. Ensure required Oracle client libraries are available if not using the thin client.
- **Network Share `FileNotFoundError`:** Verify `SHARE_USERNAME` and `SHARE_PASSWORD` in `config.yaml` are correct and the user has permission to access the share (`\\server\share`).
- **Django Errors:** Check the Django server logs for details. Ensure migrations (`python manage.py migrate`) have been run.
- **API Failures (e.g., Transcription):** Check API keys in `config.yaml`. Verify network connectivity to the API endpoint.

## Cross References
- [Architecture Overview](architecture.md)
- [Configuration Reference](config_reference.md)
- [Readme](../readme.md)
