import os
import fcntl
import logging
import math
import random
import json
import time
import hashlib
import db_manager

# Singleton DB instance
DB = db_manager.DatabaseManager()

# Utility functions

def safe_file_write(file_path, data):
    """Write data to a file safely using locks."""
    with open(file_path, 'w') as file:
        fcntl.flock(file, fcntl.LOCK_EX)
        file.write(data)
        fcntl.flock(file, fcntl.LOCK_UN)


def safe_file_read(file_path, binary=False):
    """Read data from a file safely using locks."""
    mode = 'rb' if binary else 'r'
    with open(file_path, mode) as file:
        fcntl.flock(file, fcntl.LOCK_SH)
        data = file.read()
        fcntl.flock(file, fcntl.LOCK_UN)
    return data


def safe_json_write(filepath, data):
    """Write JSON data safely."""
    try:
        json_str = json.dumps(data, indent=4)
        safe_file_write(filepath, json_str)
    except: pass


def safe_json_read(filepath, default=None):
    """Read JSON data safely."""
    if default is None: default = {}
    if not os.path.exists(filepath): return default
    try:
        data_str = safe_file_read(filepath)
        return json.loads(data_str)
    except: return default


class SmartJSONLoader:
    """Cached JSON loader that only re-reads if file modified."""
    def __init__(self, filepath, default=None):
        self.filepath = filepath
        self.default = default if default is not None else {}
        self.last_mtime = 0
        self.cache = self.default

    def load(self):
        try:
            if not os.path.exists(self.filepath):
                return self.default

            mtime = os.path.getmtime(self.filepath)
            if mtime > self.last_mtime:
                self.cache = safe_json_read(self.filepath, self.default)
                self.last_mtime = mtime
                return self.cache, True # Changed: return tuple (data, changed)
            return self.cache, False
        except:
            return self.cache, False

class FileIntegrityCache:
    """Tracks files to avoid re-scanning unchanged content."""
    def __init__(self):
        self.files = {} # path -> (mtime, size)

    def filter_changed(self, filepaths):
        """Return only files that are new or modified since last check."""
        changed = []
        current_files = set(filepaths)

        # Cleanup deleted files from cache
        # Optimization: Use list comprehension for speed if cache is large
        keys_to_delete = [p for p in self.files if p not in current_files]
        for p in keys_to_delete:
            del self.files[p]

        for p in filepaths:
            try:
                # Optimization: os.stat result object access is fast
                stat = os.stat(p)
                sig = (stat.st_mtime, stat.st_size)
                # Direct check
                if self.files.get(p) != sig:
                    self.files[p] = sig
                    changed.append(p)
            except FileNotFoundError:
                pass
        return changed

    def invalidate(self, filepath):
        if filepath in self.files:
            del self.files[filepath]

class QTableManager:
    """Manages Q-Table via SQLite with caching for performance."""
    def __init__(self, agent_name, actions):
        self.agent_name = agent_name
        self.actions = actions
        self.cache = {} # state_action -> value (Write-through cache)
        self.best_action_cache = {} # state -> action

    def get_q(self, state, action):
        key = f"{state}_{action}"
        if key in self.cache:
            return self.cache[key]

        # Cache miss: Read from DB
        val = DB.get_q_value(self.agent_name, state, action)
        self.cache[key] = val
        return val

    def update_q(self, state, action, value):
        key = f"{state}_{action}"
        self.cache[key] = value

        # Async/Buffered DB write could go here, but for now write-through
        DB.update_q_value(self.agent_name, state, action, value)

        # Invalidate best action cache
        if state in self.best_action_cache:
            del self.best_action_cache[state]

    def get_best_action(self, state):
        if state in self.best_action_cache:
            return self.best_action_cache[state]

        # Optimization: Let DB do the heavy lifting if not in cache
        # But since we have a local cache that might be fresher, we should check it first?
        # Actually, for Q-Learning, local memory (RAM) is ground truth for the session.
        # We will iterate actions using get_q (which checks RAM then DB).

        best = max(self.actions, key=lambda a: self.get_q(state, a))
        self.best_action_cache[state] = best
        return best

    def get_max_q(self, state):
        return max(self.get_q(state, a) for a in self.actions)

    def learn_from_replay(self, batch_size=10, alpha=0.1, gamma=0.9):
        """Sample experience from DB (including Proxy War) and update Q-Table."""
        samples = DB.sample_experience(self.agent_name, batch_size)
        count = 0
        for (state, action, reward, next_state) in samples:
            # Q-Learning Update Rule
            current_q = self.get_q(state, action)
            max_next_q = self.get_max_q(next_state)
            new_q = current_q + alpha * (reward + gamma * max_next_q - current_q)
            self.update_q(state, action, new_q)
            count += 1
        return count

def adaptive_sleep(base_sleep, activity_factor, min_sleep=0.1):
    """Sleep less if active, more if idle."""
    sleep_time = max(min_sleep, base_sleep / (1 + activity_factor))
    time.sleep(sleep_time)


def scan_threats(watch_dir):
    """Efficiently scan for visible and hidden threats."""
    visible = []
    hidden = []
    try:
        with os.scandir(watch_dir) as entries:
            for entry in entries:
                # Direct attribute access is slightly faster than method call
                if entry.is_file():
                    name = entry.name
                    # Check prefixes directly
                    if name.startswith('malware_'):
                        visible.append(entry.path)
                    elif name.startswith('.sys_'):
                        hidden.append(entry.path)
    except FileNotFoundError:
        pass
    return visible, hidden


def calculate_entropy(data):
    """Calculate the entropy of a string of data."""
    if not data:
        return 0

    counts = [0] * 256
    for b in data:
        counts[b] += 1

    entropy = 0
    length = len(data)
    for count in counts:
        if count > 0:
            p_x = count / length
            entropy -= p_x * math.log2(p_x)

    return entropy

def calculate_sha256(filepath):
    """Calculate SHA256 hash of a file efficiently."""
    sha256 = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while True:
                data = f.read(65536) # 64k chunks
                if not data: break
                sha256.update(data)
        return sha256.hexdigest()
    except: return None


def setup_logging(name, log_file_path):
    """Set up logging to a specified file and console."""
    # Create directory if missing
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # File Handler
    fh = logging.FileHandler(log_file_path)
    fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(fh)

    # Console Handler (if not already handled by root, but for specific agents)
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(message)s')) # Cleaner console output
    logger.addHandler(ch)

    return logger


def manage_session(session_id):
    """Manage a user session given a session ID."""
    # Placeholder for session management logic
    pass

