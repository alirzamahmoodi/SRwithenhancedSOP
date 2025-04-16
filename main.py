import sys
import argparse
import yaml
import logging
import os

# Remove direct pipeline imports, they are used by processing_worker now
from modules.database_monitor import DatabaseMonitor
# from modules.query import process_study_key # Moved to processing_worker
# from modules.extract_audio import ExtractAudio # Moved to processing_worker
# from modules.transcribe import Transcribe # Moved to processing_worker
# from modules.store_transcribed_report import StoreTranscribedReport # Moved to processing_worker
# from modules.encapsulate_text_as_enhanced_sr import EncapsulateTextAsEnhancedSR # Moved to processing_worker

from modules.logger_config import setup_logging
from modules import database_operations as db_ops # Still needed for initial connection
# from modules import smb_connect # Moved to processing_worker

# Keep oracledb imports if init_oracle_client is used
import oracledb 
import cryptography.hazmat.primitives.kdf.pbkdf2
import cryptography.x509

def load_config(config_path):
    try:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Error: Configuration file not found at {config_path}", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing configuration file {config_path}: {e}", file=sys.stderr)
        sys.exit(1)

# Load config early to use for logging and DB setup
config_path = "config.yaml"
config = load_config(config_path)

# Setup logging using the loaded config path
setup_logging(config_path)
logger = logging.getLogger('detailed') # Get the configured logger

# Initialize DB connection (optional, can be lazy)
# Consider moving this into DatabaseMonitor or ensuring it's called before monitor needs it.
db_ops.connect_db(config)

# Uncomment and adjust Oracle client initialization if needed.
# oracle_client_path = config.get("ORACLE_CLIENT_PATH")
# if oracle_client_path:
#     try:
#         logger.info(f"Initializing Oracle Client from path: {oracle_client_path}")
#         oracledb.init_oracle_client(lib_dir=oracle_client_path)
#         logger.info("Oracle Client initialized successfully.")
#     except Exception as e: # Catch a broader exception type during init
#         logger.error(f"Failed to initialize Oracle Client path: {e}", exc_info=True)
#         sys.exit(1)
# else:
#     logger.warning("ORACLE_CLIENT_PATH not found in config.yaml. Proceeding without explicit initialization.")

# ----------------- Pipeline Execution (REMOVED) -----------------
# def run_pipeline(study_key):
    # ... This function is now moved to modules/processing_worker.py ...

# ----------------- Main Entry Point -----------------
def main():
    # Logging is already set up
    # Config is already loaded
    # DB connection might be initialized

    parser = argparse.ArgumentParser(description="Run enhanced SR transcription pipeline in monitor mode.")
    # Remove STUDY_KEY argument
    # parser.add_argument("STUDY_KEY", nargs="?", help="Study key for processing")
    parser.add_argument("--monitor", action="store_true", help="Run database monitoring mode (required)")
    args = parser.parse_args()

    if args.monitor:
        logger.info("Starting database monitor mode...")
        # Pass config to monitor
        monitor = DatabaseMonitor(config)
        try:
            # start_monitoring now contains the loop that calls the processing worker
            monitor.start_monitoring()
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received. Stopping monitor...")
            monitor.stop_monitoring()
            logger.info("Database monitoring stopped by user.")
        except Exception as e:
            logger.critical(f"Unhandled exception in monitor mode: {e}", exc_info=True)
            monitor.stop_monitoring() # Attempt graceful shutdown
            sys.exit(1) # Exit with error code
        finally:
             # Ensure DB connections are closed if monitor manages them
             # Or handle cleanup within monitor.stop_monitoring()
             logger.info("Monitor mode exiting.")
             sys.exit(0) # Normal exit

    # if args.STUDY_KEY: # Logic removed
        # run_pipeline(args.STUDY_KEY)
    else: # Only error if --monitor flag is missing
        parser.error("The --monitor flag is required to run the service.")

if __name__ == "__main__":
    main()
