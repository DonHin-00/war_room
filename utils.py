import os
import fcntl
import logging
import math
import random
import collections
import json
import hashlib
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


def secure_create(file_path, data):
    """Create a file securely with 600 permissions and O_EXCL."""
    fd = os.open(file_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'w') as f:
        f.write(data)


def calculate_entropy(data):
    """Calculate the entropy of a string or bytes of data."""
    if len(data) == 0:
        return 0
    counter = collections.Counter(data)
    total_len = len(data)
    probabilities = [float(count) / total_len for count in counter.values()]
    entropy = -sum(p * math.log2(p) for p in probabilities)
    return entropy


def validate_state(state):
    """Validate the war state schema."""
    if not isinstance(state, dict):
        return False
    # Example schema: {'blue_alert_level': int}
    if 'blue_alert_level' in state:
        if not isinstance(state['blue_alert_level'], int):
            return False
        if not (1 <= state['blue_alert_level'] <= 5):
            return False
    return True


def setup_logging(log_file_path):
    """Set up logging to a specified file."""
    logging.basicConfig(filename=log_file_path,
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s:%(message)s')

MEMORY_CACHE = {}

def access_memory(filepath, data=None):
    """Atomic JSON I/O with read caching."""
    global MEMORY_CACHE

    # WRITE: Always write to disk if data is provided
    if data is not None:
        try:
            with open(filepath, 'w') as f: json.dump(data, f, indent=4)
            # Update cache timestamp to avoid immediate re-read
            if os.path.exists(filepath):
                 MEMORY_CACHE[filepath] = (os.path.getmtime(filepath), data)
        except: pass
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
                data = json.load(f)
                # Validation for state file
                if "war_state.json" in filepath and not validate_state(data):
                    return {}
                MEMORY_CACHE[filepath] = (mtime, data)
                return data
        except: return {}
    return {}

class AuditLogger:
    """Tamper-evident audit logger using hash chaining."""
    def __init__(self, filepath):
        self.filepath = filepath

    def log_event(self, actor, action, details):
        prev_hash = "00000000000000000000000000000000"

        # Read last line to get previous hash
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        last_entry = json.loads(lines[-1])
                        prev_hash = last_entry.get('curr_hash', prev_hash)
            except: pass

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
        except Exception as e:
            print(f"Audit Log Error: {e}")


def manage_session(session_id):
    """Manage a user session given a session ID."""
    # Placeholder for session management logic
    pass

def is_honeypot(filepath):
    """Check if a file is a known honeypot."""
    return filepath.endswith(".honey") or "decoy" in filepath

def is_tar_pit(filepath):
    """Check if a file is a tar pit (slows down read)."""
    return filepath.endswith(".tar_pit")
