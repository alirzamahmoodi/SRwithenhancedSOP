import sys
import argparse
import yaml
import logging
import oracledb
import cryptography.hazmat.primitives.kdf.pbkdf2
import cryptography.x509
import threading
import queue
import subprocess
import time
import os

# Update import statements to use modules directory
from modules.database_monitor import DatabaseMonitor
from modules.query import process_study_key
from modules.extract_audio import ExtractAudio
from modules.transcribe import Transcribe
from modules.store_transcribed_report import StoreTranscribedReport
from modules.logger_config import setup_logging
# from modules.encapsulate_text_as_enhanced_sr import EncapsulateTextAsEnhancedSR

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)
config = load_config("config.yaml")

# Uncomment and adjust Oracle client initialization if needed.
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

# ----------------- Pipeline Execution -----------------
def run_pipeline(study_key):
    try:
        final_path = process_study_key(config, study_key)
        logging.info(f"DICOM file path: {final_path}")
    except Exception as err:
        logging.error(f"Error processing study key {study_key}: {err}")
        sys.exit(1)

    extract_audio = ExtractAudio(config)
    transcribe = Transcribe(config)
    # encapsulate_text_as_enhanced_sr = EncapsulateTextAsEnhancedSR(config)
    store_transcribed_report = StoreTranscribedReport(config)

    # Extract audio and obtain the temporary WAV file path.
    audio_path = extract_audio.extract_audio(final_path)

    # Use the temporary WAV file in the transcription process.
    report_list = transcribe.transcribe(final_path, audio_path)

    # After transcription (and any subsequent processing), delete the temporary WAV file.
    if os.path.exists(audio_path):
        try:
            os.remove(audio_path)
            logging.info(f"Temporary audio file deleted: {audio_path}")
        except Exception as e:
            logging.warning(f"Failed to delete temporary audio file {audio_path}: {e}")

    if report_list:
        if config.get('ENCAPSULATE_TEXT_AS_ENHANCED_SR', 'OFF') == 'ON':
            sr_path = encapsulate_text_as_enhanced_sr.encapsulate_text_as_enhanced_sr(report_list, final_path)
            logging.info(f"Enhanced SR saved to: {sr_path}")

        if config.get('STORE_TRANSCRIBED_REPORT', 'OFF') == 'ON':
            store_transcribed_report.store_transcribed_report(study_key, report_list)

        if config.get('PRINT_GEMINI_OUTPUT', 'OFF') == 'ON':
            print(report_list)
    else:
        logging.warning("No transcription was generated.")

# ----------------- Main Entry Point -----------------
def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Run enhanced SR transcription pipeline")
    # STUDY_KEY is optional if running in monitor mode.
    parser.add_argument("STUDY_KEY", nargs="?", help="Study key for processing")
    parser.add_argument("--monitor", action="store_true", help="Run database monitoring mode")
    args = parser.parse_args()

    if args.monitor:
        logging.info("Starting database monitor mode...")
        monitor = DatabaseMonitor(config)
        try:
            monitor.start_monitoring()
        except KeyboardInterrupt:
            monitor.stop_monitoring()
            logging.info("Database monitoring stopped by user.")
        sys.exit(0)

    if args.STUDY_KEY:
        run_pipeline(args.STUDY_KEY)
    else:
        parser.error("You must provide a STUDY_KEY or use the --monitor flag.")

if __name__ == "__main__":
    main()
