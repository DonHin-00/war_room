import os
import fcntl
import logging
import math
import random
import json
import time

# Utility functions

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def safe_file_write(file_path, data):
    """Write data to a file safely using locks."""
    # Use 'a+' to create if missing, but avoid truncating before lock
    with open(file_path, 'a+') as file:
        fcntl.flock(file, fcntl.LOCK_EX)
        file.seek(0)
        file.truncate()
        file.write(data)
        file.flush()
        fcntl.flock(file, fcntl.LOCK_UN)


def safe_file_read(file_path):
    """Read data from a file safely using locks."""
    # Use 'a+' to handle missing file gracefully if needed,
    # but 'r' is standard if we expect it to exist.
    # If we want to be robust against missing files like 'access_memory' was:
    if not os.path.exists(file_path):
        return ""
    with open(file_path, 'r') as file:
        fcntl.flock(file, fcntl.LOCK_SH)
        data = file.read()
        fcntl.flock(file, fcntl.LOCK_UN)
    return data


def safe_json_write(file_path, data):
    """Write JSON data to a file safely using locks."""
    try:
        json_str = json.dumps(data, indent=4)
        safe_file_write(file_path, json_str)
    except (TypeError, ValueError) as e:
        logging.error(f"Error serializing JSON to {file_path}: {e}")


def safe_json_read(file_path):
    """Read JSON data from a file safely using locks."""
    content = safe_file_read(file_path)
    if not content:
        return {}
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {}


def calculate_entropy(data):
    """Calculate the entropy of a string of data."""
    if len(data) == 0:
        return 0
    probabilities = [float(data.count(x)) / len(data) for x in set(data)]
    entropy = -sum(p * math.log2(p) for p in probabilities)
    return entropy


def setup_logging(log_file_path):
    """Set up logging to a specified file."""
    logging.basicConfig(filename=log_file_path,
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s:%(message)s')


def manage_session(session_id):
    """Manage a user session given a session ID."""
    if not isinstance(session_id, str) or not session_id.isalnum():
        raise ValueError("Invalid session_id. Must be alphanumeric.")

    session_dir = os.path.join(BASE_DIR, "sessions")
    try:
        os.makedirs(session_dir, exist_ok=True)
    except OSError as e:
        logging.error(f"Error creating session directory: {e}")
        return

    session_file = os.path.join(session_dir, f"session_{session_id}.json")

    try:
        # Open with 'a+' to create if not exists, but allow reading
        with open(session_file, 'a+') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.seek(0)
            content = f.read()

            try:
                data = json.loads(content) if content else {}
            except json.JSONDecodeError:
                data = {}

            if not data:
                data = {"session_id": session_id, "created_at": time.time(), "history": []}

            data['last_accessed'] = time.time()

            f.seek(0)
            f.truncate()
            json.dump(data, f)
            f.flush()
            # Lock is released when file is closed
            return data
    except IOError as e:
        logging.error(f"Error managing session {session_id}: {e}")

