# Module: database_operations

## Overview

This module centralizes all interactions with the MongoDB database, which stores the application's state (study processing status) and results (transcriptions).

It uses the `pymongo` library to connect to the database specified in `config.yaml` and provides functions to update study status and save transcription data.

## Key Collections

*   **`studies`:** Stores one document per study key, tracking its progress through the pipeline.
    *   `_id`: MongoDB ObjectId
    *   `study_key`: String (Unique identifier)
    *   `dicom_path`: String (Path to source DICOM file)
    *   `status`: String (e.g., "received", "processing_query", "processing_audio", "transcribing", "completed", "error")
    *   `received_timestamp`: DateTime (When first detected)
    *   `last_updated_timestamp`: DateTime (When status last changed)
    *   `error_message`: String (Details if status is "error")
*   **`transcriptions`:** Stores the results of successful transcriptions.
    *   `_id`: MongoDB ObjectId
    *   `study_key`: String (Links to the `studies` collection)
    *   `report_text`: String or List[String] (The transcription result)
    *   `sr_path`: String (Optional, path to generated Enhanced SR DICOM file)
    *   `transcription_timestamp`: DateTime (When transcription was saved)

## Functions

### `connect_db(config)`

*   **Purpose:** Establishes a connection to the MongoDB server and database specified in the `config` dictionary.
*   **Arguments:**
    *   `config` (dict): The application configuration dictionary (loaded from `config.yaml`). Expected keys: `MONGODB_URI`, `MONGODB_DATABASE`.
*   **Returns:** The `pymongo.database.Database` object on success, or `None` on failure.
*   **Details:** Uses a global variable to reuse the connection across calls. Performs a simple check (`ismaster`) to verify the connection.

### `get_db(config)`

*   **Purpose:** Returns the current database connection instance, calling `connect_db` if the connection hasn't been established yet.
*   **Arguments:**
    *   `config` (dict): The application configuration dictionary.
*   **Returns:** The `pymongo.database.Database` object or `None`.

### `update_study_status(config, study_key, status, error_message=None, dicom_path=None)`

*   **Purpose:** Creates or updates a document in the `studies` collection for the given `study_key`.
*   **Arguments:**
    *   `config` (dict): Application configuration.
    *   `study_key` (str): The unique identifier for the study.
    *   `status` (str): The new status to set (e.g., "processing_audio", "error").
    *   `error_message` (str, optional): An error message if the status is "error". Clears the field otherwise.
    *   `dicom_path` (str, optional): The path to the DICOM file, usually set when transitioning to "processing_audio".
*   **Details:** Uses `update_one` with `upsert=True`. Sets `received_timestamp` only on insertion. Updates `last_updated_timestamp` on every call.

### `save_transcription(config, study_key, report_list, sr_path=None)`

*   **Purpose:** Inserts a new document into the `transcriptions` collection with the results.
*   **Arguments:**
    *   `config` (dict): Application configuration.
    *   `study_key` (str): The identifier for the study.
    *   `report_list` (str or list): The transcribed text.
    *   `sr_path` (str, optional): The path where the Enhanced SR file was saved (if generated).
*   **Details:** Uses `insert_one`. Sets the `transcription_timestamp` automatically.

## Dependencies

*   `pymongo`: For MongoDB interaction.
*   `logging`: For application logging.
*   `datetime`: For timestamps.

## Integration

*   Called by `main.py` during the `run_pipeline` function to log progress and results.
*   Called by `modules/database_monitor.py` to log the initial "received" status.
*   The Django dashboard (`dashboard/`) reads data written by this module. 