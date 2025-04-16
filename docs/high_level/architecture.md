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
    subgraph Service Host
        APP(main.py --monitor) -- Starts --> DBMON(modules/database_monitor.py)
        DBMON -- Polls --> ODB[(Oracle DB)]
        DBMON -- Finds Study_Key --> PW(modules/processing_worker.py)
        DBMON -- Status Updates --> DBOPS(modules/database_operations.py)

        PW -- Study_Key --> Q(modules/query.py)
        ODB -- Metadata --> Q
        Q -- Path String --> PW
        PW -- Status Updates --> DBOPS

        PW -- UNC Path + Credentials --> SMB(modules/smb_connect.py)
        SMB -- Authenticates --> FS[Network Share]

        PW -- Path --> EA(modules/extract_audio.py)
        FS -- DICOM File --> EA
        EA -- Audio File --> PW
        PW -- Status Updates --> DBOPS

        PW -- Audio File --> T(modules/transcribe.py)
        T -- Audio Data --> EXT(External Transcribe API)
        EXT -- Report Dict --> T
        T -- Report Dict --> PW

        %% Database Operations Module handles MongoDB
        PW -- Report Data / Status Updates --> DBOPS
        DBOPS -- Writes --> MDB[(MongoDB)]

        %% Assuming a module (like StoreReportModule) saves text to Oracle
        PW -- Report Dict --> STORE(modules/store_transcribed_report.py)
        STORE -- Saves Transcription --> ODB
    end

    style MDB fill:#b9f6ca
    style ODB fill:#f9bdbb
```

## Sequence Diagram

```mermaid
sequenceDiagram
    participant Main as main.py
    participant DBMON as DatabaseMonitor
    participant PWORK as ProcessingWorker
    participant DBOPS as DBOperations
    participant QUERY as QueryModule
    participant SMBC as SmbConnect
    participant EXTAUD as ExtractAudio
    participant TRANSC as TranscribeModule
    participant STORE as StoreReportModule
    participant ESR as EncapsulateSRModule
    participant ORACLE as OracleDB
    participant MONGO as MongoDB
    participant SHARE as NetworkShare
    participant TEMP as TempFileSystem
    participant API as GeminiAPI
    participant SR_OUT as SROutputFolder

    Main->>DBMON: Start Monitoring
    loop Polling Loop
        DBMON->>ORACLE: Poll for studies (STUDYSTAT=3010)
        ORACLE-->>DBMON: study_key
        DBMON->>DBOPS: update_status(study_key, 'received')
        DBOPS->>MONGO: Write status 'received'
        DBMON->>PWORK: process_study(study_key)
        activate PWORK
        PWORK->>DBOPS: update_status(study_key, 'processing_query')
        DBOPS->>MONGO: Write status 'processing_query'
        PWORK->>QUERY: get_dicom_path(study_key)
        activate QUERY
        QUERY->>ORACLE: Read metadata/path
        ORACLE-->>QUERY: path_info
        QUERY-->>PWORK: dicom_path
        deactivate QUERY

        alt If path is UNC
            PWORK->>SMBC: connect(path, credentials)
            activate SMBC
            SMBC->>SHARE: Authenticate
            SMBC-->>PWORK: Connection Success/Fail
            deactivate SMBC
        end

        PWORK->>DBOPS: update_status(study_key, 'processing_audio')
        DBOPS->>MONGO: Write status 'processing_audio'
        PWORK->>EXTAUD: extract_audio(dicom_path)
        activate EXTAUD
        EXTAUD->>SHARE: Read DICOM file
        EXTAUD->>TEMP: Write temp_audio_file
        EXTAUD-->>PWORK: temp_audio_path
        deactivate EXTAUD

        PWORK->>DBOPS: update_status(study_key, 'transcribing')
        DBOPS->>MONGO: Write status 'transcribing'
        PWORK->>TRANSC: transcribe(dicom_path, temp_audio_path)
        activate TRANSC
        TRANSC->>TEMP: Read temp_audio_file
        TRANSC->>API: Send audio data
        API-->>TRANSC: report_dict
        TRANSC-->>PWORK: report_dict
        deactivate TRANSC

        PWORK->>DBOPS: save_transcription(study_key, report_dict)
        DBOPS->>MONGO: Write transcription data
        PWORK->>DBOPS: update_status(study_key, 'saving_report')
        DBOPS->>MONGO: Write status 'saving_report'

        PWORK->>STORE: save_to_oracle(report_dict)
        activate STORE
        STORE->>ORACLE: Call F_INSERT(report_data)
        STORE-->>PWORK: Success/Fail
        deactivate STORE
        PWORK->>DBOPS: update_status(study_key, 'complete_oracle')
        DBOPS->>MONGO: Write status 'complete_oracle'

        opt Create SR Report
            PWORK->>ESR: create_sr(dicom_path, report_dict)
            activate ESR
            ESR->>SHARE: Read DICOM template/data
            ESR->>SR_OUT: Write SR file
            ESR-->>PWORK: sr_file_path
            deactivate ESR
            PWORK->>DBOPS: update_status(study_key, 'complete_sr_oracle')
            DBOPS->>MONGO: Write status 'complete_sr_oracle'
        end

        PWORK->>TEMP: Delete temp_audio_file
        deactivate PWORK
        PWORK-->>DBMON: Processing Finished
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