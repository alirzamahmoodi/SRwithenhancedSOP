import pydicom
import google.generativeai as genai
import logging

class Transcribe:
    def __init__(self, config):
        genai.configure(api_key=config["GEMINI_API_KEY"])
        self.model = genai.GenerativeModel(config["MODEL_NAME"])

    def transcribe(self, dcm_path, audio_path):
        try:
            # Read DICOM file to extract patient and study information if needed
            ds = pydicom.dcmread(dcm_path)
            # Upload audio file to Gemini API
            uploaded_file = genai.upload_file(audio_path)
            prompt = f"""You are a medical transcription assistant. Transcribe the following medical dictation into a structured report in English. Follow these guidelines:

1. **Structure**: Organize the report into ONE paragraph of sentences of plain text.

2. **Language**: Ensure the entire report is in English, even if parts of the dictation are in Persian.

3. **Patient Information**: Crucially, Exclude and remove any private patient information (e.g., name, ) in the report, but you are free to mention their age or history.

4. **Tone**: Use a formal and professional tone suitable for a medical report. Write consistent paragraphs and avoid bullet points or lists.

5. **No Introductory Phrases**:  **Crucially, DO NOT include any introductory or conversational phrases at the beginning of the report.**  Specifically, **absolutely avoid phrases like "Here's a medical report dictation:", "Okay, here is the report:", or any similar preamble.**  The report should start immediately with the transcript.

6. **Accuracy**: Ensure the transcription is accurate and free of errors.

7. **Repetition**: Omit any repeated words or phrases and remove any unnecessary data and conversations between physician and transcription operator.
"""
            response = self.model.generate_content(
                [uploaded_file, prompt],
                generation_config=genai.GenerationConfig(
                    response_mime_type="text/plain",
                    temperature=1,
                )
            )
            report_content = response.text.strip()
            return report_content
        except Exception as e:
            logging.error(f"Transcription failed: {str(e)}")
            return None
