import pydicom
from pydicom.dataset import Dataset, FileDataset
from datetime import datetime
import os

class EncapsulateTextAsEnhancedSR:
    def __init__(self, config):
        self.sr_output_folder = config["SR_OUTPUT_FOLDER"]

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
        basename = os.path.basename(original_dcm_path).replace(".dcm", "_SR.dcm")
        sr_filename = os.path.join(self.sr_output_folder, basename)
        os.makedirs(self.sr_output_folder, exist_ok=True)
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
        sr_ds.SeriesDescription = 'Dictation Transcription'
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
        doc_title.CodeMeaning = "AI-Generated Dictation Transcription"
        sr_ds[(0x0040, 0xA043)].value.append(doc_title)

        # **Fix: Correctly Parse and Structure the Report**
        content_items = []

        item = Dataset()
        item.ValueType = "TEXT"
        concept_code = Dataset()
        concept_code.CodeValue = "R-10226"
        concept_code.CodingSchemeDesignator = "DCM"
        concept_code.CodeMeaning = "Reading"
        item.ConceptNameCodeSequence = [concept_code]
        item.TextValue = report_text.strip()
        content_items.append(item)

        # **✅ Fix: Ensure Root Container is Well-Formed**
        root_container = Dataset()
        root_container.ValueType = "CONTAINER"
        root_container.ContinuityOfContent = "SEPARATE"

        doc_title_sequence = Dataset()
        doc_title_sequence.CodeValue = "18748-4"
        doc_title_sequence.CodingSchemeDesignator = "LN"
        doc_title_sequence.CodeMeaning = " "
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
