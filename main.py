import sys
import yaml
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from audio_transcriber import AudioTranscriber

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

class DicomCreatedHandler(FileSystemEventHandler):
    def __init__(self, transcriber, processed_folder):
        self.transcriber = transcriber
        self.processed_folder = processed_folder

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".dcm"):
            dcm_path = event.src_path
            print(f"New DICOM file detected: {dcm_path}")
            audio_path = self.transcriber.extract_audio(dcm_path)
            report_text = self.transcriber.transcribe(dcm_path, audio_path)
            if report_text:
                sr_path = self.transcriber.encapsulate_text_as_enhanced_sr(report_text, dcm_path)
                print(f"Enhanced SR saved to: {sr_path}")
                # Move the processed file
                filename = os.path.basename(dcm_path)
                os.rename(dcm_path, os.path.join(self.processed_folder, filename))

if __name__ == "__main__":
    config = load_config("config.yaml")
    transcriber = AudioTranscriber(config["GEMINI_API_KEY"], config["SR_OUTPUT_FOLDER"])
    
    # Process single file if provided via command-line argument.
    if len(sys.argv) > 1 and sys.argv[1].endswith(".dcm"):
        dcm_file = sys.argv[1]
        audio_path = transcriber.extract_audio(dcm_file)
        report_text = transcriber.transcribe(dcm_file, audio_path)
        if report_text:
            sr_path = transcriber.encapsulate_text_as_enhanced_sr(report_text, dcm_file)
            print(f"Enhanced SR saved to: {sr_path}")
    else:
        spool_folder = config["PRIMARY_SPOOL_FOLDER"]
        processed_folder = config["PROCESSED_SPOOL_FOLDER"]

        # Process any files already present.
        transcriber.process_spool_folder(spool_folder, processed_folder)

        # Set up folder watcher.
        event_handler = DicomCreatedHandler(transcriber, processed_folder)
        observer = Observer()
        observer.schedule(event_handler, spool_folder, recursive=False)
        observer.start()
        print("Service started. Watching for new DICOM files...")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
