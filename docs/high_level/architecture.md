# System Architecture

## Overview

This system automates the process of transcribing medical dictations associated with DICOM studies. It monitors an Oracle database for new studies, retrieves associated DICOM audio data (potentially from authenticated network shares), uses an external service (like Google Gemini) for transcription, stores the status and results in a MongoDB database, and provides a Django-based web dashboard for monitoring progress.


## Key Components

1.  **Main Application (`main.py`)**
    *   Entry point for the service, launched via `python main.py --monitor`.
    *   Loads configuration (`config.yaml`), initializes logging.
    *   Instantiates and starts the `DatabaseMonitor`.

2.  **Oracle Database Monitor (`modules/database_monitor.py`)**
    *   Polls an Oracle table (e.g., `TSTUDY`) for studies requiring transcription (e.g., `STUDYSTAT=3010`).
    *   When a new `STUDY_KEY` is detected, it updates the study's status to `received` in the MongoDB `studies` collection via `database_operations`.
    *   Directly calls `processing_worker.process_study(config, study_key)` to initiate the pipeline for that study.
    *   Waits for the `process_study` call to complete before continuing the polling loop.

3.  **Processing Worker (`modules/processing_worker.py`)**
    *   Contains the `process_study(config, study_key)` function, which orchestrates the transcription process for a single study.
    *   Calls `query.process_study_key` to get the potential DICOM path from Oracle.
    *   Updates study status in MongoDB (`processing_query`, `processing_audio`, `transcribing`, etc.) via `database_operations`.
    *   If the path is UNC, calls `smb_connect.connect_to_share` to authenticate.
    *   Calls `extract_audio.extract_audio` to read the DICOM file and save a temporary audio file.
    *   Calls `transcribe.transcribe` to send the audio to the external transcription service.
    *   If transcription is successful:
        *   Calls `database_operations.save_transcription` to store the report text/dictionary in the MongoDB `transcriptions` collection.
        *   Updates study status to `processing_complete` (or `processing_complete_sr` if SR encapsulation is enabled) in MongoDB.
    *   Handles errors, updating the study status to `error` in MongoDB with details.
    *   Cleans up temporary files.

4.  **Path Query (`modules/query.py`)**
    *   Receives a `STUDY_KEY`.
    *   Connects to the Oracle database to retrieve metadata associated with the study.
    *   Constructs the full, potential DICOM file path.
    *   Returns the constructed path string.

5.  **Network Share Connector (`modules/smb_connect.py`)**
    *   Receives a UNC path and credentials.
    *   Uses `pywin32` to establish an authenticated connection to the network share.

6.  **Audio Extraction (`modules/extract_audio.py`)**
    *   Takes the DICOM file path.
    *   Reads the DICOM file, extracts the audio stream, saves it to a temporary file.
    *   Returns the path to the temporary audio file.

7.  **Transcription (`modules/transcribe.py`)**
    *   Takes the DICOM path and temporary audio file path.
    *   Connects to the external transcription service (e.g., Google Gemini API).
    *   Sends the audio, receives the report (as a dictionary).
    *   Returns the report dictionary or `None`.

8.  **MongoDB Operations (`modules/database_operations.py`)**
    *   Provides functions (`update_study_status`, `save_transcription`) to interact with MongoDB collections (`studies`, `transcriptions`).

9.  **MongoDB Database**
    *   Stores application state (`studies`) and results (`transcriptions`).

10. **Django Web Dashboard (`dashboard/`)**
    *   Separate web application connecting to MongoDB.
    *   Displays study status and transcription results.
    *   Runs as a separate process (`python manage.py runserver`).

## Technical Stack

| Layer                 | Technologies                                    | Config Source   |
|-----------------------|-------------------------------------------------|-----------------|
| **Runtime**           | Python 3.11, Conda                              | environment.yml |
| **Core Service**      | `oracledb`, `pywin32`                           | config.yaml     |
| **Database**          | MongoDB                                         | config.yaml     |
| **DB Connectors**     | `pymongo`                                       | environment.yml |
| **Web Dashboard**     | Django, `djongo`                                | environment.yml, config.yaml |
| **AI Processing**     | Google Gemini (or other via `transcribe.py`)    | config.yaml     |
| **Medical Imaging**   | `pydicom` (likely used in `extract_audio.py`)   | DICOM Standard  |
| **Build (Optional)**  | PyInstaller                                     | audio_transcriber.spec |

## Data Flow Diagram

```mermaid
graph TD
    %% ===== Define Styles =====
    classDef entry fill:#f9f,stroke:#333,stroke-width:2px;          %% Main Entry Point
    classDef module fill:#ccf,stroke:#333,stroke-width:2px;         %% Core Processing Modules
    classDef dbInterface fill:#e6e6fa,stroke:#333,stroke-width:2px;  %% MongoDB Interface Module
    classDef primaryDB fill:#f8c471,stroke:#333,stroke-width:2px;    %% Oracle - Source & Final Report
    classDef processDB fill:#aed6f1,stroke:#333,stroke-width:2px;    %% Mongo - Process State Tracking
    classDef externalAPI fill:#f7dc6f,stroke:#333,stroke-width:2px;   %% External Service (Gemini)
    classDef fileSystem fill:#a9dfbf,stroke:#333,stroke-width:2px;   %% Filesystem Resources
    classDef dashboard fill:#d7dbdd,stroke:#333,stroke-width:2px;    %% Web Dashboard

    %% ===== External Systems / Data Stores =====
    ORACLE[(Oracle DB)]:::primaryDB
    MONGO[(MongoDB)]:::processDB
    API{{Gemini API}}:::externalAPI
    SHARE[Network Share]:::fileSystem
    TEMP[Temp Audio Files]:::fileSystem
    SR_OUT[SR Output Folder]:::fileSystem

    %% ===== Main Application Flow =====
    subgraph "Transcription Service Host"
        direction TB
        MAIN(main.py --monitor):::entry
        DBMON(database_monitor.py):::module
        PWORK(processing_worker.py):::module
        DBOPS(database_operations.py):::dbInterface
        QUERY(query.py):::module
        SMBC(smb_connect.py):::module
        EXTAUD(extract_audio.py):::module
        TRANSC(transcribe.py):::module
        STORE(store_transcribed_report.py):::module
        ESR(encapsulate_..._sr.py):::module

        %% --- Monitoring & Initiation ---
        MAIN -- Starts --> DBMON
        DBMON -- 1. Polls (STUDYSTAT=3010) --> ORACLE
        ORACLE -- 2. Returns study_key --> DBMON
        DBMON -- 3. Update Status ('received') --> DBOPS
        DBOPS -- 3a. Writes Status --> MONGO
        DBMON -- 4. Calls process_study --> PWORK

        %% --- Study Processing Pipeline ---
        PWORK -- 5. Update Status ('processing_query') --> DBOPS
        PWORK -- 6. Needs DICOM Path --> QUERY
        QUERY -- 6a. Reads Metadata/Path --> ORACLE
        ORACLE -- 6b. Returns Path Info --> QUERY
        QUERY -- 6c. Returns dicom_path --> PWORK

        PWORK -- 7. Connects to Share (if UNC) --> SMBC
        SMBC -- 7a. Authenticates --> SHARE

        PWORK -- 8. Update Status ('processing_audio') --> DBOPS
        PWORK -- 9. Needs Audio --> EXTAUD
        EXTAUD -- 9a. Reads DICOM --> SHARE
        EXTAUD -- 9b. Writes Temp Audio --> TEMP
        EXTAUD -- 9c. Returns audio_path --> PWORK

        PWORK -- 10. Update Status ('transcribing') --> DBOPS
        PWORK -- 11. Needs Transcription --> TRANSC
        TRANSC -- 11a. Reads Temp Audio --> TEMP
        TRANSC -- 11b. Sends Audio --> API
        API -- 11c. Returns Report Dictionary --> TRANSC
        TRANSC -- 11d. Returns report_dict --> PWORK

        %% --- Result Handling & Storage ---
        PWORK -- 12. Store Temp Transcription --> DBOPS
        DBOPS -- 12a. Writes Transcription --> MONGO
        PWORK -- 13. Update Status ('saving_report') --> DBOPS

        %% --- Primary Output: Save to Oracle ---
        PWORK -- 14. Saves Final Report --> STORE
        STORE -- 14a. Calls F_INSERT --> ORACLE
        PWORK -- 15. Update Status ('complete_oracle') --> DBOPS

        %% --- Optional Output: Create SR File ---
        subgraph "Optional SR Output"
            direction TB
            PWORK -- 16. Creates SR? --> ESR
            ESR -- 16a. Reads DICOM --> SHARE
            ESR -- 16b. Writes SR File --> SR_OUT
            ESR -- 16c. Returns sr_path --> PWORK
            PWORK -- 16d. Update Status ('complete_sr_oracle') --> DBOPS
        end

        %% --- Cleanup & Loop Continuation ---
        PWORK -- 17. Deletes Temp Audio --> TEMP
        PWORK -- 18. Processing Complete --> DBMON
        DBMON -- 19. Continues Polling --> DBMON

        %% --- General DB Interface Links ---
        DBOPS -- Manages Study State --> MONGO
    end

    %% ===== Dashboard Flow =====
    subgraph "Dashboard Host"
        DASH(Dashboard App):::dashboard
        USER(User via Browser)

        USER -- Views Dashboard --> DASH
        DASH -- Reads Status/Transcriptions --> MONGO
        MONGO -- Returns Data --> DASH
        DASH -- Renders Page --> USER
    end
```
*Diagram clarifying database roles and workflow steps.*

*   **Credentials:**
    *   `config.yaml` contains sensitive credentials. Access control is crucial.
    *   Consider alternatives like environment variables or secrets management for production.
*   **Network Shares:** Use least privilege principles for the `SHARE_USERNAME` account.
*   **MongoDB:** Configure authentication and network controls.
*   **Django Dashboard:** Follow Django security best practices.
*   **PHI:** Review transcription service handling of PHI.

## Cross References
- [Installation Guide](installation.md)
- [Configuration Reference](config_reference.md)
- [Module Documentation](../modules/main.md)
- [Readme](../readme.md)