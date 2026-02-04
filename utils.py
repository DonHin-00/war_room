import os
import fcntl
import logging
import math
import random
import json
import time
import hashlib
import resource
import sys
from db_manager import DatabaseManager

# Singleton DB Access
DB = DatabaseManager()

# Utility functions

try:
    from config import PATHS
    BASE_DIR = PATHS['BASE_DIR']
except ImportError:
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
    """Write JSON data to a file safely using locks. Deprecated: Use DB."""
    # Kept for backward compatibility or simple file ops
    try:
        json_str = json.dumps(data, indent=4)
        safe_file_write(file_path, json_str)
        # Update checksum
        checksum = hashlib.sha256(json_str.encode()).hexdigest()
        safe_file_write(file_path + ".checksum", checksum)
    except (TypeError, ValueError) as e:
        logging.error(f"Error serializing JSON to {file_path}: {e}")


def safe_json_read(file_path):
    """Read JSON data from a file safely using locks. Deprecated: Use DB."""
    content = safe_file_read(file_path)
    if not content:
        return {}

    # Verify checksum if it exists
    checksum_file = file_path + ".checksum"
    if os.path.exists(checksum_file):
        expected = safe_file_read(checksum_file).strip()
        actual = hashlib.sha256(content.encode()).hexdigest()
        if expected and expected != actual:
            logging.error(f"Integrity check failed for {file_path}! Discarding corrupted data.")
            return {}

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        logging.warning(f"Corrupted JSON in {file_path}: {e}. Resetting.")
        return {}

# --- DB Wrappers for Q-Learning ---
class QTableManager:
    def __init__(self, agent_name):
        self.agent = agent_name
        self.db = DB
        # Cache for performance, write-back
        self.cache = {}

    def get(self, state, action):
        key = f"{state}_{action}"
        if key in self.cache:
            return self.cache[key]
        val = self.db.get_q_value(self.agent, state, action)
        self.cache[key] = val
        return val

    def update(self, state, action, value):
        self.cache[f"{state}_{action}"] = value
        # In high-perf, we might buffer this. For now, direct write.
        # optimization: periodic sync?
        pass # We rely on sync()

    def sync(self):
        """Flush cache to DB."""
        for key, val in self.cache.items():
            try:
                state, action = key.rsplit('_', 1)
                self.db.update_q_value(self.agent, state, action, val)
            except: pass

def validate_state(state):
    """Validate and repair the war state."""
    required_keys = {'blue_alert_level'}
    if not isinstance(state, dict):
        return {'blue_alert_level': 1}

    for key in required_keys:
        if key not in state:
            state[key] = 1

    # Ensure types
    try:
        state['blue_alert_level'] = int(state['blue_alert_level'])
    except (ValueError, TypeError):
        state['blue_alert_level'] = 1

    # Clamp values
    if state['blue_alert_level'] < 1: state['blue_alert_level'] = 1
    if state['blue_alert_level'] > 5: state['blue_alert_level'] = 5

    return state


def calculate_entropy(data):
    """Calculate the entropy of a string of data."""
    if len(data) == 0:
        return 0
    probabilities = [float(data.count(x)) / len(data) for x in set(data)]
    entropy = -sum(p * math.log2(p) for p in probabilities)
    return entropy

def calculate_checksum(file_path):
    """Calculate SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        return None


def setup_logging(log_file_path):
    """Set up logging to a specified file."""
    logging.basicConfig(filename=log_file_path,
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s:%(message)s')


def manage_session(session_id):
    """Manage a user session given a session ID."""
    if not isinstance(session_id, str) or not session_id.isalnum():
        raise ValueError("Invalid session_id. Must be alphanumeric.")

    try:
        from config import PATHS
        session_dir = PATHS['SESSIONS_DIR']
    except ImportError:
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

class AuditLogger:
    def __init__(self):
        try:
            from config import PATHS
            self.log_file = PATHS['AUDIT_LOG']
        except ImportError:
            self.log_file = os.path.join(BASE_DIR, "audit.jsonl")

    def log_event(self, actor, action, target, details=None):
        """Log an event to the immutable audit log."""
        event = {
            "timestamp": time.time(),
            "actor": actor,
            "action": action,
            "target": target,
            "details": details or {},
            "hash": self._calculate_hash(actor, action, target)
        }

        try:
            with open(self.log_file, 'a') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.write(json.dumps(event) + "\n")
                fcntl.flock(f, fcntl.LOCK_UN)
        except Exception as e:
            logging.error(f"Failed to write audit log: {e}")

    def _calculate_hash(self, actor, action, target):
        """Simple hash chain (mock) for integrity."""
        # In a real system, we'd include the previous hash.
        raw = f"{time.time()}:{actor}:{action}:{target}"
        return hashlib.sha256(raw.encode()).hexdigest()

def limit_resources():
    """Limit CPU and Memory usage to prevent runaway AI."""
    # Limit CPU time to 60 seconds (Soft) / 120 seconds (Hard) per process
    # Note: In a real long-running sim, we might want this higher or disabled.
    # For this demo, it prevents infinite loops locking the container.
    try:
        # resource.setrlimit(resource.RLIMIT_CPU, (60, 120))
        pass # Disabled for now to allow long-running dash session
    except ValueError:
        pass

    # Limit Memory to 512MB
    try:
        limit = 512 * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    except ValueError:
        pass

def check_disk_usage(limit_mb=100):
    """Ensure simulation doesn't fill the disk."""
    try:
        from config import PATHS
        battlefield = PATHS['BATTLEFIELD']
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(battlefield):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)

        if total_size > limit_mb * 1024 * 1024:
            logging.warning("Battlefield size limit reached! Cleaning up...")
            # Emergency cleanup
            for f in os.listdir(battlefield):
                try: os.remove(os.path.join(battlefield, f))
                except: pass
    except Exception as e:
        logging.error(f"Disk check failed: {e}")
