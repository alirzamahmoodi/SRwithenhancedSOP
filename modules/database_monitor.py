import threading
import queue
import logging
import oracledb
import os
import sys
import subprocess
import time
from . import database_operations as db_ops # Import the MongoDB operations

class DatabaseMonitor:
    def __init__(self, config):
        self.config = config
        self.is_running = True
        self.queue = queue.Queue()
        self.poll_interval = 60  # seconds
        self.attempted_studies = set() # Track studies attempted in this session

    def worker(self):
        """Worker thread that processes study keys from the queue."""
        # Ensure config is passed or accessible for DB connection
        # db_ops.connect_db(self.config) # Connect once per worker if needed

        while self.is_running:
            try:
                study_key = self.queue.get(timeout=1)
            except queue.Empty:
                continue

            logging.info(f"Processing study key from queue: {study_key}")

            # The run_pipeline function (called via subprocess) now handles 
            # detailed status updates within its execution.
            # We already marked it as 'received' when adding to the queue.

            # Determine if running as compiled EXE or script
            main_script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "main.py"))
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
                args = [exe_path, str(study_key)]
            else:
                args = [
                    sys.executable,
                    main_script_path,
                    str(study_key)
                ]
            try:
                # Run the main script as a separate process
                # Consider capturing stdout/stderr if needed for detailed logging
                process = subprocess.run(args, check=True, capture_output=True, text=True)
                logging.info(f"Subprocess for {study_key} completed successfully.")
                logging.debug(f"Subprocess stdout: {process.stdout}")
                # Status is updated within the subprocess via run_pipeline
            except subprocess.CalledProcessError as e:
                logging.error(f"Subprocess for {study_key} failed with code {e.returncode}.")
                logging.error(f"Subprocess stderr: {e.stderr}")
                # Update status to error here as a fallback if the subprocess failed entirely
                db_ops.update_study_status(self.config, study_key, "error", error_message=f"Subprocess execution failed: {e.stderr[:500]}") # Truncate long errors
            except Exception as e:
                logging.error(f"Unexpected error running subprocess for {study_key}: {e}")
                db_ops.update_study_status(self.config, study_key, "error", error_message=f"Subprocess runner error: {str(e)}")

            self.queue.task_done()

    def start_monitoring(self):
        worker_thread = threading.Thread(target=self.worker, daemon=True)
        worker_thread.start()

        dsn = oracledb.makedsn(
            self.config["ORACLE_HOST"],
            self.config["ORACLE_PORT"],
            service_name=self.config["ORACLE_SERVICE_NAME"]
        )
        try:
            connection = oracledb.connect(
                user=self.config["ORACLE_USERNAME"],
                password=self.config["ORACLE_PASSWORD"],
                dsn=dsn
            )
            logging.info("Connected to Oracle database for monitoring.")
        except Exception as e:
            logging.error(f"Database connection failed: {e}")
            return

        # Ensure DB connection is available before monitoring loop
        if not db_ops.get_db(self.config):
             logging.error("MongoDB connection failed. Cannot start monitoring.")
             return

        while self.is_running:
            processed_keys_in_batch = set() # Track keys processed in this poll
            try:
                cursor = connection.cursor()
                # Ensure query uses correct table/column names from your Oracle DB
                query = "SELECT STUDY_KEY FROM TREPORT WHERE REPORT_STAT = 3010"
                cursor.execute(query)
                rows = cursor.fetchall()
                for row in rows:
                    study_key = row[0]
                    # Check if we already processed this key in this batch
                    if study_key not in processed_keys_in_batch and study_key not in self.attempted_studies:
                        logging.info(f"Detected study {study_key} with REPORT_STAT '3010'.")
                        # Update status to 'received' in MongoDB *before* adding to queue
                        # This prevents adding it again if monitoring restarts quickly
                        # It also provides an initial record for the dashboard
                        db_ops.update_study_status(self.config, study_key, "received")
                        self.queue.put(study_key)
                        processed_keys_in_batch.add(study_key)
                        self.attempted_studies.add(study_key)
                        logging.info(f"Added study {study_key} to processing queue.")
                    else:
                         logging.debug(f"Skipping study {study_key} already added in this batch.")

                cursor.close()
                # Commit might not be necessary for SELECT, depends on Oracle config/transactions
                # connection.commit()
            except Exception as e:
                logging.error(f"Error during monitoring query: {e}")
                # Consider specific error handling (e.g., reconnect attempt)

            for _ in range(self.poll_interval):
                if not self.is_running:
                    break
                time.sleep(1)
        connection.close()
        logging.info("Monitor Database Service has stopped.")

    def stop_monitoring(self):
        self.is_running = False