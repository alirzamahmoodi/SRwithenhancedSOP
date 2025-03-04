import pydicom
import numpy as np
from scipy.io.wavfile import write
import time
import os
import logging

class ExtractAudio:
    def __init__(self, config):
        self.config = config

    def extract_audio(self, dcm_path):
        retries = 5
        for attempt in range(retries):
            try:
                ds = pydicom.dcmread(dcm_path)
                break  # If reading succeeds, exit the loop.
            except PermissionError:
                if attempt < retries - 1:
                    time.sleep(1)  # Wait for 1 second before retrying.
                else:
                    raise PermissionError(f"Unable to access file: {dcm_path}")
        waveform = ds.WaveformSequence[0]
        audio_data = np.frombuffer(waveform.WaveformData, dtype=np.int16)
        wav_path = dcm_path.replace(".dcm", ".wav")
        write(wav_path, int(waveform.SamplingFrequency), audio_data)
        return wav_path
