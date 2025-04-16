import threading
# import queue # No longer needed
import logging
import oracledb
import os
import sys
# import subprocess # No longer needed
import time
from . import database_operations as db_ops # Import the MongoDB operations
from . import processing_worker # Import the new worker module

class DatabaseMonitor:
    def __init__(self, config):
        self.config = config
        self.is_running = True
        # self.queue = queue.Queue() # No longer needed
        self.poll_interval = config.get("POLL_INTERVAL_SECONDS", 60) # Use config value or default
        self.attempted_studies = set() # Track studies attempted in this session
        self.logger = logging.getLogger('detailed') # Get the logger

    # def worker(self):
        # """Worker thread that processes study keys from the queue."""
        # This function is removed and replaced by direct calls to processing_worker.process_study
        # ... (old worker code removed) ...

    def start_monitoring(self):
        # worker_thread = threading.Thread(target=self.worker, daemon=True) # No longer needed
        # worker_thread.start()

        self.logger.info("Database monitoring starting.")

        dsn = oracledb.makedsn(
            self.config["ORACLE_HOST"],
            self.config["ORACLE_PORT"],
            service_name=self.config["ORACLE_SERVICE_NAME"]
        )
        connection = None # Initialize connection variable
        try:
            connection = oracledb.connect(
                user=self.config["ORACLE_USERNAME"],
                password=self.config["ORACLE_PASSWORD"],
                dsn=dsn
            )
            self.logger.info("Connected to Oracle database for monitoring.")
        except Exception as e:
            self.logger.error(f"Oracle database connection failed: {e}")
            return # Cannot monitor without DB connection

        # Ensure MongoDB connection is available before monitoring loop
        if not db_ops.get_db(self.config):
             self.logger.error("MongoDB connection failed. Cannot start monitoring.")
             if connection: connection.close() # Close Oracle connection if open
             return

        while self.is_running:
            processed_keys_in_batch = set() # Track keys processed in this poll
            try:
                with connection.cursor() as cursor:
                    # Ensure query uses correct table/column names from your Oracle DB
                    # TODO: Make query configurable?
                    query = "SELECT STUDY_KEY FROM TSTUDY WHERE STUDYSTAT = 3010"
                    self.logger.debug(f"Executing monitoring query: {query}")
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    self.logger.debug(f"Found {len(rows)} studies with status 3010.")
                    for row in rows:
                        study_key = row[0]
                        # Check if we already processed this key in this batch or session
                        if study_key not in processed_keys_in_batch and study_key not in self.attempted_studies:
                            self.logger.info(f"Detected new study {study_key} with STUDYSTAT '3010'.")
                            # Update status to 'received' in MongoDB *before* processing
                            db_ops.update_study_status(self.config, study_key, "received")
                            processed_keys_in_batch.add(study_key)
                            self.attempted_studies.add(study_key)
                            self.logger.info(f"Adding study {study_key} to attempted set and initiating processing.")

                            # --- Directly call the processing worker --- 
                            try:
                                # Call synchronously. The loop will wait here until process_study finishes.
                                processing_worker.process_study(self.config, study_key)
                                self.logger.info(f"Processing finished for study {study_key}. Continuing monitor loop.")
                            except Exception as process_err:
                                # Log any unexpected error during the call to process_study itself
                                self.logger.critical(f"Critical error during processing call for study {study_key}: {process_err}", exc_info=True)
                                # Update status to error as a last resort if process_study failed badly
                                db_ops.update_study_status(self.config, study_key, "error", error_message=f"Monitor failed to process: {str(process_err)[:200]}")
                            # --- End direct call --- 

                        else:
                             self.logger.debug(f"Skipping study {study_key} already attempted or added in this batch.")

                # Commit might not be necessary for SELECT, depends on Oracle config/transactions
                # connection.commit()
            except oracledb.Error as ora_err:
                self.logger.error(f"Oracle error during monitoring query: {ora_err}")
                # Consider specific error handling (e.g., reconnect attempt, exit)
                time.sleep(5) # Wait a bit before retrying
            except Exception as e:
                self.logger.error(f"Unexpected error during monitoring loop: {e}", exc_info=True)
                time.sleep(5) # Wait a bit before retrying

            self.logger.debug(f"Monitoring loop finished cycle. Waiting for {self.poll_interval} seconds.")
            # Wait for the poll interval, checking for stop signal periodically
            for _ in range(self.poll_interval):
                if not self.is_running:
                    break
                time.sleep(1)

        if connection:
            connection.close()
            self.logger.info("Oracle database connection closed.")
        self.logger.info("Monitor Database Service has stopped.")

    def stop_monitoring(self):
        self.logger.info("Stop signal received. Shutting down monitor...")
        self.is_running = False