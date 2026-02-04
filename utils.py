import os
import fcntl
import logging
import math
import random
import collections
import json
import hashlib
import time
from typing import Union, Dict, Any, Optional, List, Tuple

# Utility functions

def safe_file_write(file_path: str, data: str) -> None:
    """
    Write data to a file safely using exclusive locks.

    Args:
        file_path: Path to the file.
        data: String content to write.
    """
    try:
        with open(file_path, 'w') as file:
            fcntl.flock(file, fcntl.LOCK_EX)
            file.write(data)
            fcntl.flock(file, fcntl.LOCK_UN)
    except OSError as e:
        logging.error(f"Failed to write to {file_path}: {e}")


def safe_file_read(file_path: str) -> Optional[str]:
    """
    Read data from a file safely using shared locks.

    Args:
        file_path: Path to the file.

    Returns:
        The file content as string, or None if error.
    """
    try:
        with open(file_path, 'r') as file:
            fcntl.flock(file, fcntl.LOCK_SH)
            data = file.read()
            fcntl.flock(file, fcntl.LOCK_UN)
        return data
    except OSError as e:
        logging.error(f"Failed to read from {file_path}: {e}")
        return None


def secure_create(file_path: str, data: str) -> None:
    """
    Create a file securely with 0o600 permissions and O_EXCL to prevent race conditions.

    Args:
        file_path: Path to the new file.
        data: Content to write.
    """
    try:
        fd = os.open(file_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w') as f:
            f.write(data)
    except OSError as e:
        logging.error(f"Secure create failed for {file_path}: {e}")


def calculate_entropy(data: Union[str, bytes]) -> float:
    """
    Calculate the Shannon entropy of a string or bytes.

    Args:
        data: Input data.

    Returns:
        Entropy value (float).
    """
    if not data:
        return 0.0
    counter = collections.Counter(data)
    total_len = len(data)
    probabilities = [float(count) / total_len for count in counter.values()]
    entropy = -sum(p * math.log2(p) for p in probabilities)
    return entropy


def validate_state(state: Dict[str, Any]) -> bool:
    """
    Validate the war state schema.

    Args:
        state: Dictionary representing the state.

    Returns:
        True if valid, False otherwise.
    """
    if not isinstance(state, dict):
        return False
    # Example schema: {'blue_alert_level': int}
    if 'blue_alert_level' in state:
        if not isinstance(state['blue_alert_level'], int):
            return False
        if not (1 <= state['blue_alert_level'] <= 5):
            return False
    return True


def setup_logging(log_file_path: str) -> None:
    """
    Set up logging to a specified file.

    Args:
        log_file_path: Path to the log file.
    """
    logging.basicConfig(filename=log_file_path,
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s:%(message)s')

MEMORY_CACHE: Dict[str, Tuple[float, Any]] = {}

def access_memory(filepath: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Atomic JSON I/O with read caching based on mtime.

    Args:
        filepath: Path to the JSON file.
        data: Data to write (optional). If provided, performs a write.

    Returns:
        The loaded data (on read) or empty dict (on write or error).
    """
    global MEMORY_CACHE

    # WRITE: Always write to disk if data is provided
    if data is not None:
        try:
            with open(filepath, 'w') as f: json.dump(data, f, indent=4)
            # Update cache timestamp to avoid immediate re-read
            if os.path.exists(filepath):
                 MEMORY_CACHE[filepath] = (os.path.getmtime(filepath), data)
        except (OSError, TypeError) as e:
            logging.error(f"Memory Write Error {filepath}: {e}")
        return {}

    # READ: Check modification time
    if os.path.exists(filepath):
        try:
            mtime = os.path.getmtime(filepath)
            if filepath in MEMORY_CACHE:
                cached_mtime, cached_data = MEMORY_CACHE[filepath]
                if mtime == cached_mtime:
                    return cached_data

            # File changed or not in cache, read it
            with open(filepath, 'r') as f:
                try:
                    data_loaded = json.load(f)
                except json.JSONDecodeError:
                    # Retry once after a brief sleep (simulating spinlock waiting for a concurrent write to finish)
                    time.sleep(0.1)
                    with open(filepath, 'r') as f2:
                        data_loaded = json.load(f2)

                # Validation for state file
                if "war_state.json" in filepath and not validate_state(data_loaded):
                    logging.warning(f"Invalid state detected in {filepath}")
                    return {}

                MEMORY_CACHE[filepath] = (mtime, data_loaded)
                return data_loaded
        except (OSError, json.JSONDecodeError) as e:
            # logging.error(f"Memory Read Error {filepath}: {e}") # Reduce log noise for expected race
            return {}
    return {}

class AuditLogger:
    """Tamper-evident audit logger using hash chaining."""
    def __init__(self, filepath: str):
        self.filepath = filepath

    def log_event(self, actor: str, action: str, details: str) -> None:
        """
        Log an event securely with hash chaining.

        Args:
            actor: The entity performing the action (RED/BLUE).
            action: The action name.
            details: Description of the action.
        """
        prev_hash = "00000000000000000000000000000000"

        # Read last line to get previous hash
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        last_entry = json.loads(lines[-1])
                        prev_hash = last_entry.get('curr_hash', prev_hash)
            except (OSError, json.JSONDecodeError):
                pass

        timestamp = time.time()
        entry_str = f"{timestamp}:{actor}:{action}:{details}:{prev_hash}"
        curr_hash = hashlib.sha256(entry_str.encode()).hexdigest()

        entry = {
            'timestamp': timestamp,
            'actor': actor,
            'action': action,
            'details': details,
            'prev_hash': prev_hash,
            'curr_hash': curr_hash
        }

        # Secure atomic append
        try:
            with open(self.filepath, 'a') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.write(json.dumps(entry) + "\n")
                fcntl.flock(f, fcntl.LOCK_UN)
        except OSError as e:
            logging.error(f"Audit Log Error: {e}")


def manage_session(session_id: str) -> None:
    """
    Manage a user session given a session ID.

    Args:
        session_id: The session identifier.
    """
    # Placeholder for session management logic
    pass

def is_honeypot(filepath: str) -> bool:
    """Check if a file is a known honeypot."""
    return filepath.endswith(".honey") or "decoy" in filepath

def is_tar_pit(filepath: str) -> bool:
    """Check if a file is a tar pit (slows down read)."""
    return filepath.endswith(".tar_pit")
