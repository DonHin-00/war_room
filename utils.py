import os
import fcntl
import logging
import math
import random
import json
import sys
import hashlib

# Configure Logging for Utils
logger = logging.getLogger("Utils")

# Utility functions

def safe_file_write(file_path, data):
    """Write string data to a file safely using locks."""
    try:
        with open(file_path, 'w') as file:
            fcntl.flock(file, fcntl.LOCK_EX)
            file.write(data)
            fcntl.flock(file, fcntl.LOCK_UN)
        return True
    except Exception as e:
        logger.error(f"Failed to write file {file_path}: {e}")
        return False

def safe_file_read(file_path):
    """Read string data from a file safely using locks."""
    try:
        if not os.path.exists(file_path):
            return ""
        with open(file_path, 'r') as file:
            fcntl.flock(file, fcntl.LOCK_SH)
            data = file.read()
            fcntl.flock(file, fcntl.LOCK_UN)
        return data
    except Exception as e:
        logger.error(f"Failed to read file {file_path}: {e}")
        return ""

def secure_create(filepath, content, is_binary=False):
    """Securely create a file, failing if it exists (Atomic)."""
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    mode = 0o600
    try:
        fd = os.open(filepath, flags, mode)
        with os.fdopen(fd, 'wb' if is_binary else 'w') as f:
            f.write(content)
        return True
    except OSError:
        return False

def safe_json_write(file_path, data, write_checksum=False):
    """Write JSON data to a file safely using locks."""
    try:
        # Atomic write pattern: write to temp, flush, sync, rename?
        # Or just flock on the main file. Simpler for this scope is flock.
        with open(file_path, 'w') as file:
            fcntl.flock(file, fcntl.LOCK_EX)
            json.dump(data, file, indent=4)
            file.flush()
            os.fsync(file.fileno())
            fcntl.flock(file, fcntl.LOCK_UN)

        if write_checksum:
            checksum = calculate_checksum(data)
            safe_file_write(file_path + ".sha256", checksum)

        return True
    except TypeError as e:
        logger.error(f"JSON Serialization failed for {file_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to write JSON {file_path}: {e}")
        return False

def calculate_checksum(data_dict):
    """Calculate SHA256 checksum of a dictionary."""
    encoded = json.dumps(data_dict, sort_keys=True).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()

def safe_json_read(file_path, default=None, verify_checksum=False):
    """Read JSON data from a file safely using locks."""
    if default is None:
        default = {}

    if not os.path.exists(file_path):
        return default

    try:
        with open(file_path, 'r') as file:
            fcntl.flock(file, fcntl.LOCK_SH)
            # Handle empty files
            content = file.read()
            if not content.strip():
                fcntl.flock(file, fcntl.LOCK_UN)
                return default
            file.seek(0)
            data = json.load(file)
            fcntl.flock(file, fcntl.LOCK_UN)

        if verify_checksum:
            checksum_file = file_path + ".sha256"
            if os.path.exists(checksum_file):
                current_checksum = calculate_checksum(data)
                stored_checksum = safe_file_read(checksum_file).strip()
                if current_checksum != stored_checksum:
                    logger.error(f"INTEGRITY ERROR: Checksum mismatch for {file_path}!")
                    return default
            else:
                logger.warning(f"No checksum found for {file_path}, assuming first run.")

        return data
    except json.JSONDecodeError as e:
        logger.error(f"JSON Decode failed for {file_path}: {e}")
        return default
    except Exception as e:
        logger.error(f"Failed to read JSON {file_path}: {e}")
        return default

def calculate_entropy(data):
    """
    Calculate the Shannon entropy of a byte string or string.
    If string, converts to utf-8 bytes.
    """
    if not data:
        return 0

    if isinstance(data, str):
        data = data.encode('utf-8')

    if len(data) == 0:
        return 0

    entropy = 0
    for x in range(256):
        p_x = float(data.count(x.to_bytes(1, 'little'))) / len(data)
        if p_x > 0:
            entropy += - p_x * math.log(p_x, 2)

    return entropy

def validate_state(state):
    """Ensure state dictionary has valid types (Input Validation)."""
    if not isinstance(state, dict):
        return False
    if 'blue_alert_level' in state:
        val = state['blue_alert_level']
        if not isinstance(val, int) or val < 0:
            return False

    # Validate Timestamp/Sequence if present
    if 'timestamp' in state and not isinstance(state['timestamp'], (int, float)):
        return False

    return True

def check_root():
    """Fail if running as root."""
    if hasattr(os, 'getuid'):
        if os.getuid() == 0:
            sys.stderr.write("❌ SECURITY ERROR: Do not run this simulation as root!\n")
            sys.exit(1)

def setup_logging(name, log_file=None):
    """Set up logging."""
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

def get_directory_size_mb(path):
    """Calculate directory size in MB."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size / (1024 * 1024)

def check_disk_usage(path, max_mb):
    """Check if directory usage exceeds limit."""
    if get_directory_size_mb(path) > max_mb:
        return False
    return True
