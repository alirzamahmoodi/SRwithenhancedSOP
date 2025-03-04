import cx_Oracle
import logging
from datetime import datetime

class StoreTranscribedReport:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('detailed')

    def store_transcribed_report(self, study_key, report_content):
        self.logger.info(f"Storing transcribed report for study key: {study_key}")
        dsn = cx_Oracle.makedsn(self.config["ORACLE_HOST"], self.config["ORACLE_PORT"], self.config["ORACLE_SERVICE_NAME"])
        try:
            connection = cx_Oracle.connect(self.config["ORACLE_USERNAME"], self.config["ORACLE_PASSWORD"], dsn)
            cursor = connection.cursor()
            # Retrieve REPORT_KEY and REPORTER_KEY from TREPORT using the provided study_key.
            cursor.execute(
                "SELECT REPORT_KEY, REPORTER_KEY FROM TREPORT WHERE STUDY_KEY = :study_key",
                study_key=study_key
            )
            row = cursor.fetchone()
            if not row:
                self.logger.warning(f"No TREPORT record found for STUDY_KEY={study_key}")
                return
            report_key, reporter_key = row
            report_date = datetime.now().strftime('%Y%m%d%H%M%S')
            
            # Generate a new REPORT_TEXT_KEY using the existing sequence SEQ_TREPORTTEXT
            cursor.execute("SELECT SEQ_TREPORTTEXT.NEXTVAL FROM DUAL")
            report_text_key = cursor.fetchone()[0]
            
            # Insert the transcribed report into TREPORTTEXT
            insert_sql = """
            INSERT INTO TREPORTTEXT 
            (REPORT_TEXT_KEY, REPORT_KEY, REPORT_STAT, SRTEMPLATE_KEY, REPORTER_KEY, REPORT_DATE, REPORT_TYPE, REPORT_TEXT, CONCLUSION, FLAG, WFLAG)
            VALUES 
            (:report_text_key, :report_key, :report_stat, :srtemplate_key, :reporter_key, :report_date, :report_type, :report_text, :conclusion, :flag, :wflag)
            """
            cursor.execute(
                insert_sql,
                report_text_key=report_text_key,
                report_key=report_key,
                report_stat=4010,
                srtemplate_key=None,  # Replace with actual SRTEMPLATE_KEY if needed
                reporter_key=reporter_key,
                report_date=report_date,
                report_type="p",
                report_text=report_content,
                conclusion="",
                flag="N",
                wflag="N"
            )
            
            # Update the REPORT_STAT in TREPORT
            update_sql = """
            UPDATE TREPORT
            SET REPORT_STAT = :report_stat, MODIFY_DATE = :modify_date
            WHERE REPORT_KEY = :report_key
            """
            cursor.execute(
                update_sql,
                report_stat=4010,  # Replace with the appropriate status code
                modify_date=report_date,
                report_key=report_key
            )
            
            connection.commit()
            self.logger.info("TREPORTTEXT record inserted and TREPORT updated successfully.")
        except Exception as e:
            self.logger.error(f"Failed to store transcribed report: {str(e)}")
        finally:
            cursor.close()
            connection.close()
