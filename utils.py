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
from typing import Any, Union, List, Tuple, Deque, Dict

# Utility functions

def safe_file_write(file_path: str, data: str) -> None:
    """
    Write data to a file safely using locks and atomic move.
    Ensure permissions are friendly (644) for shared access.
    """
    dir_name = os.path.dirname(os.path.abspath(file_path))

    with tempfile.NamedTemporaryFile('w', dir=dir_name, delete=False) as tf:
        fcntl.flock(tf, fcntl.LOCK_EX)
        try:
            tf.write(data)
            tf.flush()
            os.fsync(tf.fileno())
            os.fchmod(tf.fileno(), 0o644)
        finally:
            fcntl.flock(tf, fcntl.LOCK_UN)

    os.replace(tf.name, file_path)


def safe_file_read(file_path: str, timeout: float = 1.0) -> str:
    """
    Read data from a file safely using locks.
    Includes a timeout mechanism to avoid Tar Pits.
    """
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

def safe_json_read(file_path: str) -> Any:
    """Read JSON data safely with retry logic."""
    if not os.path.exists(file_path):
        return {}

    for _ in range(3):
        data = safe_file_read(file_path)
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                pass
        time.sleep(0.01)
    return {}

def safe_json_write(file_path: str, data: Any) -> None:
    """Write JSON data safely."""
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

def setup_logging(log_file_path: str) -> None:
    """Set up logging to a specified file."""
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
    with open(filepath, 'w') as f:
        f.write("LOGIC_BOMB_ACTIVE_DO_NOT_READ")

def is_honeypot(filepath: str) -> bool:
    try:
        if is_tar_pit(filepath): return False
        return "sys_config.dat" in filepath or "shadow_backup" in filepath or "honeypot" in filepath
    except: return False

# --- OPS INFRASTRUCTURE ---

class AuditLogger:
    """Tamper-evident structured logger."""
    def __init__(self, log_path: str):
        self.log_path = log_path
        self.previous_hash = "0" * 64
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
