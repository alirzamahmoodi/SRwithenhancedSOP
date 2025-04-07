# Audio Extraction Module

## Purpose
Handles extraction of audio data from DICOM waveform sequences. Converts DICOM waveform data to standard WAV format for processing by subsequent transcription components.

## Class Overview
```python
class ExtractAudio:
    """
    <mcsymbol name="ExtractAudio" filename="extract_audio.py" path="e:\SRwithenhancedSOP\extract_audio.py" startline="7" type="class"></mcsymbol>
    Main processor for DICOM audio extraction
    
    Args:
        config (dict): Configuration dictionary from config.yaml
    """
```

## Main Method
```python
def extract_audio(self, dcm_path: str) -> str:
    """
    <mcsymbol name="ExtractAudio.extract_audio" filename="extract_audio.py" path="e:\SRwithenhancedSOP\extract_audio.py" startline="12" type="function"></mcsymbol>
    Core method that performs the audio extraction workflow
    
    Parameters:
        dcm_path (str): Full path to input DICOM file
    
    Returns:
        str: Path to generated WAV file
    
    Raises:
        FileNotFoundError: Missing input DICOM file
        InvalidDicomError: Corrupted/non-compliant DICOM
        AttributeError: Missing required DICOM fields
    """
```

## Key Functionality
1. **File Handling**
   - Windows long path support (>260 characters)
   - File existence verification
   - Retry logic for file access contention

2. **DICOM Processing**
   - Validates presence of `WaveformSequence`
   - Extracts `WaveformData` and `SamplingFrequency`
   - Converts raw data to numpy array

3. **Output Generation**
   - Creates WAV file in same directory as input
   - Maintains original audio fidelity
   - Handles byte ordering and data formatting

## Configuration Requirements
```yaml
# From <mcfile name="config.yaml" path="e:\SRwithenhancedSOP\config.yaml"></mcfile>
storage:
  paths:
    dicom_input: "/path/to/dicom"  # Source directory for DICOM files

logging:
  level: "INFO"  # Controls verbosity of extraction logs
```

## Error Handling
| Error Type               | Cause                           | Resolution                     |
|--------------------------|----------------------------------|--------------------------------|
| `FileNotFoundError`      | Missing DICOM file              | Verify file path in PACS       |
| `InvalidDicomError`       | Corrupted DICOM data            | Validate DICOM compliance      |
| `AttributeError`         | Missing waveform data           | Check modality type (must be SR)|

## Dependencies
```text
- pydicom: DICOM file parsing
- numpy: Audio data manipulation
- scipy: WAV file generation
```

## Usage Example
```python
from extract_audio import ExtractAudio

processor = ExtractAudio(config=app_config)
wav_path = processor.extract_audio("input.dcm")
```

## Related Documents
- [System Workflow](high_level/workflow.md)
- [DICOM Processing Guide](modules/main.md)
- [Configuration Reference](high_level/config_reference.md)
```
