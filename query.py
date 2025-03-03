import cx_Oracle
import os
import sys
import yaml
import argparse
import subprocess
import logging
from logger_config import setup_logging

setup_logging()


def load_config(config_filename):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)
    config_path = os.path.join(base_path, config_filename)
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


def process_study_key(config, study_key):
    # Create DSN from individual config values if ORACLE_DSN is not provided.
    if "ORACLE_DSN" in config:
        dsn = config["ORACLE_DSN"]
    else:
        dsn = cx_Oracle.makedsn(
            config["ORACLE_HOST"],
            config["ORACLE_PORT"],
            service_name=config["ORACLE_SERVICE_NAME"]
        )
    
    connection = cx_Oracle.connect(
        config["ORACLE_USERNAME"],  # changed from ORACLE_USER to ORACLE_USERNAME
        config["ORACLE_PASSWORD"],  # changed from ORACLE_PASS to ORACLE_PASSWORD
        dsn
    )
    
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


def run_main_with_final_path(final_path):
    # Assume main.exe is in the same folder as query.exe.
    main_exe = os.path.join(os.path.dirname(sys.executable), "main.exe")
    subprocess.run([main_exe, final_path], check=True)


def main():
    parser = argparse.ArgumentParser(
        description="Lookup DICOM file path by STUDY_KEY from Oracle database."
    )
    parser.add_argument("STUDY_KEY", help="Study key to lookup in TREPORT table")
    args = parser.parse_args()

    config = load_config("config.yaml")

    try:
        final_path = process_study_key(config, args.STUDY_KEY)
        logging.info(f"DICOM file path: {final_path}")
    except Exception as err:
        logging.error(f"Error processing study key: {err}")
        sys.exit(1)

    # Call main.exe with the DICOM file path as an argument.
    run_main_with_final_path(final_path)


if __name__ == "__main__":
    main()