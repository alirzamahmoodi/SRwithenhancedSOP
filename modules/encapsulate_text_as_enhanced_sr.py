import pydicom
from pydicom.dataset import Dataset, FileDataset
from datetime import datetime
import os
import logging
import traceback

class EncapsulateTextAsEnhancedSR:
    def __init__(self, config):
        self.config = config
        self.sr_output_folder = config["SR_OUTPUT_FOLDER"]
        self.logger = logging.getLogger('detailed')

    def encapsulate_text_as_enhanced_sr(self, report_list, original_dcm_path):
        self.logger.info(f"Attempting to encapsulate text as Enhanced SR for DICOM file: {original_dcm_path}")
        try:
            ds = pydicom.dcmread(original_dcm_path)
        except Exception as e:
            self.logger.error(f"Failed to read original DICOM file {original_dcm_path}: {e}")
            return None

        # **✅ File Meta Information**
        file_meta = Dataset()
        file_meta.MediaStorageSOPClassUID = pydicom.uid.UID("1.2.840.10008.5.1.4.1.1.88.22")  # Enhanced SR
        file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
        file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian
        # Let pydicom calculate this on save, or set explicitly if needed
        # file_meta.FileMetaInformationGroupLength = 204 # Often calculated automatically

        # **Create SR Dataset**
        basename = os.path.basename(original_dcm_path).replace(".dcm", "_SR.dcm")
        sr_filename = os.path.join(self.sr_output_folder, basename)
        try:
            os.makedirs(self.sr_output_folder, exist_ok=True)
        except OSError as e:
            self.logger.error(f"Failed to create output directory {self.sr_output_folder}: {e}")
            return None

        sr_ds = FileDataset(sr_filename, {}, file_meta=file_meta, preamble=b"\0" * 128)

        # **Copy Patient & Study Info**
        # Add error handling/defaults for missing tags
        sr_ds.PatientID = ds.get('PatientID', 'Unknown')
        sr_ds.PatientName = ds.get('PatientName', 'Unknown')
        sr_ds.PatientBirthDate = ds.get('PatientBirthDate', '')
        sr_ds.PatientSex = ds.get('PatientSex', 'O') # Use 'O' for Other if unknown
        sr_ds.StudyDate = ds.get('StudyDate', datetime.now().strftime('%Y%m%d'))
        sr_ds.StudyTime = ds.get('StudyTime', datetime.now().strftime('%H%M%S'))
        sr_ds.StudyInstanceUID = ds.get('StudyInstanceUID', pydicom.uid.generate_uid())
        sr_ds.AccessionNumber = ds.get('AccessionNumber', '') # Often useful

        # **Required SR Attributes**
        # Set Specific Character Set in main dataset (matches file meta)
        # sr_ds.SpecificCharacterSet = 'ISO_IR 100' # Old Latin-1
        sr_ds.SOPClassUID = file_meta.MediaStorageSOPClassUID
        sr_ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
        sr_ds.Modality = 'SR'
        sr_ds.ContentDate = datetime.now().strftime('%Y%m%d')
        sr_ds.ContentTime = datetime.now().strftime('%H%M%S.%f')[:16] # Include fractional seconds
        sr_ds.SeriesDescription = 'AI Dictation Transcription SR' # More specific description
        sr_ds.SeriesInstanceUID = pydicom.uid.generate_uid()
        sr_ds.SeriesNumber = 99 # Assign a distinct series number
        sr_ds.InstanceNumber = 1
        sr_ds.CompletionFlag = "COMPLETE"
        sr_ds.VerificationFlag = "UNVERIFIED"
        sr_ds.InstanceCreationDate = sr_ds.ContentDate
        sr_ds.InstanceCreationTime = sr_ds.ContentTime

        # Add Manufacturer Information
        sr_ds.Manufacturer = self.config.get('SR_MANUFACTURER', 'YourOrg/ProjectName')
        sr_ds.ManufacturerModelName = self.config.get('SR_MODEL_NAME', 'AI Transcription SR Generator')
        sr_ds.SoftwareVersions = self.config.get('SR_SOFTWARE_VERSION', '1.0.0')

        # **Top-level Document Title**
        sr_ds.ConceptNameCodeSequence = [] # Initialize if not present
        doc_title = Dataset()
        doc_title.CodeValue = "18748-4"  # LOINC code for Diagnostic imaging report
        doc_title.CodingSchemeDesignator = "LN"
        doc_title.CodeMeaning = "AI-Generated Dictation Transcription Report"
        sr_ds.ConceptNameCodeSequence.append(doc_title)

        # **Build Content Sequence from report_list**
        content_items = []
        if not isinstance(report_list, list):
            self.logger.error(f"Expected report_list to be a list, but got {type(report_list)}")
            return None

        for section in report_list:
            if not isinstance(section, dict):
                self.logger.warning(f"Skipping non-dict item in report_list: {section}")
                continue

            for key, value in section.items():
                item = Dataset()
                item.ValueType = "TEXT"
                item.RelationshipType = "CONTAINS" # Relationship to parent container

                concept_code = Dataset()
                if key.lower() == "reading":
                    concept_code.CodeValue = "111027" # Finding
                    concept_code.CodingSchemeDesignator = "DCM"
                    concept_code.CodeMeaning = "Finding"
                elif key.lower() == "conclusion":
                    concept_code.CodeValue = "111030" # Impression
                    concept_code.CodingSchemeDesignator = "DCM"
                    concept_code.CodeMeaning = "Impression"
                else:
                    self.logger.warning(f"Unknown section key '{key}' in report_list. Using generic concept.")
                    concept_code.CodeValue = "121071" # Observation Context
                    concept_code.CodingSchemeDesignator = "DCM"
                    concept_code.CodeMeaning = key # Use the key as meaning

                item.ConceptNameCodeSequence = [concept_code]
                item.TextValue = str(value).strip() # Ensure value is string
                content_items.append(item)

        if not content_items:
            self.logger.error("No valid content items generated from report_list.")
            return None

        # **Create Root Container**
        root_container = Dataset()
        root_container.ValueType = "CONTAINER"
        root_container.ContinuityOfContent = "SEPARATE"
        root_container.RelationshipType = "CONTAINS" # Root container relationship

        # Container Concept Name (e.g., the type of report it contains)
        container_concept = Dataset()
        container_concept.CodeValue = "111058" # Report
        container_concept.CodingSchemeDesignator = "DCM"
        container_concept.CodeMeaning = "Report"
        root_container.ConceptNameCodeSequence = [container_concept]

        # Assign generated content items to the container's sequence
        root_container.ContentSequence = content_items

        # Assign root container to the main dataset's ContentSequence
        sr_ds.ContentSequence = [root_container]

        # **Ensure Correct Endianness and VR**
        sr_ds.is_little_endian = True
        sr_ds.is_implicit_VR = False

        # Save file
        try:
            # Explicitly use Little Endian Explicit VR
            sr_ds.save_as(sr_filename, write_like_original=False)
            self.logger.info(f"Enhanced SR saved successfully to: {sr_filename}")
            return sr_filename
        except Exception as e:
            self.logger.error(f"Failed to save Enhanced SR file {sr_filename}: {e}")
            self.logger.debug(traceback.format_exc())
            return None
