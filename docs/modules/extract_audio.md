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
    *   `FileNotFoundError`: If the input `dcm_path` does not exist.
    *   `pydicom.errors.InvalidDicomError`: If the file is not a valid DICOM file.
    *   `AttributeError`: If required DICOM tags (like `WaveformSequence`, `WaveformData`, `SamplingFrequency`) are missing.
    *   `PermissionError`, `OSError`: If file access fails after retries.
    *   Other file I/O errors during WAV writing.
*   **Workflow:**
    1.  Checks if `dcm_path` exists.
    2.  Applies Windows long path prefix if necessary.
    3.  Attempts to read the DICOM file at `dcm_path` using `pydicom.dcmread()`, with a retry mechanism for transient access errors (`PermissionError`, `OSError`).
    4.  Validates the presence and extracts data from necessary tags (`WaveformSequence`, `WaveformData`, `SamplingFrequency`).
    5.  Determines the audio data type (e.g., `np.int16`, `np.uint8`) based on `WaveformBitsAllocated`, logging warnings for unsupported values.
    6.  Converts the raw `WaveformData` into a NumPy array using the determined data type.
    7.  Logs a warning if `NumberOfChannels` is not 1.
    8.  Generates an output WAV filename by replacing the `.dcm` extension with `.wav` in the original `dcm_path`.
    9.  Writes the audio data to the WAV file using `scipy.io.wavfile.write` with the extracted sampling frequency.
    10. Returns the path to the created WAV file.

## Key Functionality

*   **DICOM Parsing:** Reads and interprets DICOM file structure using `pydicom`.
*   **Waveform Extraction:** Specifically targets and extracts embedded audio waveform data.
*   **WAV Conversion:** Converts the raw DICOM audio data into a standard WAV format.
*   **File Access:** Requires read access to the input DICOM file path and write access to create the temporary WAV file.

## Dependencies

*   `pydicom`: For reading DICOM files.
*   `numpy`: For numerical manipulation of audio data.
*   `scipy.io.wavfile`: For writing WAV files.
*   `os`: For path manipulation and existence checks.
*   `time`: Used for delays in the file read retry loop.
*   `logging`: For logging progress and errors.

## Integration

*   Called by `main.py` within the `run_pipeline` function after the path is obtained from `query.py` and potentially after authentication via `smb_connect.py`.
*   The returned WAV file path is passed to the `transcribe.py` module.

## Related Documents
- [System Architecture](../high_level/architecture.md)
- [Main Workflow](main.md)
