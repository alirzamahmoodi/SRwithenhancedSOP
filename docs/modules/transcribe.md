# Speech-to-Text Transcription Module

## Purpose
Converts extracted audio into structured medical reports using Google's Gemini AI. Ensures HIPAA-compliant processing and produces DICOM-compatible structured results.

## Class Overview
```python
class Transcribe:
    """
    <mcsymbol name="Transcribe" filename="transcribe.py" path="e:\SRwithenhancedSOP\transcribe.py" startline="10" type="class"></mcsymbol>
    Core processor for medical audio transcription
    
    Args:
        config (dict): Configuration containing API credentials
    """
```

## Main Method
```python
def transcribe(self, dcm_path: str, audio_path: str) -> str:
    """
    <mcsymbol name="Transcribe.transcribe" filename="transcribe.py" path="e:\SRwithenhancedSOP\transcribe.py" startline="18" type="function"></mcsymbol>
    Executes full transcription pipeline
    
    Parameters:
        dcm_path (str): Source DICOM file path (for metadata validation)
        audio_path (str): Extracted WAV audio file path
    
    Returns:
        str: JSON-formatted report with 'Reading' and 'Conclusion' sections
    
    Raises:
        GoogleAPIError: Cloud service communication failures
        InvalidDicomError: Metadata validation failures
    """
```

## Key Functionality
1. **AI Integration**
   - Secure API credential management
   - Audio file upload to Gemini Cloud
   - Structured JSON response parsing

2. **Medical Report Structure**
   - Pydantic model validation
   - Automatic section separation (Findings/Conclusion)
   - PHI redaction

3. **Error Resilience**
   - Exponential backoff for network errors
   - Service availability monitoring
   - Detailed error logging

## Configuration Requirements
```yaml
# From <mcfile name="config.yaml" path="e:\SRwithenhancedSOP\config.yaml"></mcfile>
ai:
  gemini_api_key: "your-api-key"  # Google Cloud credentials
  model_name: "gemini-2.0-flash"       # AI model version
  temperature: 1.0               # Creativity vs accuracy
```

## Error Handling Matrix
| Error Type               | Frequency | Severity | Recovery Strategy          |
|--------------------------|-----------|----------|-----------------------------|
| `Unauthenticated`        | Low       | Critical | Validate API key rotation   |
| `DeadlineExceeded`       | Medium    | High     | Retry with backoff          |
| `ServiceUnavailable`     | Medium    | High     | Circuit breaker pattern     |
| `InvalidDicomError`      | High      | Medium   | Validate input DICOMs       |

## Dependencies
```text
- google-generativeai: Cloud AI access
- pydicom: Metadata validation
- pydantic: Response structure enforcement
```

## Usage Example
```python
from transcribe import Transcribe

transcriber = Transcribe(config=app_config)
report = transcriber.transcribe("dictation_audio_file.dcm", "audio.wav")
```

## Related Documents
- [AI Configuration Guide](high_level/config_reference.md)
- [Workflow Diagram](high_level/architecture.md)
- [Audio Extraction Docs](modules/extract_audio.md)
```