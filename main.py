import sys
import argparse
import yaml
import logging
from query import process_study_key
from extract_audio import ExtractAudio
from transcribe import Transcribe
from encapsulate_text_as_enhanced_sr import EncapsulateTextAsEnhancedSR
from store_transcribed_report import StoreTranscribedReport
from logger_config import setup_logging

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)
config = load_config("config.yaml")

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Run enhanced SR transcription")
    parser.add_argument("STUDY_KEY", help="Study key for processing")
    args = parser.parse_args()

    try:
        final_path = process_study_key(config, args.STUDY_KEY)
        logging.info(f"DICOM file path: {final_path}")
    except Exception as err:
        logging.error(f"Error processing study key: {err}")
        sys.exit(1)

    extract_audio = ExtractAudio(config)
    transcribe = Transcribe(config)
    encapsulate_text_as_enhanced_sr = EncapsulateTextAsEnhancedSR(config)
    store_transcribed_report = StoreTranscribedReport(config)

    audio_path = extract_audio.extract_audio(final_path)
    report_text = transcribe.transcribe(final_path, audio_path)
    if report_text:
        sr_path = encapsulate_text_as_enhanced_sr.encapsulate_text_as_enhanced_sr(report_text, final_path)
        logging.info(f"Enhanced SR saved to: {sr_path}")
        store_transcribed_report.store_transcribed_report(args.STUDY_KEY, report_text)
    else:
        logging.warning("No transcription was generated.")

if __name__ == "__main__":
    main()
