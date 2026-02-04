import time
import json
import os
import sys

# Adjust path to find utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from utils import safe_file_read, safe_file_write

class Gatekeeper:
    """Adaptive Policy Engine: Manages Ban States and Escalation."""

    def __init__(self, state_file, logger):
        self.state_file = state_file
        self.logger = logger
        self.policy_state = self.load_state() # {target: {strikes: n, ban_until: timestamp}}

    def load_state(self):
        try:
            content = safe_file_read(self.state_file)
            return json.loads(content) if content else {}
        except: return {}

    def save_state(self):
        try: safe_file_write(self.state_file, json.dumps(self.policy_state, indent=4))
        except: pass

    def report_offense(self, target):
        now = time.time()
        if target not in self.policy_state:
            self.policy_state[target] = {"strikes": 0, "ban_until": 0}

        record = self.policy_state[target]
        record["strikes"] += 1

        # Adaptive Escalation
        if record["strikes"] == 1:
            duration = 10 # Warning shot
            level = "TEMP"
        elif record["strikes"] == 2:
            duration = 60 # Timeout
            level = "LONG"
        else:
            duration = 3600 # Permaban (effectively)
            level = "PERMA"

        record["ban_until"] = now + duration
        self.logger.warning(f"Gatekeeper: {target} Strike {record['strikes']}. Banned for {duration}s ({level}).")
        self.save_state()

    def is_banned(self, target):
        if target not in self.policy_state: return False
        return time.time() < self.policy_state[target]["ban_until"]
