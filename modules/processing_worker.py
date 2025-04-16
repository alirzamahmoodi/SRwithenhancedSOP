import logging
import os
import sys

# Assuming necessary modules are in the parent 'modules' directory or installed
from . import database_operations as db_ops
from . import smb_connect
from .query import process_study_key
from .extract_audio import ExtractAudio
from .transcribe import Transcribe
from .store_transcribed_report import StoreTranscribedReport # If used and enabled
from .encapsulate_text_as_enhanced_sr import EncapsulateTextAsEnhancedSR # If used and enabled

# Note: Config is passed as an argument, no need to load it here unless for defaults
# from modules.logger_config import setup_logging # Logging should be configured by the caller (main.py or monitor)

def process_study(config, study_key):
    """Processes a single study key through the transcription pipeline."""
    final_path = None
    audio_path = None
    sr_path = None # Initialize sr_path
    logger = logging.getLogger('detailed') # Get the logger configured by the main script
    logger.info(f"--- Starting pipeline for study key: {study_key} ---")

    try:
        # Record initial status or update existing one
        db_ops.update_study_status(config, study_key, "processing_query")
        final_path = process_study_key(config, study_key)
        logger.info(f"DICOM file path found: {final_path}")

        # Check if path is valid before proceeding
        if not final_path or not isinstance(final_path, str):
             error_msg = f"Failed to retrieve a valid DICOM path for study {study_key}. Path received: {final_path}"
             logger.error(error_msg)
             db_ops.update_study_status(config, study_key, "error", error_message=error_msg)
             return # Exit processing

        # --- Add Network Share Connection Logic ---
        # Check if path is UNC and if credentials are in config
        share_user = config.get('SHARE_USERNAME')
        share_pass = config.get('SHARE_PASSWORD')

        is_unc_path = final_path.startswith('\\')

        if is_unc_path and share_user and share_pass:
            logger.info(f"UNC path detected: {final_path}. Attempting network share connection.")
            if not smb_connect.connect_to_share(final_path, share_user, share_pass):
                # Connection failed - log error and update status
                error_msg = f"Failed to authenticate to network share for path: {final_path}"
                logger.error(error_msg)
                db_ops.update_study_status(config, study_key, "error", error_message=error_msg)
                return # Exit pipeline if connection failed
            else:
                logger.info("Network share connection successful or already established.")
        elif is_unc_path and (not share_user or not share_pass):
            logger.warning(f"UNC path detected ({final_path}) but SHARE_USERNAME or SHARE_PASSWORD not found in config.yaml. Proceeding without explicit authentication.")
        # --- End Network Share Connection Logic ---

        # Update status with DICOM path (after potential share connection)
        db_ops.update_study_status(config, study_key, "processing_audio", dicom_path=final_path)

        # Initialize components needed for the pipeline
        extract_audio = ExtractAudio(config)
        transcribe = Transcribe(config)


        # Extract audio
        logger.info(f"Attempting to extract audio from: {final_path}")
        audio_path = extract_audio.extract_audio(final_path)
        # Check if audio extraction was successful
        if not audio_path:
             error_msg = f"Audio extraction failed for DICOM file: {final_path}"
             logger.error(error_msg)
             # update_study_status should ideally be called within extract_audio on failure,
             # but we add a fallback here.
             db_ops.update_study_status(config, study_key, "error", error_message=error_msg)
             return # Exit processing

        logger.info(f"Audio extracted successfully to: {audio_path}")
        db_ops.update_study_status(config, study_key, "transcribing")

        # Transcribe
        logger.info(f"Starting transcription for DICOM {final_path} and audio {audio_path}")
        # The transcribe method now returns a dict or None
        transcription_dict = transcribe.transcribe(final_path, audio_path)

        # Save transcription result to DB *before* optional steps
        if transcription_dict and isinstance(transcription_dict, dict):
            logger.info(f"Transcription successful for study {study_key}. Saving result.")
            db_ops.save_transcription(config, study_key, transcription_dict) # Pass the dict directly
            db_ops.update_study_status(config, study_key, "processing_complete") # Initial complete status
        else:
            logger.warning(f"No transcription was generated or returned for study {study_key}.")
            db_ops.update_study_status(config, study_key, "error", error_message="No transcription generated or transcription failed")
            # Skip further processing if no report
            return # Exit pipeline function

        # Optional: Encapsulate SR
        if config.get('ENCAPSULATE_TEXT_AS_ENHANCED_SR', 'OFF') == 'ON':
            logger.info(f"Encapsulation enabled. Processing SR for study {study_key}.")
            try:
                # Initialize only if needed
                encapsulate_text_as_enhanced_sr = EncapsulateTextAsEnhancedSR(config)
                sr_path = encapsulate_text_as_enhanced_sr.encapsulate_text_as_enhanced_sr(transcription_dict, final_path) # Pass dict

                # Check if SR generation was successful before logging/saving
                if sr_path:
                    logger.info(f"Enhanced SR saved to: {sr_path}")
                    # Update transcription record with SR path
                    db_ops.save_transcription(config, study_key, transcription_dict, sr_path=sr_path) # Update existing record
                    db_ops.update_study_status(config, study_key, "processing_complete_sr") # More specific complete status
                else:
                    logger.error(f"Enhanced SR generation failed for study {study_key}. sr_path is None.")
                    db_ops.update_study_status(config, study_key, "error", error_message="SR encapsulation failed (returned None)")

            except Exception as e:
                 logger.error(f"Failed during SR encapsulation for {study_key}: {e}", exc_info=True) # Add exc_info for details
                 db_ops.update_study_status(config, study_key, "error", error_message=f"SR encapsulation failed: {str(e)[:200]}") # Truncate long errors

        # Optional: Store report (potentially legacy/alternative storage)
        if config.get('STORE_TRANSCRIBED_REPORT', 'OFF') == 'ON':
            logger.info(f"Legacy report storage enabled. Storing report for study {study_key}.")
            try:
                # Initialize only if needed
                store_transcribed_report = StoreTranscribedReport(config)
                # Adapt this call based on what store_transcribed_report expects.
                # If it expects the list format, wrap the dict: [transcription_dict]
                # If it expects the dict, pass it directly: transcription_dict
                # Assuming it might still expect the list:
                store_transcribed_report.store_transcribed_report(study_key, [transcription_dict])
                logger.info(f"Legacy report stored successfully for {study_key}.")
                # db_ops.update_study_status(config, study_key, "processing_complete_stored") # Even more specific status if needed
            except Exception as e:
                 logger.error(f"Failed during custom report storage for {study_key}: {e}", exc_info=True)
                 # Avoid overwriting a potential SR error with this less critical one? Or append?
                 # Let's just log for now, assuming DB status reflects primary outcome.
                 # db_ops.update_study_status(config, study_key, "error", error_message=f"Custom storage failed: {str(e)[:200]}")

        # Optional: Print output
        if config.get('PRINT_GEMINI_OUTPUT', 'OFF') == 'ON':
            logger.info(f"Printing Gemini Output for {study_key}:")
            print(transcription_dict) # Print the dictionary

        logger.info(f"--- Pipeline finished for study key: {study_key} ---")

    except FileNotFoundError as fnf_err:
        # Specifically catch FileNotFoundError which might occur if path is wrong
        error_msg = f"Pipeline error (FileNotFound) for study key {study_key}: {fnf_err}"
        logger.error(error_msg)
        db_ops.update_study_status(config, study_key, "error", error_message=str(fnf_err))

    except Exception as err:
        # General error handler
        error_msg = f"Pipeline error for study key {study_key}: {err}"
        logger.error(error_msg, exc_info=True) # Log full traceback for unexpected errors
        db_ops.update_study_status(config, study_key, "error", error_message=f"Pipeline failed: {str(err)[:200]}")

    finally:
        # Cleanup temporary audio file
        if audio_path and os.path.exists(audio_path):
            logger.debug(f"Attempting to delete temporary audio file: {audio_path}")
            try:
                os.remove(audio_path)
                logger.info(f"Temporary audio file deleted: {audio_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temporary audio file {audio_path}: {e}") 