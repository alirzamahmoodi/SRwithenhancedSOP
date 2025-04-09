import logging
import win32wnet
import win32netcon
import pywintypes
import re

def connect_to_share(unc_path, username, password):
    """
    Establishes a connection to a network share using provided credentials.

    Args:
        unc_path (str): The full UNC path to a file or directory on the share.
        username (str): The username for authentication (e.g., 'DOMAIN\\user', '.\\user').
        password (str): The password for authentication.

    Returns:
        bool: True if connection succeeded or already exists, False otherwise.
    """
    if not unc_path or not unc_path.startswith('\\'):
        logging.debug(f"Path '{unc_path}' is not a UNC path. No connection needed.")
        return True # Not a UNC path, so connection is implicitly successful

    # Extract the share root (\\server\share) from the full path
    match = re.match(r"^(\\\\[^\\]+\\[^\\]+)", unc_path)
    if not match:
        logging.error(f"Could not extract share root from UNC path: {unc_path}")
        return False
    share_root = match.group(1)

    logging.info(f"Attempting connection to network share: {share_root}")

    try:
        # Define the network resource
        nr = win32wnet.NETRESOURCE()
        nr.dwType = win32netcon.RESOURCETYPE_DISK
        nr.lpRemoteName = share_root
        # nr.lpLocalName = None  # No drive letter mapping needed

        # Attempt to add the connection
        # CONNECT_UPDATE_PROFILE ensures the connection is persistent for the user session
        # but doesn't require mapping a drive letter.
        win32wnet.WNetAddConnection2(nr, password, username, win32netcon.CONNECT_UPDATE_PROFILE)
        logging.info(f"Successfully established connection to {share_root}")
        return True

    except pywintypes.error as e:
        # Error codes reference: https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes
        # ERROR_ALREADY_ASSIGNED (85) or ERROR_SESSION_CREDENTIAL_CONFLICT (1219)
        # often mean a connection exists, possibly with different credentials.
        # ERROR_DEVICE_ALREADY_REMEMBERED (1202) can mean a persistent connection exists.
        if e.winerror in (85, 1219, 1202):
            logging.warning(f"Connection to {share_root} likely already exists or conflicts: {e.strerror} (Code: {e.winerror}). Assuming access is possible.")
            # It's often okay to proceed if a connection already exists
            return True
        # ERROR_LOGON_FAILURE (1326) - Bad username/password
        elif e.winerror == 1326:
            logging.error(f"Authentication failed for {share_root} with username '{username}'. Check credentials. Error: {e.strerror}")
            return False
        # ERROR_BAD_NETPATH (53) - Network path not found
        elif e.winerror == 53:
             logging.error(f"Network path not found: {share_root}. Check server/share name. Error: {e.strerror}")
             return False
        else:
            logging.error(f"Failed to connect to {share_root}: {e.strerror} (Code: {e.winerror})")
            return False
    except Exception as e:
        logging.error(f"An unexpected error occurred during network share connection to {share_root}: {e}")
        return False

# Example usage (for testing):
# if __name__ == '__main__':
#     import yaml
#     try:
#         with open('../config.yaml', 'r') as f:
#             config = yaml.safe_load(f)
#     except FileNotFoundError:
#         print("config.yaml not found in parent directory for testing.")
#         exit()

#     test_path = r"\\172.31.100.60\Longterm\some\test\file.dcm" # Replace with a valid path on your share
#     user = config.get('SHARE_USERNAME')
#     pwd = config.get('SHARE_PASSWORD')

#     if user and pwd:
#         if connect_to_share(test_path, user, pwd):
#             print(f"Connection to share seems successful (or already exists).")
#             # Try accessing the path now, e.g., os.path.exists(test_path)
#         else:
#             print(f"Failed to connect to the share.")
#     else:
#         print("SHARE_USERNAME or SHARE_PASSWORD not found in config.yaml") 