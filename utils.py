import os
import fcntl
import logging
import math
import json
import time

# --- LOGGING ---
def setup_logging(log_file_path):
    """Set up logging to a specified file."""
    logging.basicConfig(filename=log_file_path,
                        level=logging.INFO,
                        format='%(asctime)s %(levelname)s:%(message)s')

# --- FILE OPERATIONS ---
def ensure_directories(path):
    """Ensure the directory exists."""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

def safe_json_read(filepath):
    """Read JSON data from a file safely using locks."""
    if not os.path.exists(filepath):
        return {}

    try:
        with open(filepath, 'r') as file:
            fcntl.flock(file, fcntl.LOCK_SH)
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}
            fcntl.flock(file, fcntl.LOCK_UN)
        return data
    except Exception as e:
        logging.error(f"Error reading {filepath}: {e}")
        return {}

def safe_json_write(filepath, data):
    """Write JSON data to a file safely using locks."""
    try:
        # Open in append mode to avoid truncation before lock acquisition
        # 'a+' opens for reading and appending (writing at end of file).
        # The file is created if it does not exist.
        # The stream is positioned at the end of the file.
        with open(filepath, 'a+') as file:
            fcntl.flock(file, fcntl.LOCK_EX)
            file.seek(0)
            file.truncate()
            json.dump(data, file, indent=4)
            file.flush()
            os.fsync(file.fileno())
            fcntl.flock(file, fcntl.LOCK_UN)
        return True
    except Exception as e:
        logging.error(f"Error writing to {filepath}: {e}")
        return False

# --- UTILITIES ---
def calculate_entropy(filepath):
    """Detects High Entropy (Encrypted/Obfuscated) files."""
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
            if not data: return 0
            entropy = 0
            for x in range(256):
                p_x = float(data.count(x.to_bytes(1, 'little'))) / len(data)
                if p_x > 0:
                    entropy += - p_x * math.log(p_x, 2)
            return entropy
    except Exception as e:
        logging.warning(f"Error calculating entropy for {filepath}: {e}")
        return 0
