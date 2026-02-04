import os
import fcntl
import logging
import math
import random
import json
import time

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
        for p in list(self.files.keys()):
            if p not in current_files:
                del self.files[p]

        for p in filepaths:
            try:
                stat = os.stat(p)
                sig = (stat.st_mtime, stat.st_size)
                if p not in self.files or self.files[p] != sig:
                    self.files[p] = sig
                    changed.append(p)
            except FileNotFoundError:
                pass
        return changed

    def invalidate(self, filepath):
        if filepath in self.files:
            del self.files[filepath]

class QTableManager:
    """Manages Q-Table with caching for O(1) best action lookup."""
    def __init__(self, actions):
        self.q_table = {}
        self.actions = actions
        self.best_action_cache = {} # state_key -> action

    def load(self, data):
        self.q_table = data
        self.best_action_cache = {} # Invalidate on load

    def get_q(self, state, action):
        return self.q_table.get(state + "_" + action, 0)

    def update_q(self, state, action, value):
        self.q_table[state + "_" + action] = value
        # Invalidate best action cache for this state
        if state in self.best_action_cache:
            del self.best_action_cache[state]

    def get_best_action(self, state):
        if state in self.best_action_cache:
            return self.best_action_cache[state]

        # Find best action (standard max)
        # Optimized: Pre-construct keys generator
        best = max(self.actions, key=lambda a: self.q_table.get(state + "_" + a, 0))
        self.best_action_cache[state] = best
        return best

    def get_max_q(self, state):
        # We can also cache max_q if needed, but best_action usually implies it
        return max(self.q_table.get(state + "_" + a, 0) for a in self.actions)

    def export(self):
        return self.q_table

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


def setup_logging(log_file_path):
    """Set up logging to a specified file."""
    logging.basicConfig(filename=log_file_path,
                        level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s:%(message)s')


def manage_session(session_id):
    """Manage a user session given a session ID."""
    # Placeholder for session management logic
    pass

