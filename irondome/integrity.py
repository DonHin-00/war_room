import hashlib
import os
from .siem import siem_logger
import time

class FileIntegrityMonitor:
    def __init__(self, watch_dir):
        self.watch_dir = watch_dir
        self.hashes = {}
        self.scan_interval = 5

    def calculate_hash(self, filepath):
        hasher = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                buf = f.read()
                hasher.update(buf)
            return hasher.hexdigest()
        except:
            return None

    def build_baseline(self):
        siem_logger.log_event("FIM", "STARTUP", f"Building baseline for {self.watch_dir}", "INFO")
        for root, _, files in os.walk(self.watch_dir):
            if "logs" in root or "__pycache__" in root or ".git" in root: continue
            for file in files:
                path = os.path.join(root, file)
                self.hashes[path] = self.calculate_hash(path)
        siem_logger.log_event("FIM", "BASELINE_BUILT", f"Monitored {len(self.hashes)} files", "INFO")

    def scan(self):
        current_hashes = {}
        for root, _, files in os.walk(self.watch_dir):
            if "logs" in root or "__pycache__" in root or ".git" in root: continue
            for file in files:
                path = os.path.join(root, file)
                current_hashes[path] = self.calculate_hash(path)

        # Check for modifications
        for path, hash_val in self.hashes.items():
            if path not in current_hashes:
                siem_logger.log_event("FIM", "FILE_DELETED", f"File deleted: {path}", "CRITICAL")
            elif current_hashes[path] != hash_val:
                siem_logger.log_event("FIM", "FILE_MODIFIED", f"File modified: {path}", "CRITICAL")

        # Check for new files
        for path in current_hashes:
            if path not in self.hashes:
                siem_logger.log_event("FIM", "FILE_CREATED", f"New file detected: {path}", "WARNING")

        self.hashes = current_hashes
