# Audio Extraction Module (`extract_audio.py`)

## Purpose

Handles the extraction of audio data from DICOM files, specifically targeting waveform sequences. It reads the DICOM file, extracts relevant audio metadata and waveform data, and converts/saves it as a standard WAV audio file for processing by the transcription module.

## Class: `ExtractAudio`

*   Encapsulates the logic for audio extraction.
*   Initialized with the application `config` dictionary (though it may not use any specific config values directly).

## Main Method: `extract_audio(self, dcm_path)`

*   **Purpose:** Performs the audio extraction workflow.
*   **Parameters:**
    *   `dcm_path` (str): Full path to the input DICOM file. This path should already be validated or accessible (e.g., via prior authentication using `smb_connect` if it's a UNC path).
*   **Returns:**
    *   `str`: Path to the temporary WAV file generated.
*   **Raises:**
    *   `FileNotFoundError`: If the input `dcm_path` does not exist or is inaccessible (could indicate an issue with the path itself or underlying permissions/authentication if `smb_connect` failed silently or wasn't needed/used).
    *   `pydicom.errors.InvalidDicomError`: If the file is not a valid DICOM file.
    *   `AttributeError` / `KeyError`: If required DICOM tags (like `WaveformSequence`, `WaveformData`, `ChannelSampleRate`) are missing.
    *   Other file I/O errors.
*   **Workflow:**
    1.  Attempts to read the DICOM file at `dcm_path` using `pydicom.dcmread()`.
    2.  Validates the presence and extracts data from necessary tags (e.g., `WaveformSequence`, `WaveformData`, `ChannelSampleRate`).
    3.  Converts the raw `WaveformData` into a suitable format (e.g., NumPy array).
    4.  Generates a temporary WAV filename (often based on the input filename or study key).
    5.  Writes the audio data to the temporary WAV file using appropriate libraries (e.g., `scipy.io.wavfile.write`).
    6.  Returns the path to the created WAV file.

## Key Functionality

*   **DICOM Parsing:** Reads and interprets DICOM file structure using `pydicom`.
*   **Waveform Extraction:** Specifically targets and extracts embedded audio waveform data.
*   **WAV Conversion:** Converts the raw DICOM audio data into a standard WAV format.
*   **File Access:** Requires read access to the input DICOM file path and write access to create the temporary WAV file.

## Dependencies

*   `pydicom`: For reading DICOM files.
*   `numpy`: For numerical manipulation of audio data.
*   `scipy`: (Likely `scipy.io.wavfile`) For writing WAV files.
*   `os`, `tempfile`: For path manipulation and temporary file creation.
*   `logging`: For logging progress and errors.

## Integration

*   Called by `main.py` within the `run_pipeline` function after the path is obtained from `query.py` and potentially after authentication via `smb_connect.py`.
*   The returned WAV file path is passed to the `transcribe.py` module.

## Related Documents
- [System Architecture](../high_level/architecture.md)
- [Main Workflow](main.md)
