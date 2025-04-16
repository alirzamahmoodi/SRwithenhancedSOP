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
            prompt = f"""You are a highly accurate medical transcription AI. A dictation includeing mixed Persian language and English medical terms relevant to the medical content is provided. translate them accurately within the transcription and transcribe everything into English. Your task is to generate a JSON report containing two fields: 'Reading' and 'Conclusion'. The 'Reading' field should contain the accurate but fluent transcription of the provided audio dictation. The 'Conclusion' field should summarize the key findings or diagnosis based on the dictation.

Follow these instructions STRICTLY:

1.  **Output Format**: Produce a SINGLE JSON object containing exactly two keys: "Reading" and "Conclusion".
    * If using a list schema, the output list MUST contain only ONE such JSON object.
    * **Example Output:**
      ```json
      {{
        "Reading": "Almost verbatim transcription of the dictation goes here...",
        "Conclusion": "Summary of key findings or diagnosis based on the report goes here. If none, state something like 'No specific findings mentioned in the dictation.'"
      }}
      ```
2.  **Reading Section**: This section must contain an **accurate and fluent** transcription of the medical dictation. 
    *   Correct stutters, false starts, and unnecessary repetitions to create a readable report, but **do not change the medical meaning**.
    *   **Limit this section to approximately 6000 characters.**
3.  **Conclusion Section**: This section must ONLY summarize the essential medical findings or diagnosis stated EXPLICITLY in the 'Reading' section. If the 'Reading' contains no specific findings, the 'Conclusion' should state that (e.g., "No specific findings mentioned in the dictation."). **Limit this section to approximately 2000 characters.**
4.  **Language**: The dictation includes Persian terms relevant to the medical content, translate them accurately within the transcription and transcribe everything into English.
5.  **Patient Information**: Remove ALL private patient identifiers (like name, MRN, specific address). Age or general history can be retained if dictated.
6.  **Tone**: Maintain a formal, professional medical tone. Use complete sentences and paragraphs. Avoid lists or bullet points.
7.  **Crucially - Exclude Non-Dictation Content**:
    * Do NOT transcribe instructions to the transcriber, greetings, sign-offs (like "goodbye doctor"), background noise descriptions, or meta-comments about the recording process (e.g., "I need to check this file again").
    * Focus *exclusively* on the intended medical dictation content.
8.  **Crucially - No Introductory Phrases**: Your response MUST start IMMEDIATELY with the JSON object (`{{`). Do NOT include ANY preamble like "Here is the report:", "Okay:", etc.
9.  **Accuracy and Fluency**: Be precise with medical terms. Produce a fluent, readable transcription by correcting stutters and repetitions naturally, without altering the core medical information dictated. Trust the core dictation content.
"""
            self.logger.debug("Generating content with Gemini API")

            try:
                response = self.model.generate_content(
                    [uploaded_file, prompt],
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json"
                        # response_schema=Transcription
                    )
                )
                raw_json_response = response.text
                self.logger.info(f"Transcription completed for audio file: {audio_path}")
                # self.logger.debug(f"Raw response text was: {raw_json_response}") # Log raw before stripping if needed
                try:
                    # Strip leading/trailing whitespace (including newlines) before parsing
                    cleaned_json_response = raw_json_response.strip()
                    # Attempt to parse the JSON directly into a dictionary
                    transcription_dict = json.loads(cleaned_json_response)
                    self.logger.debug(f"Successfully parsed generated report content.")

                    # Validate the parsed dictionary
                    if isinstance(transcription_dict, dict):
                        # Check if the required keys exist
                        if "Reading" in transcription_dict and "Conclusion" in transcription_dict:
                             self.logger.debug("Parsed transcription dictionary successfully.")
                             # Optional: Validate against Pydantic model if strict conformance is needed
                             # try:
                             #     Transcription(**transcription_dict)
                             #     return transcription_dict
                             # except ValidationError as val_err:
                             #     self.logger.error(f"Parsed dictionary does not match Transcription model: {val_err}")
                             #     self.logger.debug(f"Parsed dictionary was: {transcription_dict}")
                             #     return None
                             return transcription_dict # Return the validated dictionary
                        else:
                            self.logger.error("Parsed dictionary is missing 'Reading' or 'Conclusion' key.")
                            self.logger.debug(f"Parsed dictionary was: {transcription_dict}")
                            return None
                    else:
                        self.logger.error(f"Expected a dictionary, but parsing yielded: {type(transcription_dict)}")
                        self.logger.debug(f"Parsed response was: {transcription_dict}")
                        return None

                except json.JSONDecodeError as json_err:
                    self.logger.error(f"Failed to parse JSON response from Gemini: {json_err}")
                    # self.logger.debug(f"Raw response text was: {report_content}") # Use new variable name
                    self.logger.debug(f"Raw response text was: {raw_json_response}")
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
