# Module: Encapsulate Text as Enhanced SR (`encapsulate_text_as_enhanced_sr.py`)

## Overview

This module is responsible for taking the transcribed text report and embedding it within a new DICOM Enhanced Structured Report (SR) object. It aims to create a DICOM-compliant SR file that includes the transcription, potentially alongside relevant metadata from the original study.

**Note:** The execution of this module is optional and controlled by the `ENCAPSULATE_TEXT_AS_ENHANCED_SR` setting in `config.yaml`.

## Key Features (Intended)

*   **DICOM SR Generation:** Creates SR objects conforming to relevant DICOM standards (e.g., TID 2000 Basic Text SR).
*   **Metadata Preservation:** Aims to copy necessary identifying information (Patient ID, Study UID, etc.) from the original study into the new SR object.
*   **Text Embedding:** Inserts the transcribed report text into the appropriate content items within the SR structure.

## Implementation Steps

The `encapsulate_text_as_enhanced_sr` method performs the following:

1.  **Read Original DICOM:** Reads the DICOM file specified by `original_dcm_path` using `pydicom`.
2.  **Prepare File Meta:** Creates a `Dataset` for file meta information, setting `MediaStorageSOPClassUID` to Enhanced SR (1.2.840.10008.5.1.4.1.1.88.22) and `TransferSyntaxUID`.
3.  **Create SR Dataset:** Initializes a `FileDataset` for the new SR, setting the output filename based on the original name and the `SR_OUTPUT_FOLDER` from the configuration.
4.  **Copy Metadata:** Copies essential patient and study information (PatientID, StudyInstanceUID, etc.) from the original dataset, with basic defaults for missing tags.
5.  **Set SR Attributes:** Populates required SR attributes like `SOPClassUID`, `SOPInstanceUID`, `Modality`, `ContentDate`, `ContentTime`, `SeriesDescription`, `SeriesInstanceUID`, `CompletionFlag`, `VerificationFlag`, and manufacturer details (potentially read from config).
6.  **Set Document Title:** Adds a `ConceptNameCodeSequence` to the SR dataset indicating the document type (e.g., LOINC "Diagnostic imaging report").
7.  **Build Content Sequence:** 
    *   Iterates through the input `report_list` (expected to be a list of dicts, e.g., `[{"finding": "..."}, {"impression": "..."}]`).
    *   For each key-value pair, creates a `TEXT` content item.
    *   Sets the `ConceptNameCodeSequence` for the item based on the key (using DCM codes for "finding" and "impression", or a generic code otherwise).
    *   Sets the `TextValue` to the report section's text.
8.  **Create Root Container:** Creates a `CONTAINER` content item to hold all the text items.
9.  **Assign Content:** Assigns the list of text items to the container's `ContentSequence`, and assigns the container to the main SR dataset's `ContentSequence`.
10. **Save SR File:** Sets endianness and VR, then saves the SR dataset to the designated path using `sr_ds.save_as()`.
11. **Return Path:** Returns the full path to the newly created SR file, or `None` if an error occurred.

## Configuration (`config.yaml`)

```yaml
# ----------------- Core Service Operation -----------------
ENCAPSULATE_TEXT_AS_ENHANCED_SR: "OFF" # Set to "ON" to enable SR generation

# ----------------- SR Generation Specific -----------------
# Required if ENCAPSULATE_TEXT_AS_ENHANCED_SR is "ON"
SR_OUTPUT_FOLDER: "C:/RaoufSoft/Spool/101" # Path to save generated SR files

# Optional: Manufacturer details for the generated SR
# SR_MANUFACTURER: "YourOrg/ProjectName"
# SR_MODEL_NAME: "AI Transcription SR Generator"
# SR_SOFTWARE_VERSION: "1.0.0"
```

## Dependencies

*   `pydicom`: For all DICOM reading, manipulation, and writing.
*   `os`: For path manipulation.
*   `datetime`: For generating timestamps.
*   `logging`: For logging progress and errors.

## Integration

*   Called optionally within `main.py`'s `run_pipeline` function *after* successful transcription and *before* optional legacy storage.
*   Receives the `report_list` (transcribed text) and `final_path` (path to the original DICOM) as input.
*   The path to the generated SR file (`sr_path`) is returned and potentially saved to the MongoDB `transcriptions` record via `database_operations.save_transcription`.

[Back to Module Index](main.md)