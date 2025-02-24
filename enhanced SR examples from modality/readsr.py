import os
import pydicom
import contextlib

def print_dataset(ds, indent=0):
    """Recursively prints dataset elements with indentation for sequences, skipping unreadable binary data."""
    indent_str = "    " * indent
    for element in ds:
        try:
            name = element.name
        except Exception:
            name = str(element.tag)
        # Check for binary data and replace with a placeholder.
        if element.VR in ['OB', 'OW', 'UN'] and isinstance(element.value, bytes):
            value = f"<{len(element.value)} bytes of binary data>"
        else:
            value = element.value
        if element.VR == "SQ":  # If the element is a sequence, dive in further.
            print(f"{indent_str}{element.tag} {name} - Sequence ({len(element.value)} items)")
            for i, item in enumerate(element.value, 1):
                print(f"{indent_str}  Item {i}:")
                print_dataset(item, indent+2)
        else:
            print(f"{indent_str}{element.tag} {name}: {value}")

def process_file(filepath):
    try:
        ds = pydicom.dcmread(filepath)
        filename = os.path.basename(filepath)
        modality = ds.get("Modality", "Unknown")
        print(f"File: {filename}")
        print(f"Modality: {modality}")
        print("Dataset structure:")
        print_dataset(ds)
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

def main():
    folder = os.path.join(os.getcwd())  # Assumes current working directory is the folder
    dcm_files = [f for f in os.listdir(folder) if f.lower().endswith(".dcm")]
    
    print(f"Found {len(dcm_files)} DICOM file(s) in this folder.\n")
    
    for filename in dcm_files:
        filepath = os.path.join(folder, filename)
        output_filename = os.path.splitext(filename)[0] + "_output.txt"
        with open(output_filename, "w", encoding="utf-8") as outfile:
            with contextlib.redirect_stdout(outfile):
                print("========================================")
                process_file(filepath)
                print("========================================\n")
        print(f"Created output file: {output_filename}")

if __name__ == "__main__":
    main()