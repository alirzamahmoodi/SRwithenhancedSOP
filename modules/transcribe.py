import traceback
import pydicom
import google.generativeai as genai
import google.api_core.exceptions as google_exceptions
import logging
from pydantic import BaseModel

class Transcription(BaseModel):
    Reading: str
    Conclusion: str

class Transcribe:
    def __init__(self, config):
        genai.configure(api_key=config["GEMINI_API_KEY"])
        self.model = genai.GenerativeModel(config["MODEL_NAME"])
        self.logger = logging.getLogger('detailed')

    def transcribe(self, dcm_path, audio_path):
        self.logger.info(f"Transcribing audio file: {audio_path} for DICOM file: {dcm_path}")

        try:
            # Read DICOM file
            self.logger.debug(f"Reading DICOM file: {dcm_path}")
            try:
                ds = pydicom.dcmread(dcm_path)
                self.logger.debug("DICOM file read successfully")
            except FileNotFoundError:
                self.logger.error(f"DICOM file not found: {dcm_path}")
                return None
            except pydicom.errors.InvalidDicomError:
                self.logger.error(f"Invalid DICOM file: {dcm_path}")
                return None
            except Exception as e:
                self.logger.error(f"Unexpected error while reading DICOM file: {str(e)}")
                self.logger.debug(traceback.format_exc())
                return None

            # Upload audio file to Gemini API
            self.logger.debug(f"Uploading audio file: {audio_path} to Gemini API")
            try:
                uploaded_file = genai.upload_file(audio_path)
                self.logger.debug(f"Audio file uploaded successfully: {uploaded_file}")
            except FileNotFoundError:
                self.logger.error(f"Audio file not found: {audio_path}")
                return None
            except google_exceptions.GoogleAPIError as e:
                self.logger.error(f"Google Cloud API error during file upload: {str(e)}")
                self.logger.debug(traceback.format_exc())
                return None
            except google_exceptions.ServiceUnavailable:
                self.logger.critical("Google Cloud service is unavailable. Check API status or internet connection.")
                return None
            except Exception as e:
                self.logger.error(f"Unexpected error while uploading audio: {str(e)}")
                self.logger.debug(traceback.format_exc())
                return None

            # Generate transcription
            prompt = f"""You are a medical transcription assistant. Transcribe the following medical dictation into a structured report in English. Follow these guidelines:

1. **Structure**: Organize the report into a JSON with two sections: The first section 'Reading' and the second section 'Conclusion'. The Reading section should include the transcription of the medical dictation, and the Conclusion section should summarize the key findings or diagnosis from 'Reading' Section.

2. **Language**: Ensure the entire report is in English, even if parts of the dictation are in Persian.

3. **Patient Information**: Crucially, Exclude and remove any private patient information (e.g., name, ) in the report. You are free to mention their age or history if needed.

4. **Tone**: Use a formal and professional tone suitable for a medical report. Write consistent paragraphs and avoid bullet points or lists.

5. **No Introductory Phrases**:  **Crucially, DO NOT include any introductory or conversational phrases at the beginning of the report.**  Specifically, **absolutely avoid phrases like "Here's a medical report dictation:", "Okay, here is the report:", or any similar preamble.**  The report should start immediately with the transcript.

6. **Accuracy**: Ensure the transcription is accurate and free of errors.

7. **Remove Conversations**: Remove any unnecessary data and conversations between physician and transcription operator.
"""
            self.logger.debug("Generating content with Gemini API")

            try:
                response = self.model.generate_content(
                    [uploaded_file, prompt],
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json",
                        response_schema=list[Transcription],
                        temperature=1,
                    )
                )
                report_content = response.text
                self.logger.info(f"Transcription completed for audio file: {audio_path}")
                self.logger.debug(f"Generated report content: {report_content}")
                return report_content
            except google_exceptions.Unauthenticated:
                self.logger.error("Google Cloud API authentication failed. Check your API key.")
            except google_exceptions.DeadlineExceeded:
                self.logger.error("Google Cloud API request timed out. Try again later.")
            except google_exceptions.ServiceUnavailable:
                self.logger.critical("Google Cloud API is temporarily unavailable. Retry later.")
            except google_exceptions.GoogleAPIError as e:
                self.logger.error(f"Google Cloud API error during transcription: {str(e)}")
                self.logger.debug(traceback.format_exc())
            except Exception as e:
                self.logger.error(f"Unexpected error while generating transcription: {str(e)}")
                self.logger.debug(traceback.format_exc())

        except Exception as e:
            self.logger.critical(f"Critical failure in transcription process: {str(e)}")
            self.logger.debug(traceback.format_exc())

        return None
