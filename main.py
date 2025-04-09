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
from modules import database_operations as db_ops # Import the new module
from modules import smb_connect # Import the SMB connection helper
# from modules.encapsulate_text_as_enhanced_sr import EncapsulateTextAsEnhancedSR

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)
config = load_config("config.yaml")

# Initialize DB connection early if needed, or let get_db handle it lazily
db_ops.connect_db(config) 

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
    final_path = None
    audio_path = None
    sr_path = None # Initialize sr_path
    try:
        # Record initial status or update existing one
        db_ops.update_study_status(config, study_key, "processing_query")
        final_path = process_study_key(config, study_key)
        logging.info(f"DICOM file path: {final_path}")

        # --- Add Network Share Connection Logic --- 
        # Check if path is UNC and if credentials are in config
        share_user = config.get('SHARE_USERNAME')
        share_pass = config.get('SHARE_PASSWORD')
        
        if final_path and final_path.startswith('\\') and share_user and share_pass:
            logging.info(f"UNC path detected: {final_path}. Attempting network share connection.")
            if not smb_connect.connect_to_share(final_path, share_user, share_pass):
                # Connection failed - log error and update status
                error_msg = f"Failed to authenticate to network share for path: {final_path}"
                logging.error(error_msg)
                db_ops.update_study_status(config, study_key, "error", error_message=error_msg)
                return # Exit pipeline if connection failed
            else:
                logging.info("Network share connection successful or already established.")
        elif final_path and final_path.startswith('\\') and (not share_user or not share_pass):
            logging.warning(f"UNC path detected ({final_path}) but SHARE_USERNAME or SHARE_PASSWORD not found in config.yaml. Proceeding without explicit authentication.")
        # --- End Network Share Connection Logic ---

        # Update status with DICOM path (after potential share connection)
        db_ops.update_study_status(config, study_key, "processing_audio", dicom_path=final_path)

        extract_audio = ExtractAudio(config)
        transcribe = Transcribe(config)
        # encapsulate_text_as_enhanced_sr = EncapsulateTextAsEnhancedSR(config)
        store_transcribed_report = StoreTranscribedReport(config)

        # Extract audio
        # This step should now succeed if the share connection worked
        audio_path = extract_audio.extract_audio(final_path)
        db_ops.update_study_status(config, study_key, "transcribing")

        # Transcribe
        report_list = transcribe.transcribe(final_path, audio_path)

        # Save transcription result to DB *before* optional steps
        if report_list:
            db_ops.save_transcription(config, study_key, report_list)
            db_ops.update_study_status(config, study_key, "processing_complete") # Initial complete status
        else:
            logging.warning("No transcription was generated.")
            db_ops.update_study_status(config, study_key, "error", error_message="No transcription generated")
            # Skip further processing if no report
            return # Exit pipeline function

        # Optional: Encapsulate SR
        if config.get('ENCAPSULATE_TEXT_AS_ENHANCED_SR', 'OFF') == 'ON':
            try:
                # Ensure the module is imported if used
                # from modules.encapsulate_text_as_enhanced_sr import EncapsulateTextAsEnhancedSR
                # encapsulate_text_as_enhanced_sr = EncapsulateTextAsEnhancedSR(config)
                # sr_path = encapsulate_text_as_enhanced_sr.encapsulate_text_as_enhanced_sr(report_list, final_path)
                
                # Placeholder for actual SR generation call if module exists
                sr_path = f"/path/to/generated/{study_key}.dcm" # Example path
                
                logging.info(f"Enhanced SR saved to: {sr_path}")
                # Update transcription record with SR path
                db_ops.save_transcription(config, study_key, report_list, sr_path=sr_path) # Update existing or save again if needed
                db_ops.update_study_status(config, study_key, "processing_complete_sr") # More specific complete status
            except Exception as e:
                 logging.error(f"Failed during SR encapsulation for {study_key}: {e}")
                 db_ops.update_study_status(config, study_key, "error", error_message=f"SR encapsulation failed: {e}")


        # Optional: Store report (potentially legacy/alternative storage)
        if config.get('STORE_TRANSCRIBED_REPORT', 'OFF') == 'ON':
            try:
                store_transcribed_report.store_transcribed_report(study_key, report_list)
                # db_ops.update_study_status(config, study_key, "processing_complete_stored") # Even more specific status if needed
            except Exception as e:
                 logging.error(f"Failed during custom report storage for {study_key}: {e}")
                 db_ops.update_study_status(config, study_key, "error", error_message=f"Custom storage failed: {e}")

        # Optional: Print output
        if config.get('PRINT_GEMINI_OUTPUT', 'OFF') == 'ON':
            print(report_list)

    except FileNotFoundError as fnf_err:
        # Specifically catch FileNotFoundError which might still occur if path is wrong
        # even after authentication, or if auth failed silently (e.g., conflict).
        error_msg = f"Pipeline error (FileNotFound) for study key {study_key}: {fnf_err}"
        logging.error(error_msg)
        db_ops.update_study_status(config, study_key, "error", error_message=str(fnf_err))
    
    except Exception as err:
        # General error handler
        error_msg = f"Pipeline error for study key {study_key}: {err}"
        logging.error(error_msg, exc_info=True) # Log full traceback for unexpected errors
        db_ops.update_study_status(config, study_key, "error", error_message=str(err))

    finally:
        # Cleanup temporary audio file
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
                logging.info(f"Temporary audio file deleted: {audio_path}")
            except Exception as e:
                logging.warning(f"Failed to delete temporary audio file {audio_path}: {e}")

# ----------------- Main Entry Point -----------------
def main():
    setup_logging()
    # Load config once
    config = load_config("config.yaml") 
    # Initialize DB connection (optional, can be lazy)
    db_ops.connect_db(config)

    parser = argparse.ArgumentParser(description="Run enhanced SR transcription pipeline")
    # STUDY_KEY is optional if running in monitor mode.
    parser.add_argument("STUDY_KEY", nargs="?", help="Study key for processing")
    parser.add_argument("--monitor", action="store_true", help="Run database monitoring mode")
    args = parser.parse_args()

    if args.monitor:
        logging.info("Starting database monitor mode...")
        # Pass config to monitor
        monitor = DatabaseMonitor(config)
        try:
            # The monitor should call run_pipeline, which now handles DB updates
            monitor.start_monitoring()
        except KeyboardInterrupt:
            monitor.stop_monitoring()
            logging.info("Database monitoring stopped by user.")
        # Maybe cleanup DB connection here if needed
        sys.exit(0)

    if args.STUDY_KEY:
        # Pass config to run_pipeline if not already global/accessible
        run_pipeline(args.STUDY_KEY)
    elif not args.monitor: # Only error if not monitor and no study key
        parser.error("You must provide a STUDY_KEY or use the --monitor flag.")

if __name__ == "__main__":
    main()
