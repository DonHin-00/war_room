import os
import fcntl
import logging
import math
import random
import json
import shutil
import tempfile
import collections
import time
import errno
import stat
import hashlib
import resource
from typing import Any, Union, List, Tuple, Deque, Dict, Optional

# Add parent to path to import config for BASE_DIR validation
# Hacky, but utils needs context of allowed paths.
# Or we pass allowed paths.
# Best practice: Config defines paths, utils imports config.
import config

# Utility functions

def validate_path(path: str) -> bool:
    """
    Ensures the path is within allowed directories (BASE_DIR).
    Prevents Path Traversal.
    """
    try:
        resolved_path = os.path.realpath(path)
        base_dir = os.path.realpath(config.PATHS["BASE_DIR"])

        # Check if it starts with base_dir
        return resolved_path.startswith(base_dir)
    except:
        return False

def safe_file_write(file_path: str, data: str) -> None:
    """
    Write data to a file safely using locks and atomic move.
    """
    if not validate_path(file_path):
        raise PermissionError(f"Path traversal detected: {file_path}")

    dir_name = os.path.dirname(os.path.abspath(file_path))

    if not os.path.exists(dir_name):
        os.makedirs(dir_name, mode=0o700, exist_ok=True)

    temp_file = None
    try:
        with tempfile.NamedTemporaryFile('w', dir=dir_name, delete=False) as tf:
            temp_file = tf.name
            fcntl.flock(tf, fcntl.LOCK_EX)
            try:
                tf.write(data)
                tf.flush()
                os.fsync(tf.fileno())
                os.fchmod(tf.fileno(), 0o644)
            finally:
                fcntl.flock(tf, fcntl.LOCK_UN)
        os.replace(temp_file, file_path)
    except Exception as e:
        if temp_file and os.path.exists(temp_file):
            try: os.remove(temp_file)
            except: pass
        raise e


def safe_file_read(file_path: str, timeout: float = 1.0) -> str:
    """
    Read data from a file safely.
    """
    if not validate_path(file_path):
        # logging.warning(f"Path traversal blocked: {file_path}")
        return ""

    if not os.path.exists(file_path):
        return ""

    if is_tar_pit(file_path):
        if is_friendly():
            return ""
        pass

    try:
        fd = os.open(file_path, os.O_RDONLY | os.O_NONBLOCK)
        with os.fdopen(fd, 'r') as file:
            data = file.read(4096)
            return data if data is not None else ""
    except OSError as e:
        if e.errno == errno.EAGAIN:
             return ""
        return ""
    except Exception:
        return ""

def safe_json_read(file_path: str, default: Any = None) -> Any:
    """Read JSON data safely."""
    if default is None: default = {}
    if not validate_path(file_path): return default

    if not os.path.exists(file_path):
        return default

    for _ in range(3):
        data = safe_file_read(file_path)
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                pass
        time.sleep(0.01)

    try:
        corrupt_path = file_path + ".corrupt." + str(int(time.time()))
        shutil.copy(file_path, corrupt_path)
    except: pass

    return default

def safe_json_write(file_path: str, data: Any) -> None:
    """Write JSON data safely."""
    if not validate_path(file_path): return
    try:
        json_str = json.dumps(data, indent=4)
        safe_file_write(file_path, json_str)
    except TypeError:
        pass

def calculate_entropy(data: Union[str, bytes]) -> float:
    """Calculate the entropy of a string or bytes of data."""
    if not data:
        return 0.0

    if isinstance(data, str):
        data = data.encode('utf-8')

    counts = [0] * 256
    for byte in data:
        counts[byte] += 1

    total_len = len(data)
    entropy = 0.0

    for count in counts:
        if count > 0:
            p = float(count) / total_len
            entropy -= p * math.log2(p)

    return entropy

def generate_high_entropy_data(size: int = 1024) -> bytes:
    """Generates a block of high-entropy (random) data."""
    return os.urandom(size)

def rotate_log(log_path: str, max_bytes: int = 5 * 1024 * 1024):
    """Rotates log file if it exceeds max_bytes."""
    if not os.path.exists(log_path): return
    try:
        if os.path.getsize(log_path) > max_bytes:
            # Simple rotation: rename to .1, .2
            # Only keep 1 backup for simplicity in simulation
            backup = log_path + ".1"
            if os.path.exists(backup): os.remove(backup)
            os.rename(log_path, backup)
    except: pass

def setup_logging(log_file_path: str) -> None:
    """Set up logging to a specified file with rotation."""
    if not validate_path(log_file_path): return

    rotate_log(log_file_path)

    logging.basicConfig(filename=log_file_path,
                        level=logging.INFO,
                        format='%(asctime)s %(levelname)s:%(message)s')

# --- HEAVY MACHINERY ---

def limit_resources(ram_mb: int = 512, cpu_seconds: int = 600):
    """Enforce soft/hard limits on system resources."""
    try:
        limit = ram_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds + 30))
    except ValueError:
        pass

def scan_threats(file_path: str) -> bool:
    """Mock YARA scanner."""
    try:
        if is_tar_pit(file_path): return False
        content = safe_file_read(file_path, timeout=0.1)
        if not content: return False

        if "echo 'malware_payload'" in content: return True
        if "ENCRYPTED_HEADER_V1" in content: return True
        if ":HEARTBEAT" in content: return True
        return False
    except:
        return False

# --- ADVANCED DEFENSE PRIMITIVES ---

def is_friendly() -> bool:
    return os.environ.get("WAR_ROOM_ROLE") == "BLUE"

def create_tar_pit(filepath: str) -> None:
    if not validate_path(filepath): return
    if os.path.exists(filepath):
        if is_tar_pit(filepath): return
        try: os.remove(filepath)
        except: return
    try: os.mkfifo(filepath)
    except OSError: pass

def is_tar_pit(filepath: str) -> bool:
    try:
        mode = os.stat(filepath).st_mode
        return stat.S_ISFIFO(mode)
    except OSError: return False

def create_logic_bomb(filepath: str) -> None:
    if not validate_path(filepath): return
    with open(filepath, 'w') as f:
        f.write("LOGIC_BOMB_ACTIVE_DO_NOT_READ")

def is_honeypot(filepath: str) -> bool:
    try:
        if is_tar_pit(filepath): return False
        return "sys_config.dat" in filepath or "shadow_backup" in filepath or "honeypot" in filepath
    except: return False

# --- STATE MANAGEMENT ---

class StateManager:
    def __init__(self, state_file: str):
        self.state_file = state_file
        self.state_cache: Dict[str, Any] = {}
        self.state_mtime: float = 0.0

    def load_json(self, filepath: str) -> Dict[str, Any]:
        return safe_json_read(filepath)

    def save_json(self, filepath: str, data: Dict[str, Any]) -> None:
        safe_json_write(filepath, data)

    def get_war_state(self) -> Dict[str, Any]:
        if not os.path.exists(self.state_file):
            return {'blue_alert_level': 1}
        try:
            mtime = os.stat(self.state_file).st_mtime
            if mtime > self.state_mtime:
                self.state_cache = self.load_json(self.state_file)
                self.state_mtime = mtime
        except OSError: pass
        return self.state_cache

    def update_war_state(self, updates: Dict[str, Any]) -> None:
        current = self.load_json(self.state_file)
        current.update(updates)
        self.save_json(self.state_file, current)
        self.state_cache = current
        try:
            self.state_mtime = os.stat(self.state_file).st_mtime
        except OSError:
            self.state_mtime = time.time()

# --- OPS INFRASTRUCTURE ---

class AuditLogger:
    """Tamper-evident structured logger."""
    def __init__(self, log_path: str):
        self.log_path = log_path
        self.previous_hash = "0" * 64

        if not validate_path(log_path):
            raise PermissionError("Audit Log path unsafe")

        rotate_log(log_path) # Rotate on init
        self._recover_last_hash()

    def _recover_last_hash(self):
        if not os.path.exists(self.log_path): return
        try:
            with open(self.log_path, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_line = json.loads(lines[-1])
                    self.previous_hash = last_line.get("hash", "0" * 64)
        except: pass

    def log_event(self, actor: str, event_type: str, details: Dict[str, Any]):
        entry = {
            "timestamp": time.time(),
            "actor": actor,
            "type": event_type,
            "details": details,
            "previous_hash": self.previous_hash
        }

        entry_str = json.dumps(entry, sort_keys=True)
        current_hash = hashlib.sha256(entry_str.encode('utf-8')).hexdigest()
        entry["hash"] = current_hash

        self.previous_hash = current_hash

        try:
            with open(self.log_path, 'a') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.write(json.dumps(entry) + "\n")
                fcntl.flock(f, fcntl.LOCK_UN)
        except Exception: pass

def manage_session(session_id):
    """Manage a user session given a session ID."""
    pass
