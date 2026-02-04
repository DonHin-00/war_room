import os
import fcntl
import logging
import math
import random
import json
import collections
import threading
import time
from typing import Dict, Any, Optional, Callable, Union

# Import trace logger
# Now that we are inside the utils package, we can import relatively
from .trace_logger import trace_errors

# Utility functions

def safe_file_write(file_path: str, data: str) -> None:
    """Write data to a file safely using locks."""
    try:
        # Use 'a+' to avoid truncation before lock
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

def safe_file_read(file_path: str) -> str:
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

@trace_errors
def atomic_json_io(filepath: str, data: Optional[Union[Dict[str, Any], Any]] = None) -> Union[Dict[str, Any], Any]:
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

@trace_errors
def atomic_json_update(filepath: str, update_func: Callable[[Dict[str, Any]], Dict[str, Any]]) -> Dict[str, Any]:
    """
    Atomically update a JSON file using a callback function.
    update_func(data) -> modified_data
    This prevents race conditions by holding the lock during the read-modify-write cycle.
    """
    try:
        # Use 'a+' to create if missing, but allows reading/seeking.
        # This prevents the race condition of checking exists() then opening 'w'.
        with open(filepath, 'a+') as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                f.seek(0)
                try:
                    content = f.read()
                    if content:
                        data = json.loads(content)
                    else:
                        data = {}
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

def atomic_json_merge(filepath: str, new_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Atomically merges new_data into the existing JSON file.
    This is a specialized version of atomic_json_update for merging dicts.
    """
    def merge(existing_data: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(existing_data, dict):
            existing_data = {}
        existing_data.update(new_data)
        return existing_data

    return atomic_json_update(filepath, merge)

class AuditLogger:
    """Logs critical simulation events to a JSONL file."""
    def __init__(self, filepath: str):
        self.filepath = filepath

    def log(self, agent: str, event: str, details: Dict[str, Any]):
        entry = {
            "timestamp": time.time(),
            "agent": agent,
            "event": event,
            "details": details
        }
        try:
            with open(self.filepath, 'a') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.write(json.dumps(entry) + "\n")
                f.flush()
                os.fsync(f.fileno())
                fcntl.flock(f, fcntl.LOCK_UN)
        except Exception:
            pass

def is_honeypot(filepath: str) -> bool:
    """Checks if a file is a known honeypot based on naming convention."""
    filename = os.path.basename(filepath)
    # Honeypot names usually mimic sensitive data
    decoy_names = ["passwords.txt", "config.yaml", "aws_keys.csv", "salary_report.xlsx"]
    return filename in decoy_names or filename.startswith("decoy_")

def calculate_entropy(data: bytes) -> float:
    """Calculate the entropy of a string of data (O(N) implementation)."""
    if not data:
        return 0.0

    counts = collections.Counter(data)
    length = len(data)

    entropy = 0.0
    for count in counts.values():
        p_x = float(count) / length
        if p_x > 0:
            entropy -= p_x * math.log2(p_x)

    return entropy

class EntropyCache:
    """Thread-safe cache for file entropy calculations."""
    def __init__(self):
        self.cache: Dict[tuple, float] = {}
        self.lock = threading.Lock()

    def get(self, filepath: str) -> float:
        try:
            stat = os.stat(filepath)
            key = (filepath, stat.st_mtime, stat.st_size)

            with self.lock:
                if key in self.cache:
                    return self.cache[key]

            # Not in cache, calculate
            entropy = calculate_file_entropy_uncached(filepath)

            with self.lock:
                # Basic eviction policy if cache grows too large
                if len(self.cache) > 1000:
                    self.cache.clear()
                self.cache[key] = entropy

            return entropy
        except FileNotFoundError:
            return 0.0

# Global cache instance
_entropy_cache = EntropyCache()

def calculate_file_entropy(filepath: str) -> float:
    """Public wrapper to use the global cache."""
    return _entropy_cache.get(filepath)

def calculate_file_entropy_uncached(filepath: str, chunk_size: int = 65536) -> float:
    """
    Calculate entropy of a file's content reading in chunks.
    This is memory efficient for large files.
    """
    try:
        counts = collections.Counter()
        total_len = 0
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                counts.update(chunk)
                total_len += len(chunk)

        if total_len == 0:
            return 0.0

        entropy = 0.0
        for count in counts.values():
            p_x = float(count) / total_len
            if p_x > 0:
                entropy -= p_x * math.log2(p_x)
        return entropy
    except:
        return 0.0

def setup_logging(log_file_path: str) -> None:
    """Set up logging to a specified file."""
    logging.basicConfig(filename=log_file_path,
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s:%(message)s')

def manage_session(session_id: str) -> None:
    """Manage a user session given a session ID."""
    # Placeholder for session management logic
    pass
