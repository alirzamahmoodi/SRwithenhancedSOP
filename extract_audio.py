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

        # Check if the file exists before proceeding.
        if not os.path.exists(dcm_path):
            self.logger.error(f"File does not exist: {dcm_path}")
            raise FileNotFoundError(f"File does not exist: {dcm_path}")

        # On Windows, apply the long path prefix if needed.
        if os.name == 'nt' and len(dcm_path) > 260:
            self.logger.debug("Applying long path prefix for Windows")
            dcm_path = r"\\?\{}".format(dcm_path)

        retries = 5
        ds = None
        for attempt in range(retries):
            try:
                ds = pydicom.dcmread(dcm_path)
                self.logger.info(f"DICOM file read successfully on attempt {attempt + 1}")
                break  # Exit loop on success.
            except FileNotFoundError as e:
                self.logger.error(f"File not found on attempt {attempt+1}: {dcm_path}")
                raise e
            except pydicom.errors.InvalidDicomError as e:
                self.logger.error(f"Invalid DICOM file on attempt {attempt+1}: {dcm_path}, error: {e}")
                raise e
            except (PermissionError, OSError) as e:
                self.logger.warning(f"Error on attempt {attempt + 1} reading file: {dcm_path}, error: {e}")
                if attempt < retries - 1:
                    time.sleep(1)  # Wait before retrying.
                else:
                    self.logger.error(f"Unable to access file after {retries} attempts: {dcm_path}")
                    raise e
        if ds is None:
            raise OSError(f"Failed to read DICOM file after {retries} attempts: {dcm_path}")

        # Check if the DICOM contains a WaveformSequence.
        if not hasattr(ds, 'WaveformSequence') or not ds.WaveformSequence:
            self.logger.error("DICOM file does not contain a WaveformSequence.")
            raise AttributeError("DICOM file does not contain a WaveformSequence.")

        try:
            waveform = ds.WaveformSequence[0]
            self.logger.info("Waveform extracted from DICOM file.")
        except Exception as e:
            self.logger.error("Failed to extract waveform from WaveformSequence.")
            raise e

        # Verify that waveform data exists.
        if not hasattr(waveform, 'WaveformData'):
            self.logger.error("Waveform data is missing in the DICOM file.")
            raise AttributeError("Waveform data is missing in the DICOM file.")

        audio_data = np.frombuffer(waveform.WaveformData, dtype=np.int16)

        # Verify that the sampling frequency is available.
        if not hasattr(waveform, 'SamplingFrequency'):
            self.logger.error("Sampling frequency not found in the waveform data.")
            raise AttributeError("Sampling frequency not found in the waveform data.")

        try:
            # Generate the output WAV path.
            wav_path = dcm_path.replace(".dcm", ".wav")
            write(wav_path, int(waveform.SamplingFrequency), audio_data)
            self.logger.info(f"Audio extracted and saved to: {wav_path}")
        except Exception as e:
            self.logger.error(f"Failed to write WAV file: {e}")
            raise e

        return wav_path
