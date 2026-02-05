import os
import json
import random
import math

class BlueAgent:
    def __init__(self, data_dir="simulation_data"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.q_table_file = os.path.join(self.data_dir, "blue_q.json")
        self.q_table = self._load_memory()

        # Hyperparameters
        self.alpha = 0.3      # Learning Rate
        self.gamma = 0.9      # Discount
        self.epsilon = 0.2    # Exploration

        # Actions: DEFCON levels (1=Normal, 5=Lockdown) and Special Tactics
        self.actions = ["DEFCON_1", "DEFCON_3", "DEFCON_5", "RESET_FILTERS"]

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
        # State: string representation of current threat level
        if random.random() < self.epsilon:
            return random.choice(self.actions)

        # Greedy
        q_vals = [self.q_table.get(f"{state}_{a}", 0) for a in self.actions]
        max_q = max(q_vals)
        # Handle ties
        best_actions = [self.actions[i] for i, q in enumerate(q_vals) if q == max_q]
        return random.choice(best_actions)

    def learn(self, state, action, reward, next_state):
        old_q = self.q_table.get(f"{state}_{action}", 0)
        next_max = max([self.q_table.get(f"{next_state}_{a}", 0) for a in self.actions])

        new_q = old_q + self.alpha * (reward + self.gamma * next_max - old_q)
        self.q_table[f"{state}_{action}"] = new_q

        self.epsilon = max(0.01, self.epsilon * 0.999) # Decay
        self._save_memory()
