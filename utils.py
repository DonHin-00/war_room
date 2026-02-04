import os
import fcntl
import logging
import math
import random
import json
import collections

# Utility functions

def safe_file_write(file_path, data):
    """Write data to a file safely using locks."""
    try:
        with open(file_path, 'a+') as file:
            fcntl.flock(file, fcntl.LOCK_EX)
            file.seek(0)
            file.truncate()
            file.write(data)
            file.flush()
            os.fsync(file.fileno())
            fcntl.flock(file, fcntl.LOCK_UN)
    except Exception as e:
        logging.error(f"Error writing to {file_path}: {e}")

def safe_file_read(file_path):
    """Read data from a file safely using locks."""
    try:
        with open(file_path, 'r') as file:
            fcntl.flock(file, fcntl.LOCK_SH)
            data = file.read()
            fcntl.flock(file, fcntl.LOCK_UN)
        return data
    except Exception as e:
        logging.error(f"Error reading from {file_path}: {e}")
        return ""

def atomic_json_io(filepath, data=None):
    """
    Read or write JSON data atomically using file locks.
    WARNING: This does NOT prevent race conditions during Read-Modify-Write cycles.
    Use atomic_json_update for that.
    """
    if data is not None:
        try:
            with open(filepath, 'a+') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=4)
                f.flush()
                os.fsync(f.fileno())
                fcntl.flock(f, fcntl.LOCK_UN)
            return data # Return written data to avoid redundant read
        except Exception as e:
            # logging.error(f"Error atomic writing to {filepath}: {e}")
            return {}

    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                fcntl.flock(f, fcntl.LOCK_SH)
                try:
                    content = json.load(f)
                except json.JSONDecodeError:
                    content = {}
                fcntl.flock(f, fcntl.LOCK_UN)
                return content
        except Exception:
            return {}
    return {}

def atomic_json_update(filepath, update_func):
    """
    Atomically update a JSON file using a callback function.
    update_func(data) -> modified_data
    This prevents race conditions by holding the lock during the read-modify-write cycle.
    """
    try:
        # Ensure file exists
        if not os.path.exists(filepath):
             with open(filepath, 'w') as f: json.dump({}, f)

        with open(filepath, 'r+') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                f.seek(0)
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {}

                # Apply update
                new_data = update_func(data)

                # Write back
                f.seek(0)
                f.truncate()
                json.dump(new_data, f, indent=4)
                f.flush()
                os.fsync(f.fileno())
                return new_data
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
    except Exception as e:
        logging.error(f"Error atomic update {filepath}: {e}")
        return {}

def calculate_entropy(data):
    """Calculate the entropy of a string of data (O(N) implementation)."""
    if not data:
        return 0

    counts = collections.Counter(data)
    length = len(data)

    entropy = 0.0
    for count in counts.values():
        p_x = float(count) / length
        if p_x > 0:
            entropy -= p_x * math.log2(p_x)

    return entropy

def calculate_file_entropy(filepath):
    """Calculate entropy of a file's content."""
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
            return calculate_entropy(data)
    except:
        return 0

def setup_logging(log_file_path):
    """Set up logging to a specified file."""
    logging.basicConfig(filename=log_file_path,
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s:%(message)s')

def manage_session(session_id):
    """Manage a user session given a session ID."""
    # Placeholder for session management logic
    pass
