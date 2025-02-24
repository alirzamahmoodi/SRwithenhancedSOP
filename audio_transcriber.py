# audio_transcriber.py
import pydicom
import numpy as np
from scipy.io.wavfile import write
import google.generativeai as genai
import enum
import json
from typing_extensions import TypedDict
import os
import shutil
import pydicom.uid
from pydicom.dataset import Dataset, FileDataset
from datetime import datetime
import re

class Section(enum.Enum):
    HEADING = "heading"
    BODY = "body"

class ReportSection(TypedDict):
    section_type: Section
    content: str

class StructuredReport(TypedDict):
    PatientID: str
    PatientName: str
    PatientBirthDate: str
    StudyDate: str
    StudyTime: str
    Report: list[ReportSection]

class AudioTranscriber:
    def __init__(self, gemini_api_key):
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def extract_audio(self, dcm_path):
        ds = pydicom.dcmread(dcm_path)
        waveform = ds.WaveformSequence[0]
        audio_data = np.frombuffer(waveform.WaveformData, dtype=np.int16)
        wav_path = dcm_path.replace(".dcm", ".wav")
        write(wav_path, int(waveform.SamplingFrequency), audio_data)
        return wav_path

    def transcribe(self, dcm_path, audio_path):
        try:
            # Read DICOM file to extract patient and study information if needed
            ds = pydicom.dcmread(dcm_path)
            # Upload audio file to Gemini API
            uploaded_file = genai.upload_file(audio_path)
            prompt = f"""You are a medical transcription assistant. Transcribe the following medical dictation into a structured report in English. Follow these guidelines:

1. **Structure**: Organize the report into the following sections:
    - **Reading**: Detailed findings from the study.
    - **Conclusion**: Summary of the findings and their implications.
    - **Recommendation**: Suggested next steps or actions.

2. **Language**: Ensure the entire report is in English, even if parts of the dictation are in Persian.

3. **Patient Information**: Do not include any patient information (e.g., name, ID, birth date) in the report. This will be added separately.

4. **Tone**: Use a formal and professional tone suitable for a medical report. The report should be clear and professional.

5. **No Introductory Phrases**:  **Crucially, DO NOT include any introductory or conversational phrases at the beginning of the report.**  Specifically, **absolutely avoid phrases like "Here's a medical report dictation:", "Okay, here is the report:", or any similar preamble.**  The report should start immediately with the "Reading" section.

6. **Accuracy**: Ensure the transcription is accurate and free of errors.

7. **Formatting**: Use clear headings for each section and maintain proper formatting for readability.

8. **Repetition**: Omit any repeated words or phrases."""
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
            print(f"Transcription failed: {str(e)}")
            return None

    def encapsulate_text_as_enhanced_sr(self, report_text, original_dcm_path):
        ds = pydicom.dcmread(original_dcm_path)

        # **✅ File Meta Information**
        file_meta = Dataset()
        file_meta.MediaStorageSOPClassUID = pydicom.uid.UID("1.2.840.10008.5.1.4.1.1.88.22")  # Enhanced SR
        file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
        file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian

        # ✅ **Fix Missing File Meta Information Group Length**
        file_meta.FileMetaInformationGroupLength = 204

        # **Create SR Dataset**
        sr_filename = original_dcm_path.replace(".dcm", "_SR.dcm")
        sr_ds = FileDataset(sr_filename, {}, file_meta=file_meta, preamble=b"\0" * 128)

        # **Copy Patient & Study Info**
        sr_ds.PatientID = ds.PatientID
        sr_ds.PatientName = ds.PatientName
        sr_ds.PatientBirthDate = ds.get('PatientBirthDate', '')
        sr_ds.PatientSex = ds.get('PatientSex', 'U')
        sr_ds.StudyDate = ds.StudyDate
        sr_ds.StudyTime = ds.StudyTime
        sr_ds.StudyInstanceUID = ds.get('StudyInstanceUID', pydicom.uid.generate_uid())

        # **Required SR Attributes**
        sr_ds.SOPClassUID = file_meta.MediaStorageSOPClassUID
        sr_ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
        sr_ds.Modality = 'SR'
        sr_ds.ContentDate = datetime.now().strftime('%Y%m%d')
        sr_ds.ContentTime = datetime.now().strftime('%H%M%S')
        sr_ds.SeriesDescription = 'Transcription Report'
        sr_ds.SeriesInstanceUID = pydicom.uid.generate_uid()
        sr_ds.SeriesNumber = 1
        sr_ds.InstanceNumber = 1
        sr_ds.CompletionFlag = "COMPLETE"
        sr_ds.VerificationFlag = "UNVERIFIED"

        # **✅ Fix Instance Creation Date/Time**
        sr_ds.InstanceCreationDate = sr_ds.ContentDate  # Must be DA format
        sr_ds.InstanceCreationTime = sr_ds.ContentTime  # Must be TM format

        # **Fix: Properly Add Document Title**
        sr_ds.add_new((0x0040, 0xA043), 'SQ', [])  # Concept Name Code Sequence
        doc_title = Dataset()
        doc_title.CodeValue = "18748-4"  # LOINC code for a transcription report
        doc_title.CodingSchemeDesignator = "LN"
        doc_title.CodeMeaning = "Transcription Report"
        sr_ds[(0x0040, 0xA043)].value.append(doc_title)

        # **Revised Parsing and Structuring of the Transcription Content with Unified Style**
        import re

        # Define regex pattern to capture the three sections using groups.
        pattern = (
            r"(Reading:.*?)(?=(Conclusion:|Recommendation:|$))|"
            r"(Conclusion:.*?)(?=(Reading:|Recommendation:|$))|"
            r"(Recommendation:.*?)(?=(Reading:|Conclusion:|$))"
        )

        content_items = []
        # Use finditer for explicit iteration over matches.
        for match in re.finditer(pattern, report_text, re.DOTALL):
            # Extract the matched section text from the appropriate group.
            section_text = match.group(1) or match.group(3) or match.group(5)
            if section_text:
                # Extract the header and content.
                if ":" in section_text:
                    header, body = section_text.split(":", 1)
                    header = header.strip().upper()  # Normalize header in uppercase.
                    body = body.strip()
                else:
                    header = "UNKNOWN"
                    body = section_text.strip()

                # Determine the codes based on the section heading.
                if header.upper() == "READING":
                    code_value, code_meaning = "R-10226", "Reading"
                elif header.upper() == "CONCLUSION":
                    code_value, code_meaning = "R-10242", "Conclusion"
                elif header.upper() == "RECOMMENDATION":
                    code_value, code_meaning = "R-10266", "Recommendation"
                else:
                    code_value, code_meaning = "0000", "Unknown"

                # Assemble the formatted text.
                formatted_text = f"{header}:\n    {body}"

                # Create and populate the dataset for this section.
                item = Dataset()
                item.ValueType = "TEXT"
                concept_code = Dataset()
                concept_code.CodeValue = code_value
                concept_code.CodingSchemeDesignator = "DCM"
                concept_code.CodeMeaning = code_meaning
                item.ConceptNameCodeSequence = [concept_code]
                item.TextValue = formatted_text
                content_items.append(item)

        # Fallback if no sections were matched.
        if not content_items:
            formatted_text = f"READING:\n    {report_text.strip()}"
            item = Dataset()
            item.ValueType = "TEXT"
            concept_code = Dataset()
            concept_code.CodeValue = "R-10226"
            concept_code.CodingSchemeDesignator = "DCM"
            concept_code.CodeMeaning = "Reading"
            item.ConceptNameCodeSequence = [concept_code]
            item.TextValue = formatted_text
            content_items.append(item)

        # **✅ Fix: Ensure Root Container is Well-Formed**
        root_container = Dataset()
        root_container.ValueType = "CONTAINER"
        root_container.ContinuityOfContent = "SEPARATE"

        doc_title_sequence = Dataset()
        doc_title_sequence.CodeValue = "18748-4"
        doc_title_sequence.CodingSchemeDesignator = "LN"
        doc_title_sequence.CodeMeaning = "Test 2 Transcription Report"
        root_container.ConceptNameCodeSequence = [doc_title_sequence]

        # **Ensure ContentSequence Exists**
        root_container.ContentSequence = content_items

        # Assign root container to SR dataset
        sr_ds.ContentSequence = [root_container]

        # **✅ Ensure File Meta Information is Saved Properly**
        sr_ds.is_little_endian = True
        sr_ds.is_implicit_VR = False

        # Save file
        sr_ds.save_as(sr_filename, write_like_original=False)
        return sr_filename


    def process_spool_folder(self, spool_folder, processed_folder):
        for filename in os.listdir(spool_folder):
            if filename.endswith(".dcm") or '.' not in filename:
                dcm_path = os.path.join(spool_folder, filename)
                audio_path = self.extract_audio(dcm_path)
                report_text = self.transcribe(dcm_path, audio_path)
                if report_text:
                    sr_path = self.encapsulate_text_as_enhanced_sr(report_text, dcm_path)
                    print(f"Enhanced SR saved to: {sr_path}")
                    shutil.move(dcm_path, os.path.join(processed_folder, filename))

# End of file
