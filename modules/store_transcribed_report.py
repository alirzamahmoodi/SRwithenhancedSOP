import oracledb
import logging
from datetime import datetime
import traceback
import json

class StoreTranscribedReport:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('detailed')

    def store_transcribed_report(self, study_key, report_list):
        self.logger.info(f"Storing transcribed report for study key: {study_key}")

        parsed_report_data = None
        # Check if report_list is a string that needs parsing, or already parsed data
        if isinstance(report_list, str):
            self.logger.debug("report_list is a string, attempting JSON parse.")
            try:
                parsed_report_data = json.loads(report_list)
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse report_list string as JSON: {e}")
                self.logger.debug(traceback.format_exc())
                return
        elif isinstance(report_list, list):
            self.logger.debug("report_list is already a list, using directly.")
            parsed_report_data = report_list
        else:
            self.logger.error(f"Unexpected type for report_list: {type(report_list)}. Expected str or list.")
            return

        # Now extract Reading and Conclusion from the parsed data
        try:
            # Ensure parsed_report_data is a list with at least two elements before accessing
            if not isinstance(parsed_report_data, list) or len(parsed_report_data) < 2:
                 raise ValueError(f"Parsed report data is not a list with at least two elements. Data: {parsed_report_data}")

            reading = parsed_report_data[0].get("Reading", "")
            conclusion = parsed_report_data[1].get("Conclusion", "")
            self.logger.debug(f"Extracted Reading (first 50 chars): '{reading[:50]}...'")
            self.logger.debug(f"Extracted Conclusion (first 50 chars): '{conclusion[:50]}...'")
        except (IndexError, KeyError, TypeError, AttributeError, ValueError) as e: # Broader exception catching
            self.logger.error(f"Failed to extract Reading/Conclusion from parsed data structure: {e}")
            # Log the problematic structure for debugging
            self.logger.debug(f"Problematic parsed_report_data structure: {parsed_report_data}")
            self.logger.debug(traceback.format_exc())
            return

        dsn = oracledb.makedsn(self.config["ORACLE_HOST"], self.config["ORACLE_PORT"], self.config["ORACLE_SERVICE_NAME"])
        self.logger.debug(f"DSN created: {dsn}")

        connection = None # Initialize connection
        cursor = None # Initialize cursor
        try:
            # Use keyword arguments for connect
            connection = oracledb.connect(
                user=self.config["ORACLE_USERNAME"],
                password=self.config["ORACLE_PASSWORD"],
                dsn=dsn
            )
            self.logger.debug("Oracle connection established.")
            cursor = connection.cursor()
            self.logger.debug("Cursor created.")

            # Retrieve REPORT_KEY from TREPORT using the provided study_key.
            cursor.execute(
                "SELECT REPORT_KEY FROM TREPORT WHERE STUDY_KEY = :study_key",
                study_key=study_key
            )
            self.logger.debug("Executed query to retrieve REPORT_KEY.")
            row = cursor.fetchone()
            if not row:
                self.logger.warning(f"No TREPORT record found for STUDY_KEY={study_key}")
                return
            report_key = row[0]
            self.logger.debug(f"Retrieved REPORT_KEY: {report_key}")
            report_date = datetime.now().strftime('%Y%m%d%H%M%S')
            self.logger.debug(f"Generated report date: {report_date}")

            # Generate a new REPORT_TEXT_KEY using the existing function F_GET_TEXTKEY
            cursor.execute("SELECT DEB_TREPORT.F_GET_TEXTKEY(:study_key, 'P') FROM DUAL", study_key=study_key)
            report_text_key = cursor.fetchone()[0]
            self.logger.debug(f"Generated REPORT_TEXT_KEY: {report_text_key}")

            # Call the F_INSERT_TEXT function for Reading
            result_reading = cursor.callfunc(
                "DEB_TREPORT.F_INSERT_TEXT",
                oracledb.NUMBER,
                [report_key, 4010, 21, report_date, reading, conclusion, "P"]
            )
            self.logger.debug(f"Called F_INSERT_TEXT for Reading and received result: {result_reading}")

            # Retrieve INSTITUTION_KEY and SRC_PATIENT_ID from TSTUDY using the provided study_key.
            cursor.execute(
                "SELECT INSTITUTION_KEY, SRC_PATIENT_ID FROM TSTUDY WHERE STUDY_KEY = :study_key",
                study_key=study_key
            )
            self.logger.debug("Executed query to retrieve INSTITUTION_KEY and SRC_PATIENT_ID.")
            row = cursor.fetchone()
            if not row:
                self.logger.warning(f"No TSTUDY record found for STUDY_KEY={study_key}")
                return
            institution_key, src_patient_id = row
            self.logger.debug(f"Retrieved INSTITUTION_KEY: {institution_key}, SRC_PATIENT_ID: {src_patient_id}")

            # Update the REPORT_STAT in TREPORTTEXT using the function F_UPDATE
            update_result = cursor.callfunc(
                "DEB_TREPORT.F_UPDATE",
                oracledb.NUMBER,  # using NUMBER as the return type, adjust if needed
                [
                    institution_key,  # V_INSTITUTION_KEY
                    src_patient_id,   # V_PATIENT_ID
                    self.config["ORACLE_HOST"],  # V_HOSTIP
                    "",               # V_COMMENT
                    report_key,       # V_REPORT_KEY
                    study_key,        # V_STUDY_KEY
                    4010,             # V_REPORT_STAT
                    21,             # V_DICTATE_DOC_KEY
                    None,             # V_DICTATE_DATE
                    21,             # V_READ_DOC_KEY
                    report_date,             # V_READ_DATE
                    None,             # V_CONFIRM_DOC_KEY
                    None,             # V_CONFIRM_DATE
                    "P",              # V_REPORT_TYPE
                    None,             # V_DRAFT_DOC_KEY
                    None,             # V_DRAFT_DATE
                    None,             # V_STT
                    None              # V_READ_OPERATOR
                ]
            )
            self.logger.debug(f"Updated REPORT_STAT in TREPORTTEXT with return value: {update_result}")

            # Explicitly update the necessary columns in TREPORT
            cursor.execute(
                "UPDATE TREPORT SET REPORT_STAT = :report_stat WHERE REPORT_KEY = :report_key",
                report_stat=4010,
                report_key=report_key
            )
            self.logger.debug("Updated REPORT_STAT in TREPORT.")

            # Update the STUDYSTAT in TSTUDY
            cursor.execute(
                "UPDATE TSTUDY SET STUDYSTAT = :study_stat WHERE STUDY_KEY = :study_key",
                study_stat=4010,  # or the appropriate status value
                study_key=study_key
            )
            self.logger.debug("Updated STUDYSTAT in TSTUDY.")

            connection.commit()
            self.logger.info("TREPORTTEXT record inserted, TREPORT and TSTUDY updated successfully.")
        except Exception as e:
            self.logger.error(f"Failed to store transcribed report: {str(e)}")
            self.logger.debug(traceback.format_exc())
            # Rollback if commit failed or error occurred before commit
            if connection:
                try:
                    connection.rollback()
                    self.logger.info("Transaction rolled back due to error.")
                except Exception as rb_err:
                    self.logger.error(f"Error during rollback: {rb_err}")
        finally:
            # Close cursor and connection only if they were successfully created
            if cursor:
                try:
                    cursor.close()
                    self.logger.debug("Cursor closed.")
                except Exception as c_err:
                    self.logger.error(f"Error closing cursor: {c_err}")
            if connection:
                try:
                    connection.close()
                    self.logger.debug("Connection closed.")
                except Exception as conn_err:
                    self.logger.error(f"Error closing connection: {conn_err}")
