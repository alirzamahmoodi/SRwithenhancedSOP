# Module: smb_connect

## Overview

This module handles the specific task of establishing authenticated connections to Windows network shares (SMB/CIFS) using UNC paths (e.g., `\\server\share\path`).

It is primarily used by `main.py` before accessing DICOM files that reside on network shares requiring credentials not already cached by the user session running the Python process.

## Functions

### `connect_to_share(unc_path, username, password)`

*   **Purpose:** Attempts to establish an authenticated connection to the network share specified within the `unc_path` using the provided `username` and `password`.
*   **Arguments:**
    *   `unc_path` (str): The full UNC path to a file or directory on the target share (e.g., `\\172.31.100.60\Longterm\path\file.dcm`). The function extracts the share root (`\\server\share`) from this path.
    *   `username` (str): The username for authentication. Should be in a format recognized by Windows (e.g., `DOMAIN\user`, `.\user` for local machine users, `user@domain.com`).
    *   `password` (str): The corresponding password for the user.
*   **Returns:**
    *   `True`: If the connection is successfully established, or if a potentially usable connection already exists (e.g., errors 85, 1202, 1219), or if the provided path is not a UNC path.
    *   `False`: If the connection attempt fails due to authentication errors (bad credentials - error 1326), network path errors (bad server/share name - error 53), or other unexpected errors.
*   **Details:**
    *   Uses the `win32wnet.WNetAddConnection2` function from the `pywin32` library.
    *   Connects to the share root (e.g., `\\172.31.100.60\Longterm`) extracted from the input `unc_path`.
    *   Uses the `win32netcon.CONNECT_UPDATE_PROFILE` flag to make the connection persistent for the current user session without requiring a drive letter mapping.
    *   Includes specific error handling for common Windows networking error codes.

## Dependencies

*   `pywin32`: Provides access to Windows API functions (`win32wnet`, `win32netcon`, `pywintypes`).
*   `logging`: For application logging.
*   `re`: For extracting the share root using regular expressions.

## Integration

*   Called conditionally within the `run_pipeline` function in `main.py` after the `final_path` is determined by `query.py` and before `extract_audio.py` (or any other module) attempts to access the `final_path`, *if* the path is a UNC path and `SHARE_USERNAME`/`SHARE_PASSWORD` are present in `config.yaml`. 