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
    base_dir = os.path.dirname(os.path.abspath(__file__))
    session_file = os.path.join(base_dir, 'sessions.json')

    # Ensure file exists
    if not os.path.exists(session_file):
        with open(session_file, 'w') as f:
            json.dump({}, f)

    # Atomic Read-Modify-Write
    with open(session_file, 'r+') as file:
        try:
            # Exclusive lock to prevent race conditions
            fcntl.flock(file, fcntl.LOCK_EX)

            # Read and parse
            try:
                content = file.read()
                sessions = json.loads(content) if content else {}
            except json.JSONDecodeError:
                # Handle corrupt file by resetting or logging
                logging.error("Corrupt session file. Resetting.")
                sessions = {}

            current_time = time.time()

            if session_id in sessions:
                sessions[session_id]['last_accessed'] = current_time
                # Could add expiration logic here
            else:
                sessions[session_id] = {
                    'created_at': current_time,
                    'last_accessed': current_time,
                    'status': 'active'
                }

            # Write back
            file.seek(0)
            json.dump(sessions, file, indent=4)
            file.truncate()

            return sessions[session_id]

        finally:
            # Always unlock
            fcntl.flock(file, fcntl.LOCK_UN)
