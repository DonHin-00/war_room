import os
import fcntl
import json
import contextlib

@contextlib.contextmanager
def atomic_json_update(file_path, default=None):
    """Context manager for atomic Read-Modify-Write JSON operations."""
    if default is None: default = {}

    flags = os.O_RDWR | os.O_CREAT
    fd = os.open(file_path, flags, 0o600)
    f = os.fdopen(fd, 'r+')

    try:
        # Acquire Exclusive Lock immediately
        fcntl.flock(f, fcntl.LOCK_EX)

        # Read
        try:
            content = f.read()
            if content.strip():
                f.seek(0)
                data = json.load(f)
            else:
                data = default
        except Exception:
            data = default

        # Yield to caller for modification
        yield data

        # Write
        f.seek(0)
        f.truncate()
        json.dump(data, f, indent=4)
        f.flush()
        os.fsync(f.fileno())

    finally:
        fcntl.flock(f, fcntl.LOCK_UN)
        f.close()
