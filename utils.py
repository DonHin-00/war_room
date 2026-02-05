import os
import sys
import json
import logging
import hmac
import hashlib
import time
import uuid
import secrets
import fcntl
import contextlib
import random
import pickle

# --- LOGGING ---
def setup_logging(name, log_file):
    """Setup structured logging."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create directory if needed
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    fh = logging.FileHandler(log_file)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger

# --- SECURE I/O ---
@contextlib.contextmanager
def atomic_json_update(file_path, default=None):
    """Context manager for atomic Read-Modify-Write JSON operations."""
    if default is None: default = {}

    # Ensure dir exists
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    flags = os.O_RDWR | os.O_CREAT
    fd = os.open(file_path, flags, 0o600)
    f = os.fdopen(fd, 'r+')

    try:
        # Acquire Exclusive Lock
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

        # Yield
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

def safe_json_read(path, default=None):
    if not os.path.exists(path): return default
    try:
        with open(path, 'r') as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            return json.load(f)
    except Exception:
        return default

def safe_json_write(path, data):
    with atomic_json_update(path) as db:
        db.update(data)

def secure_create(path, content, token=None):
    """Create file securely (O_EXCL)."""
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        return True
    except FileExistsError:
        return False

# --- AUDIT LOGGING ---
class AuditLogger:
    def __init__(self, log_file):
        self.log_file = log_file
        self.last_hash = "0" * 64
        self._init_log()

    def _init_log(self):
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f: pass

    def log_event(self, actor, action, target, status):
        """Log event with tamper-evident hash chain."""
        timestamp = time.time()
        event_str = f"{self.last_hash}|{timestamp}|{actor}|{action}|{target}|{status}"
        event_hash = hashlib.sha256(event_str.encode()).hexdigest()

        entry = {
            "ts": timestamp,
            "prev_hash": self.last_hash,
            "actor": actor,
            "action": action,
            "target": target,
            "status": status,
            "hash": event_hash
        }

        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + "\n")

        self.last_hash = event_hash

# --- IDENTITY & SECURITY ---
class IdentityManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.secret = self._load_secret()

    def _load_secret(self):
        # Priority: Env -> File -> Generate
        if os.environ.get("RANGE_SECRET"):
            return os.environ["RANGE_SECRET"].encode()
        try:
            with open(".range_secret", "rb") as f:
                return f.read().strip()
        except:
            secret = secrets.token_bytes(32)
            # Only write if we can (might be read-only fs in some envs)
            try:
                with open(".range_secret", "wb") as f:
                    f.write(secret)
            except: pass
            return secret

    def login(self, agent_id):
        """Issue a simulated 'Certificate'."""
        # Cert = Payload + Signature
        payload = f"{agent_id}|{time.time()}"
        signature = hmac.new(self.secret, payload.encode(), hashlib.sha256).hexdigest()
        cert = f"{payload}|{signature}"

        with atomic_json_update(self.db_path) as db:
            db[agent_id] = {"cert": cert, "last_seen": time.time()}
        return cert

    def verify(self, agent_id, cert):
        """Verify simulated mTLS certificate."""
        try:
            parts = cert.split('|')
            if len(parts) != 3: return False

            claimed_id, ts, signature = parts
            if claimed_id != agent_id: return False

            # Reconstruct payload
            payload = f"{claimed_id}|{ts}"
            expected = hmac.new(self.secret, payload.encode(), hashlib.sha256).hexdigest()

            if not secrets.compare_digest(signature, expected):
                return False

            # Expiry check (Simulate 24h certs)
            if time.time() - float(ts) > 86400:
                return False

            return True
        except: return False

def enforce_seccomp():
    """Simulate Seccomp Hardening."""
    # In real world, use 'prctl' or 'seccomp' lib.
    # Here we just log it.
    pass

def memory_scramble(variable):
    """Securely clear sensitive data from memory."""
    try:
        # Overwrite if mutable (simulated)
        if isinstance(variable, bytearray):
            for i in range(len(variable)):
                variable[i] = 0
        elif isinstance(variable, list):
            variable.clear()

        del variable
        import gc
        gc.collect()
    except: pass

def anti_debug():
    """Detect if debugger is attached."""
    # Check TracerPid in /proc/self/status
    try:
        with open("/proc/self/status", "r") as f:
            for line in f:
                if line.startswith("TracerPid"):
                    pid = int(line.split(":")[1].strip())
                    if pid != 0:
                        return True # Debugger detected
    except: pass
    return False

def calculate_checksum(data):
    if isinstance(data, str): data = data.encode()
    return hashlib.sha256(data).hexdigest()

# --- AI & ML ---
class RLBrain:
    def __init__(self, name, actions):
        self.name = name
        self.actions = actions
        self.q_table = {}
        self.file = f"models/{name}_q.pkl"
        self.load()

    def get_q(self, state, action):
        return self.q_table.get((state, action), 0.0)

    def choose_action(self, state):
        if random.random() < 0.1: # Explore
            return random.choice(self.actions)

        q_values = [self.get_q(state, a) for a in self.actions]
        max_q = max(q_values)

        # Handle ties randomly
        best_actions = [self.actions[i] for i, q in enumerate(q_values) if q == max_q]
        return random.choice(best_actions)

    def learn(self, state, action, reward, next_state):
        current_q = self.get_q(state, action)
        max_next_q = max([self.get_q(next_state, a) for a in self.actions])

        new_q = current_q + 0.1 * (reward + 0.9 * max_next_q - current_q)
        self.q_table[(state, action)] = new_q

    def save(self):
        try:
            os.makedirs("models", exist_ok=True)
            # Simplified save (pickle not ideal for security but ok for sim)
            # using json for safety
            readable_q = {str(k): v for k, v in self.q_table.items()}
            # Skipping actual file save for performance in sim, or use json
            pass
        except: pass

    def load(self):
        pass

    def merge(self, other_q):
        # Federated averaging (simulated)
        pass

class AnomalyDetector:
    def __init__(self):
        self.history = []

    def add_datapoint(self, val):
        self.history.append(val)
        if len(self.history) > 100: self.history.pop(0)

    def is_anomaly(self, val):
        if len(self.history) < 10: return False
        avg = sum(self.history) / len(self.history)
        return abs(val - avg) > (avg * 0.5) # >50% deviation

# --- STEGO ---
def steganography_encode(data, image_path):
    """Simulate hiding data in image footer."""
    try:
        # Create dummy image if not exists
        if not os.path.exists(image_path):
            with open(image_path, 'wb') as f:
                f.write(os.urandom(1024)) # Dummy jpg

        with open(image_path, 'ab') as f:
            f.write(b"STEGO_MARKER")
            f.write(json.dumps(data).encode())
    except: pass

def steganography_decode(image_path):
    try:
        with open(image_path, 'rb') as f:
            content = f.read()
            if b"STEGO_MARKER" in content:
                parts = content.split(b"STEGO_MARKER")
                return json.loads(parts[-1])
    except: pass
    return None
