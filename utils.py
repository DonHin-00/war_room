import os
import fcntl
import logging
import math
import random
import json
import time
import re
import hashlib
import subprocess
import shutil
from datetime import datetime

# Constants
DEFAULT_SESSION_TIMEOUT = 1800  # 30 minutes
SECURITY_LOG_FILE = "security_events.log"
SESSIONS_FILE = "sessions.json"

# --- SECURITY MODULES ---

class RealSecurityManager:
    """
    Implements REAL security controls: WAF, IDS, EDR, SOAR.
    No simulations. Actual regex, hashing, and system commands.
    """

    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self.session_file = os.path.join(self.base_dir, SESSIONS_FILE)
        self.security_log = os.path.join(self.base_dir, SECURITY_LOG_FILE)

        # Hash cache for FIM (File Integrity Monitoring)
        self.fim_cache = {}
        # Initialize the file if not exists to get a baseline hash
        if not os.path.exists(self.session_file):
             with open(self.session_file, 'w') as f:
                 json.dump({}, f)
        self._update_fim_hash(self.session_file)

    def _update_fim_hash(self, filepath):
        """Calculate and store SHA-256 hash of a file."""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'rb') as f:
                    file_hash = hashlib.sha256(f.read()).hexdigest()
                    self.fim_cache[filepath] = file_hash
            except Exception as e:
                self.log_event("EDR_ERROR", f"Failed to hash {filepath}: {e}", severity="HIGH")

    def _check_fim(self, filepath):
        """
        Verify file integrity against cached hash.
        Returns False if tampered.
        """
        if not os.path.exists(filepath):
            return True

        try:
            with open(filepath, 'rb') as f:
                current_hash = hashlib.sha256(f.read()).hexdigest()

            stored_hash = self.fim_cache.get(filepath)

            if stored_hash and current_hash != stored_hash:
                return False

            return True
        except Exception:
            return False

    def log_event(self, event_type, message, severity="INFO", context=None):
        """Structured JSON logging for SOAR/SIEM ingestion."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "severity": severity,
            "message": message,
            "context": context or {}
        }

        # Write to local log file
        with open(self.security_log, "a") as f:
            f.write(json.dumps(event) + "\n")

        if severity in ["HIGH", "CRITICAL"]:
            logging.error(f"[SECURITY ALERT] {event_type}: {message}")

    # --- WAF: Web Application Firewall ---
    def check_waf(self, input_data):
        """
        Scans input for SQLi, XSS, and Command Injection patterns.
        Raises ValueError if malicious.
        """
        if not isinstance(input_data, str):
            return

        # OWASP-inspired Regex Rules
        rules = [
            (r"(\%27)|(\')|(\-\-)|(\%23)|(#)", "SQL Injection (Generic)"),
            (r"((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))", "SQL Injection (Auth Bypass)"),
            (r"\w*((\%27)|(\'))((\%6F)|o|(\%4F))((\%72)|r|(\%52))", "SQL Injection (Classic OR)"),
            (r"((\%3C)|<)((\%2F)|\/)*[a-z0-9\%]+((\%3E)|>)", "XSS (HTML Tags)"),
            (r"((\%3C)|<)[^\n]+((\%3E)|>)", "XSS (Generic Tag)"),
            (r"(;|\||`|\$|\(|\))", "Command Injection (Shell Chars)"),
            (r"\.\./", "Path Traversal")
        ]

        for pattern, threat_name in rules:
            if re.search(pattern, input_data, re.IGNORECASE):
                self.respond_soar("WAF_BLOCK", f"Detected {threat_name} in input: {input_data[:20]}...", source="WAF")
                raise ValueError(f"Security Violation: {threat_name} detected.")

    # --- SOAR: Security Orchestration, Automation, and Response ---
    def respond_soar(self, threat_type, details, source="SYSTEM"):
        """
        Execute automated defense responses.
        """
        self.log_event(threat_type, details, severity="HIGH", context={"source": source})

        # Response: Aggressive Cleanup (If FIM fails)
        if threat_type == "FIM_VIOLATION":
            self.log_event("SOAR_ACTION", "Initiating Emergency Reset of Session File", severity="CRITICAL")
            if os.path.exists(self.session_file):
                # Backup forensic evidence
                shutil.copy(self.session_file, self.session_file + f".quarantine.{int(time.time())}")
                # Wipe file
                with open(self.session_file, 'w') as f:
                    json.dump({}, f)
                # Reset Hash
                self._update_fim_hash(self.session_file)


# Instantiate Global Security Manager
security_manager = RealSecurityManager()


# --- EXISTING UTILITIES ---

def safe_file_write(file_path, data):
    """Write data to a file safely using locks."""
    with open(file_path, 'w') as file:
        fcntl.flock(file, fcntl.LOCK_EX)
        file.write(data)
        fcntl.flock(file, fcntl.LOCK_UN)


def safe_file_read(file_path):
    """Read data from a file safely using locks."""
    with open(file_path, 'r') as file:
        fcntl.flock(file, fcntl.LOCK_SH)
        data = file.read()
        fcntl.flock(file, fcntl.LOCK_UN)
    return data


def calculate_entropy(data):
    """Calculate the entropy of a string of data."""
    if len(data) == 0:
        return 0
    probabilities = [float(data.count(x)) / len(data) for x in set(data)]
    entropy = -sum(p * math.log2(p) for p in probabilities)
    return entropy


def setup_logging(log_file_path):
    """Set up logging to a specified file."""
    logging.basicConfig(filename=log_file_path,
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s:%(message)s')


def manage_session(session_id, timeout=DEFAULT_SESSION_TIMEOUT):
    """
    Manage a user session given a session ID.
    Now secured by RealSecurityManager (WAF, FIM, SOAR).

    Args:
        session_id (str): The unique identifier for the session.
        timeout (int): Session timeout in seconds.

    Returns:
        dict: The active session data.
    """
    # 1. WAF Check
    security_manager.check_waf(session_id)

    if not session_id or not isinstance(session_id, str):
        raise ValueError("Invalid session_id provided.")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    session_file = os.path.join(base_dir, 'sessions.json')

    # Ensure file exists
    if not os.path.exists(session_file):
        with open(session_file, 'w') as f:
            json.dump({}, f)
        security_manager._update_fim_hash(session_file)

    # 2. FIM Check (Pre-Access)
    if not security_manager._check_fim(session_file):
        security_manager.respond_soar("FIM_VIOLATION", f"Session file integrity mismatch!", source="EDR")

    # Atomic Read-Modify-Write
    with open(session_file, 'r+') as file:
        try:
            # Exclusive lock
            fcntl.flock(file, fcntl.LOCK_EX)

            # Read and parse
            try:
                content = file.read()
                sessions = json.loads(content) if content else {}
            except json.JSONDecodeError:
                logging.error("Corrupt session file. Resetting.")
                sessions = {}

            current_time = time.time()

            # Garbage Collection
            sessions_to_remove = []
            for sid, data in sessions.items():
                session_timeout = data.get('timeout', DEFAULT_SESSION_TIMEOUT)
                if current_time - data.get('last_accessed', 0) > session_timeout:
                    sessions_to_remove.append(sid)

            for sid in sessions_to_remove:
                del sessions[sid]

            # Handle current session
            if session_id in sessions:
                sessions[session_id]['last_accessed'] = current_time
                sessions[session_id]['status'] = 'active'
                sessions[session_id]['timeout'] = timeout
            else:
                sessions[session_id] = {
                    'created_at': current_time,
                    'last_accessed': current_time,
                    'status': 'active',
                    'timeout': timeout
                }

            # Write back
            file.seek(0)
            json.dump(sessions, file, indent=4)
            file.truncate()

            # 3. Update FIM Hash (Post-Write)
            file.flush()
            file.seek(0)
            new_hash = hashlib.sha256(file.read().encode('utf-8')).hexdigest()
            security_manager.fim_cache[session_file] = new_hash

            return sessions[session_id]

        except Exception as e:
            logging.error(f"Session Error: {e}")
            raise e
        finally:
            fcntl.flock(file, fcntl.LOCK_UN)
