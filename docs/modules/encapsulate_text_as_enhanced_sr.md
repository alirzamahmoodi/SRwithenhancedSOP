# Module: Encapsulate Text as Enhanced SR (`encapsulate_text_as_enhanced_sr.py`)

## Overview

This module is responsible for taking the transcribed text report and embedding it within a new DICOM Enhanced Structured Report (SR) object. It aims to create a DICOM-compliant SR file that includes the transcription, potentially alongside relevant metadata from the original study.

**Note:** The execution of this module is optional and controlled by the `ENCAPSULATE_TEXT_AS_ENHANCED_SR` setting in `config.yaml`.

## Key Features (Intended)

*   **DICOM SR Generation:** Creates SR objects conforming to relevant DICOM standards (e.g., TID 2000 Basic Text SR).
*   **Metadata Preservation:** Aims to copy necessary identifying information (Patient ID, Study UID, etc.) from the original study into the new SR object.
*   **Text Embedding:** Inserts the transcribed report text into the appropriate content items within the SR structure.

## Class / Function (Assumed Structure)

*(Based on common patterns, actual implementation may vary)*

```python
class EncapsulateTextAsEnhancedSR:
    def __init__(self, config):
        # Store config, potentially load SR templates
        pass

    def encapsulate_text_as_enhanced_sr(self, report_list, original_dcm_path):
        # 1. Read metadata from original_dcm_path using pydicom
        # 2. Create a new pydicom Dataset for the SR
        # 3. Populate required SR metadata (SOP Class UID, UIDs, Patient/Study info)
        # 4. Create the SR document content sequence
        # 5. Add content items for the transcribed text (report_list)
        # 6. Define output path (e.g., using config['SR_OUTPUT_FOLDER'])
        # 7. Save the new SR dataset as a DICOM file
        # 8. Return the path to the saved SR file
        pass
```

## Configuration (`config.yaml`)

```yaml
# ----------------- Core Service Operation -----------------
ENCAPSULATE_TEXT_AS_ENHANCED_SR: "OFF" # Set to "ON" to enable SR generation
# Optional: Specify where generated SR files should be saved
# SR_OUTPUT_FOLDER: "C:/path/to/save/sr_files"
```

## Dependencies (Likely)

*   `pydicom`: For reading the original DICOM metadata and creating/writing the new SR DICOM file.
*   `os`: For path manipulation.
*   `uuid`, `datetime`: For generating new UIDs and timestamps for the SR object.
*   `logging`: For logging progress and errors.

## Integration

*   Called optionally within `main.py`'s `run_pipeline` function *after* successful transcription and *before* optional legacy storage.
*   Receives the `report_list` (transcribed text) and `final_path` (path to the original DICOM) as input.
*   The path to the generated SR file (`sr_path`) is returned and potentially saved to the MongoDB `transcriptions` record via `database_operations.save_transcription`.

[Back to Module Index](main.md)