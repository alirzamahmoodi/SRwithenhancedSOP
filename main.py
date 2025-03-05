import sys
import argparse
import yaml
import logging
import oracledb
import cryptography.hazmat.primitives.kdf.pbkdf2
import cryptography.x509
from query import process_study_key
from extract_audio import ExtractAudio
from transcribe import Transcribe
from encapsulate_text_as_enhanced_sr import EncapsulateTextAsEnhancedSR
from store_transcribed_report import StoreTranscribedReport
from logger_config import setup_logging
import os

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)
config = load_config("config.yaml")

# oracle_client_path = config.get("ORACLE_CLIENT_PATH")
# if oracle_client_path:
#     try:
#         oracledb.init_oracle_client(lib_dir=oracle_client_path)
#         logging.info("Connected to Oracle Client successfully.")
#     except oracledb.DatabaseError as e:
#         logging.error(f"Failed to set Oracle Client path: {e}")
#         sys.exit(1)
# else:
#     logging.error("ORACLE_CLIENT_PATH not found in config.yaml")
#     sys.exit(1)

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
    report_list = transcribe.transcribe(final_path, audio_path)
    if report_list:
        if config.get('ENCAPSULATE_TEXT_AS_ENHANCED_SR', 'OFF') == 'ON':
            sr_path = encapsulate_text_as_enhanced_sr.encapsulate_text_as_enhanced_sr(report_list, final_path)
            logging.info(f"Enhanced SR saved to: {sr_path}")
        
        if config.get('STORE_TRANSCRIBED_REPORT', 'OFF') == 'ON':
            store_transcribed_report.store_transcribed_report(args.STUDY_KEY, report_list)
        
        if config.get('PRINT_GEMINI_OUTPUT', 'OFF') == 'ON':
            print(report_list)
    else:
        logging.warning("No transcription was generated.")

if __name__ == "__main__":
    main()
