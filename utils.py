import os
import fcntl
import logging
import math
import random
import json
import time

# Utility functions

def safe_file_write(file_path, data):
    """Write data to a file safely using locks."""
    with open(file_path, 'w') as file:
        fcntl.flock(file, fcntl.LOCK_EX)
        file.write(data)
        fcntl.flock(file, fcntl.LOCK_UN)


def safe_file_read(file_path):
    """Read data from a file safely using locks."""
    with open(file_path, 'r') as file:
        fcntl.flock(file, fcntl.LOCK_SH)
        data = file.read()
        fcntl.flock(file, fcntl.LOCK_UN)
    return data


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

    session_dir = "sessions"
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

