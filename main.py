import sys
import yaml
from audio_transcriber import AudioTranscriber

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

if __name__ == "__main__":
    config = load_config("config.yaml")
    transcriber = AudioTranscriber(config["GEMINI_API_KEY"])
    
    # If a DICOM file path is provided as a command-line argument, process it.
    if len(sys.argv) > 1 and sys.argv[1].endswith(".dcm"):
        dcm_file = sys.argv[1]
        audio_path = transcriber.extract_audio(dcm_file)
        report_text = transcriber.transcribe(dcm_file, audio_path)
        if report_text:
            sr_path = transcriber.encapsulate_text_as_enhanced_sr(report_text, dcm_file)
            print(f"Enhanced SR saved to: {sr_path}")
    else:
        transcriber.process_spool_folder(config["PRIMARY_SPOOL_FOLDER"], config["PROCESSED_SPOOL_FOLDER"])
