# Documentation Structure

e:\SRwithenhancedSOP\docs\
├── high_level/
│   ├── architecture.md
│   ├── installation.md
│   └── config_reference.md
├── modules/
│   ├── main.md
│   ├── query.md
│   ├── extract_audio.md
│   ├── transcribe.md
│   └── store_transcribed_report.md

# Build Instructions

1. **Create the Conda Environment:**
   ```bash
   conda env create -f environment.yml
   ```
2. **Activate the Environment:**
   ```bash
   conda activate google-ai
   ```
3. **Install PyInstaller:**
   ```bash
   pip install pyinstaller
   ```
4. **Build the Project:**
   ```bash
   pyinstaller audio_transcriber.spec
   ```

# Run Instructions

1. **Move the `config.yaml` File:**
   - After building, move the `config.yaml` file from:
     ```
     dist/audio_transcriber/_internal
     ```
     to:
     ```
     dist/
     ```
   This ensures that `config.yaml` is in the same folder as `audio_transcriber.exe`.

2. **Edit the `config.yaml` File:**
   - Update the file according to your use case (e.g., set paths, database credentials, and other configuration options).

3. **Set Up DICOM Receiver and Register Services:**
   - Configure your **DICOM Receiver** and **DICOM Register** services as needed for dictation and structured report processing.

4. **Run the Application in Monitor Mode:**
   - Open **Command Prompt** in the `dist` directory and run:
     ```bash
     audio_transcriber.exe --monitor
     ```
   - This command starts the process in monitor mode, and the console will display logs, showing that the service is up and running while it listens for dictated studies.

--- 

