import os
import fcntl
import logging
import math
import random
import json
import shutil
import tempfile
import collections
from typing import Any, Union, List, Tuple, Deque

# Utility functions

def safe_file_write(file_path: str, data: str) -> None:
    """
    Write data to a file safely using locks and atomic move.
    Ensure permissions are friendly (644) for shared access.
    """
    dir_name = os.path.dirname(os.path.abspath(file_path))

    # Create temp file in same directory to ensure atomic rename works
    # Use delete=False so we can chmod and rename
    with tempfile.NamedTemporaryFile('w', dir=dir_name, delete=False) as tf:
        # Lock temp file
        fcntl.flock(tf, fcntl.LOCK_EX)
        try:
            tf.write(data)
            tf.flush()
            os.fsync(tf.fileno())
            # Fix permissions to 644 (Owner: rw, Group: r, Other: r)
            # This is critical for War State shared file
            os.fchmod(tf.fileno(), 0o644)
        finally:
            fcntl.flock(tf, fcntl.LOCK_UN)

    # Atomic rename
    os.replace(tf.name, file_path)


def safe_file_read(file_path: str) -> str:
    """Read data from a file safely using locks."""
    if not os.path.exists(file_path):
        return ""

    with open(file_path, 'r') as file:
        fcntl.flock(file, fcntl.LOCK_SH)
        try:
            data = file.read()
        finally:
            fcntl.flock(file, fcntl.LOCK_UN)
    return data

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

    # Optimized calculation using list lookup
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
    Checks if a file is a potential honeypot based on naming convention.
    """
    filename = os.path.basename(filepath)
    return "honeypot" in filename or ".trap" in filename

def manage_session(session_id):
    """Manage a user session given a session ID."""
    # Placeholder for session management logic
    pass
