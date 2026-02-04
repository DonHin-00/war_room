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
import stat  # Added import
from typing import Any, Union, List, Tuple, Deque

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

    # Check if it's a FIFO/Pipe (Tar Pit detection)
    if is_tar_pit(file_path):
        if is_friendly():
            return ""
        # Red Team might still attempt to read if they don't check first
        # But for 'safe_file_read' util, we must be safe.
        pass

    try:
        # Non-blocking open attempt for FIFO safety
        fd = os.open(file_path, os.O_RDONLY | os.O_NONBLOCK)
        with os.fdopen(fd, 'r') as file:
            data = file.read(4096) # Read max 4KB
            return data
    except OSError as e:
        if e.errno == errno.EAGAIN:
             return "" # Resource temporarily unavailable (locked/empty pipe)
        return ""
    except Exception:
        return ""

def safe_json_read(file_path: str) -> Any:
    """Read JSON data safely."""
    data = safe_file_read(file_path)
    if not data:
        return {}
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return {}

def safe_json_write(file_path: str, data: Any) -> None:
    """Write JSON data safely."""
    json_str = json.dumps(data, indent=4)
    safe_file_write(file_path, json_str)

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

# --- ADVANCED DEFENSE PRIMITIVES ---

def is_friendly() -> bool:
    """
    Determines if the current process is 'Friendly' (Blue Team/Admin).
    Uses checking of an environment variable or similar marker.
    """
    return os.environ.get("WAR_ROOM_ROLE") == "BLUE"

def create_tar_pit(filepath: str) -> None:
    """
    Creates a named pipe (FIFO) that acts as a Tar Pit.
    Reads will block indefinitely unless non-blocking I/O is used.
    """
    if os.path.exists(filepath):
        if is_tar_pit(filepath): return
        try: os.remove(filepath)
        except: return

    try:
        os.mkfifo(filepath)
    except OSError:
        pass

def is_tar_pit(filepath: str) -> bool:
    """Checks if a file is a FIFO/Named Pipe."""
    try:
        mode = os.stat(filepath).st_mode
        return stat.S_ISFIFO(mode)  # Corrected usage
    except OSError:
        return False

def create_logic_bomb(filepath: str) -> None:
    """
    Creates a 'zip bomb' style logic trap or a sparse file.
    """
    with open(filepath, 'w') as f:
        f.write("LOGIC_BOMB_ACTIVE_DO_NOT_READ")

class ExperienceReplay:
    """
    A ring buffer to store AI experiences for replay learning.
    """
    def __init__(self, capacity: int = 1000):
        self.buffer: Deque[Tuple] = collections.deque(maxlen=capacity)

    def push(self, state, action, reward, next_state):
        """Save a transition."""
        self.buffer.append((state, action, reward, next_state))

    def sample(self, batch_size: int) -> List[Tuple]:
        """Sample a batch of transitions."""
        if len(self.buffer) < batch_size:
            return list(self.buffer)
        return random.sample(self.buffer, batch_size)

    def __len__(self):
        return len(self.buffer)

def is_honeypot(filepath: str) -> bool:
    """
    Checks if a file is a known honeypot.
    """
    try:
        if is_tar_pit(filepath): return False
        return "sys_config.dat" in filepath or "shadow_backup" in filepath
    except:
        return False

def manage_session(session_id):
    """Manage a user session given a session ID."""
    # Placeholder for session management logic
    pass
