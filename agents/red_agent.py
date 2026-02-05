import os
import json
import random

class RedAgent:
    def __init__(self, data_dir="simulation_data"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.q_table_file = os.path.join(self.data_dir, "red_q.json")
        self.q_table = self._load_memory()

        self.alpha = 0.3
        self.gamma = 0.9
        self.epsilon = 0.2

        # Actions: Attack Vectors
        self.actions = ["SQL_INJECTION", "XSS_SPRAY", "BRUTE_FORCE", "STEALTH_PROBE", "IDLE"]

    def _load_memory(self):
        if os.path.exists(self.q_table_file):
            try:
                with open(self.q_table_file, 'r') as f: return json.load(f)
            except: return {}
        return {}

    def _save_memory(self):
        try:
            with open(self.q_table_file, 'w') as f: json.dump(self.q_table, f)
        except: pass

    def get_action(self, state):
        # State: e.g., "BLOCKED", "OPEN", "CAPTCHA"
        if random.random() < self.epsilon:
            return random.choice(self.actions)

        q_vals = [self.q_table.get(f"{state}_{a}", 0) for a in self.actions]
        max_q = max(q_vals)
        best_actions = [self.actions[i] for i, q in enumerate(q_vals) if q == max_q]
        return random.choice(best_actions)

    def learn(self, state, action, reward, next_state):
        old_q = self.q_table.get(f"{state}_{action}", 0)
        next_max = max([self.q_table.get(f"{next_state}_{a}", 0) for a in self.actions])

        new_q = old_q + self.alpha * (reward + self.gamma * next_max - old_q)
        self.q_table[f"{state}_{action}"] = new_q

        self.epsilon = max(0.01, self.epsilon * 0.999)
        self._save_memory()
