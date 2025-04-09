import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime
import os

# Global client and db variables to reuse the connection
client = None
db = None

def connect_db(config):
    """Establishes connection to the MongoDB database using config."""
    global client, db
    if db is None:
        try:
            mongodb_uri = config.get("MONGODB_URI", "mongodb://localhost:27017/")
            db_name = config.get("MONGODB_DATABASE", "audio_transcriber_db")
            client = MongoClient(mongodb_uri)
            # The ismaster command is cheap and does not require auth.
            client.admin.command('ismaster')
            db = client[db_name]
            logging.info(f"Successfully connected to MongoDB database: {db_name}")
        except ConnectionFailure as e:
            logging.error(f"Could not connect to MongoDB: {e}")
            db = None # Ensure db is None if connection failed
            # Depending on requirements, you might want to raise the error or exit
            # raise ConnectionFailure(f"Could not connect to MongoDB: {e}") from e
        except Exception as e:
            logging.error(f"An unexpected error occurred during MongoDB connection: {e}")
            db = None
            # raise Exception(f"An unexpected error occurred during MongoDB connection: {e}") from e
    return db

def get_db(config):
    """Returns the database instance, connecting if necessary."""
    if db is None:
        return connect_db(config)
    return db

def update_study_status(config, study_key, status, error_message=None, dicom_path=None):
    """Updates the status of a study in the 'studies' collection or creates it."""
    database = get_db(config)
    if not database:
        logging.error("Database connection not available. Cannot update study status.")
        return

    now = datetime.utcnow()
    query = {"study_key": study_key}
    update_fields = {
        "$set": {
            "status": status,
            "last_updated_timestamp": now,
        },
        "$setOnInsert": {
             "study_key": study_key,
             "received_timestamp": now,
        }
    }
    if dicom_path:
        update_fields["$set"]["dicom_path"] = dicom_path
    if error_message:
        update_fields["$set"]["error_message"] = error_message
    else:
        # Ensure error message is removed if status is not 'error'
        if status != 'error':
             update_fields["$unset"] = {"error_message": ""}

    try:
        logging.debug(f"Updating study {study_key} status to {status}")
        result = database.studies.update_one(query, update_fields, upsert=True)
        if result.upserted_id:
            logging.info(f"Created new study record for {study_key} with status {status}")
        elif result.modified_count > 0:
            logging.info(f"Updated study {study_key} status to {status}")
        else:
             # This might happen if the status is already set to the target value
             logging.debug(f"No changes needed for study {study_key} status {status}")

    except Exception as e:
        logging.error(f"Failed to update status for study {study_key}: {e}")

def save_transcription(config, study_key, report_list, sr_path=None):
    """Saves the transcription result to the 'transcriptions' collection."""
    database = get_db(config)
    if not database:
        logging.error("Database connection not available. Cannot save transcription.")
        return

    now = datetime.utcnow()
    document = {
        "study_key": study_key,
        "report_text": report_list,
        "transcription_timestamp": now
    }
    if sr_path:
        document["sr_path"] = sr_path

    try:
        logging.debug(f"Saving transcription for study {study_key}")
        result = database.transcriptions.insert_one(document)
        logging.info(f"Transcription saved for study {study_key} with ID: {result.inserted_id}")
    except Exception as e:
        logging.error(f"Failed to save transcription for study {study_key}: {e}")

# Consider adding functions for querying data if needed by the core service itself 