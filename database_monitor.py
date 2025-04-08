import threading
import queue
import logging
import oracledb
import os
import sys
import subprocess
import time

class DatabaseMonitor:
    def __init__(self, config):
        self.config = config
        self.is_running = True
        self.queue = queue.Queue()
        self.poll_interval = 60  # seconds

    def worker(self):
        """Worker thread that processes study keys from the queue."""
        while self.is_running:
            try:
                study_key = self.queue.get(timeout=1)
            except queue.Empty:
                continue

            logging.info(f"Processing study key from queue: {study_key}")

            # Determine if running as compiled EXE or script
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
                args = [exe_path, str(study_key)]
            else:
                args = [
                    sys.executable,
                    os.path.join(os.path.dirname(__file__), "main.py"),
                    str(study_key)
                ]

            subprocess.run(args)
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

        while self.is_running:
            try:
                cursor = connection.cursor()
                query = "SELECT STUDY_KEY FROM TREPORT WHERE REPORT_STAT = 3010"
                cursor.execute(query)
                rows = cursor.fetchall()
                for row in rows:
                    study_key = row[0]
                    logging.info(f"Detected study {study_key} with REPORT_STAT '3010'. Adding to queue.")
                    self.queue.put(study_key)
                cursor.close()
                connection.commit()
            except Exception as e:
                logging.error(f"Error during monitoring: {e}")

            for _ in range(self.poll_interval):
                if not self.is_running:
                    break
                time.sleep(1)
        connection.close()
        logging.info("Monitor Database Service has stopped.")

    def stop_monitoring(self):
        self.is_running = False