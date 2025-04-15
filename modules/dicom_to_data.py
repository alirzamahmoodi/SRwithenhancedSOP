import pydicom
import sys

# --- Configuration ---
# <<< Replace this with the actual path to the DICOM file you want to analyze >>>
dicom_file_path = 'C:\\Users\\02-06-06\\Desktop\\1.3.12.2.1107.5.2.30.63407.30000022010104591303100002071_11724.dcm'
# --- End Configuration ---

try:
    # Read the DICOM file, stopping before the pixel data for efficiency
    ds = pydicom.dcmread(dicom_file_path, stop_before_pixels=True)

    # Print the string representation of the dataset
    # This includes Tag, VR, Value, and Name for each element
    print(f"--- DICOM Header Dump Start: {dicom_file_path} ---")
    print(str(ds))
    print(f"--- DICOM Header Dump End: {dicom_file_path} ---")

except FileNotFoundError:
    print(f"Error: File not found at '{dicom_file_path}'", file=sys.stderr)
except Exception as e:
    print(f"Error reading DICOM file '{dicom_file_path}': {e}", file=sys.stderr)
