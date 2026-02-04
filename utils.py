import os
import fcntl
import logging
import math
import secrets
import collections
import json
import hashlib
import time
import socket
import traceback
import inspect
import zlib
from contextlib import contextmanager
from typing import Union, Dict, Any, Optional, List, Tuple

# Utility functions

FAKE_HEADERS = {
    'PDF': b'%PDF-1.5\n\x25\x25\x25\x25\n',
    'PNG': b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR',
    'JPG': b'\xff\xd8\xff\xe0\x00\x10JFIF',
    'GIF': b'GIF89a'
}

def obfuscate_payload(data: bytes, key: bytes, fake_type: str = 'PDF') -> bytes:
    """
    Compress, XOR encrypt, and prepend fake header.

    Args:
        data: Raw bytes to hide.
        key: Encryption key.
        fake_type: Header type to mimic (PDF, PNG, JPG, GIF).
    """
    # 1. Compress
    compressed = zlib.compress(data, level=9)

    # 2. XOR
    encrypted = bytearray([b ^ key[i % len(key)] for i, b in enumerate(compressed)])

    # 3. Prepend Header
    header = FAKE_HEADERS.get(fake_type, b'')
    return header + encrypted

def deobfuscate_payload(data: bytes, key: bytes, fake_type: str = 'PDF') -> bytes:
    """Strip header, XOR decrypt, and decompress."""
    header = FAKE_HEADERS.get(fake_type, b'')
    if data.startswith(header):
        raw_enc = data[len(header):]
    else:
        # Fallback if header missing or wrong type
        raw_enc = data

    # XOR
    compressed = bytearray([b ^ key[i % len(key)] for i, b in enumerate(raw_enc)])

    # Decompress
    try:
        return zlib.decompress(compressed)
    except zlib.error:
        return b""

def analyze_magic(data_head: bytes) -> str:
    """Identify file type from magic bytes."""
    for ftype, header in FAKE_HEADERS.items():
        if data_head.startswith(header):
            return ftype
    return "UNKNOWN"

def safe_bind_socket(host: str, port: int) -> socket.socket:
    """
    Create and bind a TCP socket safely with address reuse.

    Args:
        host: Bind address.
        port: Bind port.

    Returns:
        Bound socket object.

    Raises:
        OSError: If bind fails.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    return s

def safe_file_write(file_path: str, data: str) -> None:
    """
    Write data to a file safely using exclusive locks and 0o600 permissions.

    Args:
        file_path: Path to the file.
        data: String content to write.
    """
    try:
        # Open with O_CREAT so we can set permissions atomically on creation
        fd = os.open(file_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, 'w') as file:
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

def read_file_head(file_path: str, size: int = 4096) -> bytes:
    """
    Read the first N bytes of a file safely.

    Args:
        file_path: Path to the file.
        size: Number of bytes to read (default 4096).

    Returns:
        Bytes read from the file.
    """
    try:
        with open(file_path, 'rb') as f:
            return f.read(size)
    except OSError:
        return b""

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
    Uses safe_file_write for secure persistence.

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
            json_str = json.dumps(data, indent=4)
            safe_file_write(filepath, json_str)

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

class TraceLogger:
    """
    Deep Error Tracing System.
    Captures stack traces, local variables, and execution context on failure.
    """
    def __init__(self, filepath: str):
        self.filepath = filepath

    def capture_exception(self, exc: Exception, context: str = "GLOBAL") -> None:
        """
        Capture detailed exception info including stack frames and locals.

        Args:
            exc: The exception object.
            context: A string label for where this occurred.
        """
        timestamp = time.time()
        tb = traceback.extract_tb(exc.__traceback__)

        # Capture simplified stack frames
        stack_info = []
        for frame in tb:
            stack_info.append({
                "filename": frame.filename,
                "lineno": frame.lineno,
                "name": frame.name,
                "line": frame.line
            })

        # Capture locals from the frame where exception occurred (dangerous, sanitize!)
        locals_dump = {}
        try:
            # Get the traceback object, walk to the last frame
            ptr = exc.__traceback__
            while ptr.tb_next:
                ptr = ptr.tb_next

            # Inspect locals
            for k, v in ptr.tb_frame.f_locals.items():
                # Only capture basic types to avoid serialization errors or huge dumps
                if isinstance(v, (str, int, float, bool, list, dict)) and len(str(v)) < 1000:
                    locals_dump[k] = str(v)
                else:
                    locals_dump[k] = f"<{type(v).__name__}>"
        except:
            locals_dump = {"error": "Failed to capture locals"}

        report = {
            "timestamp": timestamp,
            "context": context,
            "exception_type": type(exc).__name__,
            "message": str(exc),
            "stack": stack_info,
            "locals": locals_dump
        }

        try:
            with open(self.filepath, 'a') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.write(json.dumps(report) + "\n")
                fcntl.flock(f, fcntl.LOCK_UN)
        except OSError: pass

    @contextmanager
    def context(self, name: str):
        """Context manager to auto-trace exceptions within a block."""
        try:
            yield
        except Exception as e:
            self.capture_exception(e, context=name)
            raise e


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

def is_safe_path(base_dir: str, path: str) -> bool:
    """
    Ensure path is within base_dir to prevent traversal attacks.

    Args:
        base_dir: The authorized directory.
        path: The path to check.

    Returns:
        True if safe, False otherwise.
    """
    # Resolve absolute paths
    base_abs = os.path.abspath(base_dir)
    path_abs = os.path.abspath(path)
    return path_abs.startswith(base_abs)
