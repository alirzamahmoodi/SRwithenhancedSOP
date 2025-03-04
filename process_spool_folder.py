import os
import shutil
import logging
from extract_audio import ExtractAudio
from transcribe import Transcribe
from encapsulate_text_as_enhanced_sr import EncapsulateTextAsEnhancedSR

class ProcessSpoolFolder:
    def __init__(self, config):
        self.config = config
        self.extract_audio = ExtractAudio(config)
        self.transcribe = Transcribe(config)
        self.encapsulate_text_as_enhanced_sr = EncapsulateTextAsEnhancedSR(config)

    def process_spool_folder(self, spool_folder, processed_folder):
        for filename in os.listdir(spool_folder):
            file_path = os.path.join(spool_folder, filename)
            if os.path.isfile(file_path) and (filename.endswith(".dcm") or '.' not in filename):
                dcm_path = file_path
                audio_path = self.extract_audio.extract_audio(dcm_path)
                report_text = self.transcribe.transcribe(dcm_path, audio_path)
                if report_text:
                    sr_path = self.encapsulate_text_as_enhanced_sr.encapsulate_text_as_enhanced_sr(report_text, dcm_path)
                    logging.info(f"Enhanced SR saved to: {sr_path}")
                    shutil.move(dcm_path, os.path.join(processed_folder, filename))
                else:
                    logging.warning(f"No transcription was generated for {filename}")
