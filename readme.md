# Build Instructions

1. Create the conda environment:
    ```bash
    conda env create -f environment.yml
    ```
2. Activate the environment:
    ```bash
    conda activate google-ai
    ```
3. Install `pyinstaller`:
    ```bash
    pip install pyinstaller
    ```
4. Build the project using:
    ```bash
    pyinstaller audio_transcriber.spec
    ```

# Run Instructions

1. Move the `config.yaml` file from:
    ```
    dist/audio_transcriber/_internal
    ```
    to:
    ```
    dist/audio_transcriber/
    ```

2. Edit the `config.yaml` file according to your use case.

3. Set up **DICOM Receiver** and **DICOM Register** services for dictation and structured report processing.

4. Open **Command Prompt** in the `dist/audio_transcriber/` directory and run:
    ```bash
    audio_transcriber.exe
    ```

5. The service will be up and running, listening for dictation `.dcm` files in the **spool folder**.
