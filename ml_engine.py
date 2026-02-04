#!/usr/bin/env python3
"""
ML Engine - Pure Python Version
"""

import random
import logging
import math
from typing import Dict, List, Tuple, Any, Deque

import utils
import config

logger = logging.getLogger("ML_Engine")

class PrioritizedReplayBuffer:
    """
    Stores experiences with priorities. Pure Python implementation.
    """
    def __init__(self, capacity: int = 1000, alpha: float = 0.6):
        self.capacity = capacity
        self.alpha = alpha
        self.buffer = []
        self.priorities = []
        self.pos = 0

    def push(self, state, action, reward, next_state, done):
        max_prio = max(self.priorities) if self.priorities else 1.0

        if len(self.buffer) < self.capacity:
            self.buffer.append((state, action, reward, next_state, done))
            self.priorities.append(max_prio)
        else:
            self.buffer[self.pos] = (state, action, reward, next_state, done)
            self.priorities[self.pos] = max_prio
            self.pos = (self.pos + 1) % self.capacity

    def sample(self, batch_size: int, beta: float = 0.4):
        if len(self.buffer) == 0: return [], [], []

        # Calculate probabilities
        scaled_priorities = [p ** self.alpha for p in self.priorities]
        total_p = sum(scaled_priorities)
        probs = [p / total_p for p in scaled_priorities]

        # Sample indices based on probabilities
        indices = random.choices(range(len(self.buffer)), weights=probs, k=batch_size)
        samples = [self.buffer[idx] for idx in indices]

        # Calculate importance sampling weights
        total_N = len(self.buffer)
        weights = []
        max_prob = max(probs)
        min_prob = min(probs) # Approximate logic for scaling

        # IS Weights: w = (N * P)^-beta
        # Normalize by max weight (which corresponds to min prob)
        max_weight = (total_N * min_prob) ** (-beta) if min_prob > 0 else 1.0

        for idx in indices:
            prob = probs[idx]
            weight = (total_N * prob) ** (-beta)
            weights.append(weight / max_weight)

        return samples, indices, weights

    def update_priorities(self, indices, priorities):
        for idx, prio in zip(indices, priorities):
            self.priorities[idx] = prio + 1e-5

class SafetyShield:
    def __init__(self, agent_type: str):
        self.agent_type = agent_type

    def is_safe(self, action: str, state_context: Dict[str, Any]) -> bool:
        if self.agent_type == "RED":
            if action in ["T1486_ENCRYPT", "T1003_ROOTKIT"]:
                if state_context.get("traps_found", 0) > 0 and state_context.get("alert_level", 1) > 3:
                    return False
            if action == "T1070_WIPE_LOGS" and state_context.get("actions_taken", 0) < 3:
                return False

        elif self.agent_type == "BLUE":
            if action == "RESTORE_DATA" and not state_context.get("has_backup", False):
                return False
            if action == "HUNT_PROCESSES" and state_context.get("threat_count", 0) == 0:
                return False

        return True

class DoubleQLearner:
    def __init__(self, actions: List[str], name: str):
        self.actions = actions
        self.name = name
        self.q_a: Dict[str, float] = {}
        self.q_b: Dict[str, float] = {}

        self.alpha = config.RL["ALPHA"]
        self.gamma = config.RL["GAMMA"]
        self.epsilon = config.RL["EPSILON_START"]

        self.memory = PrioritizedReplayBuffer(config.RL["MEMORY_CAPACITY"])
        self.shield = SafetyShield(name)

    def load(self, data: Dict[str, Any]):
        self.q_a = data.get("A", {})
        self.q_b = data.get("B", {})

    def export(self) -> Dict[str, Any]:
        return {"A": self.q_a, "B": self.q_b}

    def get_q(self, state, action):
        return (self.q_a.get(f"{state}_{action}", 0.0) + self.q_b.get(f"{state}_{action}", 0.0)) / 2.0

    def choose_action(self, state: str, context: Dict[str, Any]) -> str:
        if random.random() < self.epsilon:
            action = random.choice(self.actions)
        else:
            max_q = -float('inf')
            best_actions = []
            for a in self.actions:
                q = self.get_q(state, a)
                if q > max_q:
                    max_q = q
                    best_actions = [a]
                elif q == max_q:
                    best_actions.append(a)
            action = random.choice(best_actions) if best_actions else random.choice(self.actions)

        if not self.shield.is_safe(action, context):
            fallback = "T1046_RECON" if self.name == "RED" else "OBSERVE"
            if fallback in self.actions and fallback != action:
                return fallback

        return action

    def learn(self, batch_size=None):
        if not batch_size: batch_size = config.RL["BATCH_SIZE"]
        if len(self.memory.buffer) < batch_size: return

        samples, indices, weights = self.memory.sample(batch_size)
        priorities = []

        for i, (state, action, reward, next_state, done) in enumerate(samples):
            if random.random() < 0.5:
                main, target = self.q_a, self.q_b
            else:
                main, target = self.q_b, self.q_a

            best_next_action = max(self.actions, key=lambda a: main.get(f"{next_state}_{a}", 0.0))
            target_value = target.get(f"{next_state}_{best_next_action}", 0.0)

            q_target = reward + (self.gamma * target_value * (1 - int(done)))
            key = f"{state}_{action}"
            current_q = main.get(key, 0.0)

            td_error = q_target - current_q
            main[key] = current_q + (self.alpha * td_error * weights[i])

            priorities.append(abs(td_error))

        self.memory.update_priorities(indices, priorities)
        self.epsilon = max(config.RL["EPSILON_MIN"], self.epsilon * config.RL["EPSILON_DECAY"])
