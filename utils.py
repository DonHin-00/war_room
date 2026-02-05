import os
import fcntl
import logging
import math
import random
import json
import time

# Constants
DEFAULT_SESSION_TIMEOUT = 1800  # 30 minutes

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


def manage_session(session_id, timeout=DEFAULT_SESSION_TIMEOUT):
    """
    Manage a user session given a session ID.

    Args:
        session_id (str): The unique identifier for the session.
        timeout (int): Session timeout in seconds (default: 30 minutes).

    Returns:
        dict: The active session data.
    """
    if not session_id or not isinstance(session_id, str):
        raise ValueError("Invalid session_id provided.")

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

            # Garbage Collection: Remove expired sessions
            # Use stored timeout if available, otherwise default
            sessions_to_remove = []
            for sid, data in sessions.items():
                session_timeout = data.get('timeout', DEFAULT_SESSION_TIMEOUT)
                if current_time - data.get('last_accessed', 0) > session_timeout:
                    sessions_to_remove.append(sid)

            for sid in sessions_to_remove:
                del sessions[sid]

            # Handle current session
            if session_id in sessions:
                # If existing session, check if it's expired based on its own timeout
                # (Double check in case GC logic above missed it or logic changes)
                session_data = sessions[session_id]
                session_timeout = session_data.get('timeout', DEFAULT_SESSION_TIMEOUT)

                # Update last_accessed and ensure status
                sessions[session_id]['last_accessed'] = current_time
                sessions[session_id]['status'] = 'active'

                # If the caller provided a NEW timeout, should we update it?
                # Usually session parameters are set on creation, but updating it allows extending/shortening on the fly.
                # Let's update it to respect the current caller's intent.
                sessions[session_id]['timeout'] = timeout

            else:
                # Create new session (either new user or expired/cleaned up)
                sessions[session_id] = {
                    'created_at': current_time,
                    'last_accessed': current_time,
                    'status': 'active',
                    'timeout': timeout
                }

            # Write back
            file.seek(0)
            json.dump(sessions, file, indent=4)
            file.truncate()

            return sessions[session_id]

        finally:
            # Always unlock
            fcntl.flock(file, fcntl.LOCK_UN)
