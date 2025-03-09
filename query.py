import oracledb
import os
import logging
import sys
from logger_config import setup_logging

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

        # Query TDICTATION to get PATHNAME and FILENAME using REPORT_KEY.
        cursor.execute(
            "SELECT PATHNAME, FILENAME FROM TDICTATION WHERE REPORT_KEY = :report_key",
            report_key=report_key
        )
        dictation_row = cursor.fetchone()
        if not dictation_row:
            logging.error(f"No TDICTATION record found for REPORT_KEY={report_key}")
            sys.exit(1)
        pathname, filename = dictation_row

        # Combine LONGTERM_PATH from config with PATHNAME and FILENAME from the query.
        final_path = os.path.join(config["LONGTERM_PATH"], pathname, filename)
        return final_path
    finally:
        cursor.close()
        connection.close()