import oracledb
import os
import logging
import sys
from modules.logger_config import setup_logging

setup_logging()


def process_study_key(config, study_key):
    # Create DSN from individual config values if ORACLE_DSN is not provided.
    logging.info("Creating DSN for Oracle connection.")
    dsn = oracledb.makedsn(config["ORACLE_HOST"], config["ORACLE_PORT"], service_name=config["ORACLE_SERVICE_NAME"])
    logging.info(f"DSN: {dsn}")

    logging.info("Connecting to Oracle database.")
    connection = oracledb.connect(user=config["ORACLE_USERNAME"], password=config["ORACLE_PASSWORD"], dsn=dsn)

    logging.info("Creating cursor for database operations.")
    cursor = connection.cursor()
    try:
        # Retrieve REPORT_KEY and REPORT_STAT for the given STUDY_KEY.
        cursor.execute(
            "SELECT REPORT_KEY, REPORT_STAT FROM TREPORT WHERE STUDY_KEY = :study_key",
            study_key=study_key
        )
        row = cursor.fetchone()
        if not row:
            logging.error(f"No TREPORT record found for STUDY_KEY={study_key}")
            sys.exit(1)
        report_key, report_stat = row

        # Query TDICTATION to get PATHNAME, FILENAME and LSTORAGE_KEY
        cursor.execute(
            "SELECT PATHNAME, FILENAME, LSTORAGE_KEY FROM TDICTATION WHERE REPORT_KEY = :report_key",
            report_key=report_key
        )
        dictation_row = cursor.fetchone()
        if not dictation_row:
            logging.error(f"No TDICTATION record found for REPORT_KEY={report_key}")
            sys.exit(1)
        pathname, filename, lstorage_key = dictation_row

        # Get storage location from TSTORAGE using LSTORAGE_KEY
        cursor.execute(
            "SELECT SHARE_FOLDER FROM TSTORAGE WHERE STORAGE_KEY = :lstorage_key",
            lstorage_key=lstorage_key
        )
        storage_row = cursor.fetchone()
        if not storage_row:
            logging.error("No TSTORAGE record found for storage configuration")
            sys.exit(1)
        share_folder = storage_row[0]

        # Construct UNC path using share name from TSTORAGE
        unc_root = f'\\\\{config["ORACLE_HOST"]}\\{share_folder}'

        # Combine paths using the share root from TSTORAGE
        final_path = os.path.join(unc_root, pathname, filename)
        final_path = os.path.abspath(os.path.normpath(final_path))

        # --- REMOVED FILE EXISTENCE CHECK --- 
        # Verification should happen after potential authentication in main.py
        # if not os.path.exists(final_path):
        #     logging.error(f"File not found at constructed path: {final_path}")
        #     sys.exit(1)

        logging.info(f"Constructed potential DICOM path: {final_path}")
        return final_path
    finally:
        cursor.close()
        connection.close()