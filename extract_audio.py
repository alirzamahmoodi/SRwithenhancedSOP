import pydicom
import numpy as np
from scipy.io.wavfile import write
import time
import os
import logging

class ExtractAudio:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('detailed')

    def extract_audio(self, dcm_path):
        self.logger.info(f"Extracting audio from DICOM file: {dcm_path}")
        retries = 5
        for attempt in range(retries):
            try:
                # Use the \\?\ prefix for long paths
                if len(dcm_path) > 260:
                    dcm_path = r"\\?\{}".format(dcm_path)
                ds = pydicom.dcmread(dcm_path)
                break  # If reading succeeds, exit the loop.
            except (PermissionError, OSError) as e:
                self.logger.warning(f"Error on attempt {attempt + 1} for file: {dcm_path}, error: {e}")
                if attempt < retries - 1:
                    time.sleep(1)  # Wait for 1 second before retrying.
                else:
                    self.logger.error(f"Unable to access file after {retries} attempts: {dcm_path}")
                    raise e
        else:
            # If the loop completes without breaking, raise an error
            raise OSError(f"Failed to read DICOM file after {retries} attempts: {dcm_path}")

        waveform = ds.WaveformSequence[0]
        audio_data = np.frombuffer(waveform.WaveformData, dtype=np.int16)
        wav_path = dcm_path.replace(".dcm", ".wav")
        write(wav_path, int(waveform.SamplingFrequency), audio_data)
        self.logger.info(f"Audio extracted and saved to: {wav_path}")
        return wav_path
