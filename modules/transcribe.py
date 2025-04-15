import traceback
import pydicom
import google.generativeai as genai
import google.api_core.exceptions as google_exceptions
import logging
from pydantic import BaseModel
import json

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
            prompt = f"""You are a highly accurate medical transcription AI. Your FIRST task is to transcribe the provided audio dictation verbatim into the 'Reading' section of a JSON report. Then, the second task is to summarize the key findings or diagnosis in the 'Conclusion' section, based *only* on the transcribed text in 'Reading'

Follow these instructions STRICTLY:

1.  **Output Format**: Produce a SINGLE JSON object containing exactly two keys: "Reading" and "Conclusion".
    * If using a list schema, the output list MUST contain only ONE such JSON object.
2.  **Reading Section**: This section must contain ONLY the accurate, word-for-word transcription of the medical dictation from the audio. **Limit this section to approximately 6000 characters.**
3.  **Conclusion Section**: This section must ONLY summarize the essential medical findings or diagnosis stated EXPLICITLY in the 'Reading' section. If the 'Reading' contains no specific findings, the 'Conclusion' should state that (e.g., "No specific findings mentioned in the dictation."). **Limit this section to approximately 2000 characters.**
4.  **Language**: Transcribe everything into English. If the dictation includes Persian terms relevant to the medical content, translate them accurately within the transcription.
5.  **Patient Information**: Remove ALL private patient identifiers (like name, MRN, specific address). Age or general history can be retained if dictated.
6.  **Tone**: Maintain a formal, professional medical tone. Use complete sentences and paragraphs. Avoid lists or bullet points.
7.  **Crucially - Exclude Non-Dictation Content**:
    * Do NOT transcribe instructions to the transcriber, greetings, sign-offs (like "goodbye doctor"), background noise descriptions, or meta-comments about the recording process (e.g., "I need to check this file again").
    * Focus *exclusively* on the intended medical dictation content.
8.  **Crucially - No Introductory Phrases**: Your response MUST start IMMEDIATELY with the JSON object (`{{`). Do NOT include ANY preamble like "Here is the report:", "Okay:", etc.
9.  **Accuracy and Verbatim Transcription**: Be precise. Transcribe *exactly* what is dictated for the medical report. Trust the dictation provided.
"""
            self.logger.debug("Generating content with Gemini API")

            try:
                response = self.model.generate_content(
                    [uploaded_file, prompt],
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json",
                        response_schema=list[Transcription],
                    )
                )
                report_content = response.text
                self.logger.info(f"Transcription completed for audio file: {audio_path}")
                # self.logger.debug(f"Generated report content: {report_content}") # Commented out to avoid UnicodeEncodeError
                try:
                    # Attempt to parse the JSON immediately to return a Python object
                    parsed_report = json.loads(report_content)
                    self.logger.debug(f"Successfully parsed generated report content.")
                    return parsed_report
                except json.JSONDecodeError as json_err:
                    self.logger.error(f"Failed to parse JSON response from Gemini: {json_err}")
                    self.logger.debug(f"Raw response text was: {report_content}")
                    return None # Return None if JSON parsing fails

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
