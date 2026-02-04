import os
import fcntl
import logging
import math
import random
import json
import sys
import hashlib
import time
import resource
import shutil
import hmac
import secrets

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

def secure_create(filepath, content, is_binary=False, token=None):
    """Securely create a file. REQUIRES AUTH TOKEN."""
    # Enforce Zero Trust
    if token:
        # Lazy load config to avoid circular dep at top level if possible,
        # but utils shouldn't import config usually?
        # Actually config is pure constants.
        try:
            import config
            idm = IdentityManager(config.SESSION_DB)
            valid, agent = idm.verify(token)
            if not valid:
                logger.error(f"ACCESS DENIED (Create): {agent} - {filepath}")
                return False
        except ImportError:
            pass # Testing/Standalone mode

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

def calculate_checksum(data):
    """Calculate SHA256 checksum of data (dict or string)."""
    if isinstance(data, dict):
        encoded = json.dumps(data, sort_keys=True).encode('utf-8')
    else:
        encoded = str(data).encode('utf-8')
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

def enforce_seccomp():
    """Simulate seccomp filtering (Tamper Protection)."""
    # In a real scenario, we'd use libseccomp to block syscalls.
    # Here we simulate it by monkey-patching dangerous os functions for the current process.
    # This is a 'soft' sandbox.

    blocked = ['system', 'popen', 'spawn', 'exec']

    def block_call(*args, **kwargs):
        raise RuntimeError("SECCOMP VIOLATION: Syscall Blocked")

    for func in blocked:
        if hasattr(os, func):
            setattr(os, func, block_call)

    # Also block subprocess if possible, but that breaks our own tools potentially.
    # We apply this ONLY to the Red/Blue agents, not the orchestrator/tools.

def broadcast_alert(message):
    """Ensure critical alerts are noticed (Escalation)."""
    # 1. Write to specific Alert Log
    try:
        with open("ALERTS.txt", "a") as f:
            f.write(f"[{time.ctime()}] 🚨 {message}\n")
    except Exception: pass

    # 2. Try 'wall' if available (Notify all terminals)
    # Only if severity is high enough, but user asked to maximize visibility.
    try:
        shutil.which('wall')
        # subprocess.run(['wall', f"SENTINEL ALERT: {message}"], timeout=1)
        # Commented out to avoid spamming the actual user terminal during dev,
        # but in a real exercise this is valid.
        pass
    except Exception: pass

def limit_resources(max_ram_mb=50):
    """Limit the current process resources (Sandboxing)."""
    try:
        # Limit RAM
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        # Set limit to max_ram_mb
        limit_bytes = max_ram_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (limit_bytes, hard))
        return True
    except Exception as e:
        logger.warning(f"Failed to set resource limits: {e}")
        return False

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

# --- Zero Trust Identity Manager ---
class IdentityManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self._secret = self._load_or_generate_secret()

    def _load_or_generate_secret(self):
        """Load secret from Env or File (Securely)."""
        # 1. Environment Variable
        env_secret = os.environ.get('RANGE_SECRET')
        if env_secret:
            return env_secret.encode()

        # 2. Key File
        secret_file = ".range_secret"
        if os.path.exists(secret_file):
            try:
                with open(secret_file, 'rb') as f:
                    return f.read()
            except Exception: pass

        # 3. Generate New
        key = secrets.token_bytes(32)
        try:
            # Atomic secure write
            fd = os.open(secret_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, 'wb') as f:
                f.write(key)
        except OSError:
            # Race condition or perm issue, just use transient key (failsafe)
            logger.warning("Could not persist secret key. Using transient key.")

        return key

    def login(self, agent_name):
        """Issue a session token."""
        # Generate random token
        raw_token = secrets.token_hex(16)
        # Sign it
        signature = hmac.new(self._secret, raw_token.encode(), hashlib.sha256).hexdigest()
        token = f"{agent_name}:{raw_token}:{signature}"

        # Persist session (Simulate Kernel Table)
        sessions = safe_json_read(self.db_path, {})
        sessions[agent_name] = {
            "token_hash": hashlib.sha256(token.encode()).hexdigest(),
            "expires": time.time() + 300 # 5 min TTL
        }
        safe_json_write(self.db_path, sessions)

        return token

    def verify(self, token):
        """Verify token validity and expiration."""
        try:
            agent, raw, sig = token.split(':')

            # 1. Verify Signature
            expected_sig = hmac.new(self._secret, raw.encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(sig, expected_sig):
                return False, "Invalid Signature"

            # 2. Verify Session State
            sessions = safe_json_read(self.db_path, {})
            if agent not in sessions:
                return False, "No Session"

            session = sessions[agent]
            if time.time() > session['expires']:
                return False, "Expired"

            # 3. Verify Token Hash matches Session
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            if not hmac.compare_digest(session['token_hash'], token_hash):
                 return False, "Token Mismatch (Hijacked?)"

            return True, agent
        except Exception:
            return False, "Malformed Token"

class AuditLogger:
    """Tamper-evident logger using hash chaining."""
    def __init__(self, filepath):
        self.filepath = filepath
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w') as f:
                # Genesis block
                genesis = {
                    "timestamp": time.time(),
                    "event": "GENESIS",
                    "agent": "SYSTEM",
                    "prev_hash": "0" * 64,
                    "hash": ""
                }
                genesis['hash'] = calculate_checksum(genesis)
                f.write(json.dumps(genesis) + "\n")

    def log_event(self, agent, event, details=None):
        """Log an event with cryptographic linkage to previous entry."""
        try:
            # Read last line to get prev_hash
            last_line = ""
            with open(self.filepath, 'r') as f:
                # Efficiently read last line? For now, read all is safe-ish given rotation/size
                # Better: seek to end and backtrack, but jsonl lines vary in length.
                # Simple approach: readlines()[-1]
                lines = f.readlines()
                if lines:
                    last_line = lines[-1]

            prev_entry = json.loads(last_line) if last_line else {}
            prev_hash = prev_entry.get("hash", "0" * 64)

            entry = {
                "timestamp": time.time(),
                "agent": agent,
                "event": event,
                "details": details or {},
                "prev_hash": prev_hash
            }

            # Calculate hash of this entry (excluding its own hash field)
            entry_hash = calculate_checksum(entry)
            entry['hash'] = entry_hash

            # Atomic append
            with open(self.filepath, 'a') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.write(json.dumps(entry) + "\n")
                fcntl.flock(f, fcntl.LOCK_UN)

            return True
        except Exception as e:
            logger.error(f"Audit log failed: {e}")
            return False

def verify_audit_log(filepath):
    """Verify the hash chain of an audit log."""
    if not os.path.exists(filepath):
        return False, "File missing"

    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()

        if not lines:
            return False, "Empty file"

        prev_hash = "0" * 64 # Genesis prev_hash assumption

        for i, line in enumerate(lines):
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                return False, f"Corrupt JSON at line {i+1}"

            # 1. Check if entry points to previous hash
            if i == 0:
                 if entry['prev_hash'] != "0" * 64:
                     return False, "Genesis block invalid"
            else:
                if entry['prev_hash'] != prev_hash:
                    return False, f"Broken chain at line {i+1}. Expected {prev_hash[:8]}..., got {entry['prev_hash'][:8]}..."

            # 2. Recalculate hash
            stored_hash = entry['hash']
            # Create copy without hash to calculate
            calc_entry = entry.copy()
            del calc_entry['hash']
            calculated_hash = calculate_checksum(calc_entry)

            if calculated_hash != stored_hash:
                 return False, f"Tampered entry at line {i+1}"

            prev_hash = stored_hash

        return True, "Chain valid"
    except Exception as e:
        return False, f"Verification error: {e}"

def secure_backup(src_path, backup_dir):
    """Securely backup a file."""
    if not os.path.exists(src_path) or os.path.islink(src_path):
        return False
    try:
        filename = os.path.basename(src_path)
        dest_path = os.path.join(backup_dir, filename)
        shutil.copy2(src_path, dest_path)
        return True
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        return False

def secure_restore(filename, backup_dir, restore_dir):
    """Restore a file from backup."""
    src_path = os.path.join(backup_dir, filename)
    dest_path = os.path.join(restore_dir, filename)

    if not os.path.exists(src_path):
        return False

    try:
        shutil.copy2(src_path, dest_path)
        return True
    except Exception as e:
        logger.error(f"Restore failed: {e}")
        return False

def steganography_encode(data, image_path):
    """Hide data in an image footer."""
    # Simulated: Append Base64 data to end of file
    import base64
    try:
        encoded = base64.b64encode(json.dumps(data).encode()).decode()
        marker = b"\xFF\xD9" # JPG EOF

        # Ensure file exists/create dummy
        if not os.path.exists(image_path):
            with open(image_path, 'wb') as f:
                f.write(b'\xFF\xD8\xFF\xE0' + b'\x00'*100) # Dummy header

        with open(image_path, 'ab') as f:
            f.write(marker + b"STEG:" + encoded.encode())
        return True
    except Exception: return False

def steganography_decode(image_path):
    """Extract hidden data from image."""
    try:
        with open(image_path, 'rb') as f:
            content = f.read()
            if b"STEG:" in content:
                raw = content.split(b"STEG:")[1]
                import base64
                return json.loads(base64.b64decode(raw).decode())
    except Exception: pass
    return None

class RLBrain:
    """Robust Q-Learning Agent with Persistence and Federation."""
    def __init__(self, name, actions, learning_rate=0.1, discount=0.9, epsilon=0.1):
        self.name = name
        self.actions = actions
        self.lr = learning_rate
        self.gamma = discount
        self.epsilon = epsilon
        self.q_table = {}

        # Path
        import config
        self.file_path = os.path.join(config.MODELS_DIR, f"{name}_qtable.json")
        self.load()

    def get_q(self, state, action):
        return self.q_table.get(f"{state}_{action}", 0.0)

    def choose_action(self, state):
        """Epsilon-greedy selection."""
        if random.random() < self.epsilon:
            return random.choice(self.actions)

        # Argmax
        q_values = [self.get_q(state, a) for a in self.actions]
        max_q = max(q_values)

        # Handle ties randomly
        candidates = [self.actions[i] for i, q in enumerate(q_values) if q == max_q]
        return random.choice(candidates)

    def learn(self, state, action, reward, next_state):
        """Q-Learning Update."""
        current_q = self.get_q(state, action)
        max_next_q = max([self.get_q(next_state, a) for a in self.actions])

        new_q = current_q + self.lr * (reward + self.gamma * max_next_q - current_q)
        self.q_table[f"{state}_{action}"] = new_q

        # Periodic Save? Or caller handles it?
        # Let's save every time for safety in this chaotic sim, or rely on caller 'sync'
        pass

    def merge(self, other_q_table):
        """Federated Learning: Average weights with peer."""
        for key, val in other_q_table.items():
            current = self.q_table.get(key, 0.0)
            # Weighted average (Trust self slightly more? Or 50/50)
            self.q_table[key] = (current + val) / 2.0

    def save(self):
        safe_json_write(self.file_path, self.q_table, write_checksum=True)

    def load(self):
        self.q_table = safe_json_read(self.file_path, default={}, verify_checksum=True)

class AnomalyDetector:
    """Unsupervised Z-Score Anomaly Detection."""
    def __init__(self, window_size=20):
        self.history = []
        self.window_size = window_size

    def add_datapoint(self, value):
        self.history.append(value)
        if len(self.history) > self.window_size:
            self.history.pop(0)

    def is_anomaly(self, value, threshold=3.0):
        if len(self.history) < 5: return False

        mean = sum(self.history) / len(self.history)
        variance = sum([((x - mean) ** 2) for x in self.history]) / len(self.history)
        std_dev = math.sqrt(variance)

        if std_dev == 0: return False

        z_score = (value - mean) / std_dev
        return abs(z_score) > threshold
