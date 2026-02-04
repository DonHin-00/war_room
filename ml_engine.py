#!/usr/bin/env python3
"""
ML Engine - Pure Python Version
Provides Advanced Reinforcement Learning components:
- Double Q-Learning
- Prioritized Experience Replay
- Safety Shields
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
        if total_p == 0:
            probs = [1.0/len(self.buffer)] * len(self.buffer)
        else:
            probs = [p / total_p for p in scaled_priorities]

        # Sample indices based on probabilities
        indices = random.choices(range(len(self.buffer)), weights=probs, k=batch_size)
        samples = [self.buffer[idx] for idx in indices]

        # Calculate importance sampling weights
        total_N = len(self.buffer)
        weights = []
        # Approximate logic for scaling weights
        # Avoid zero division
        min_prob = min([probs[i] for i in indices]) if indices else 1.0
        max_weight = (total_N * min_prob) ** (-beta) if min_prob > 0 else 1.0

        for idx in indices:
            prob = probs[idx]
            weight = (total_N * prob) ** (-beta) if prob > 0 else 0
            weights.append(weight / max_weight if max_weight > 0 else 0)

        return samples, indices, weights

    def update_priorities(self, indices, priorities):
        for idx, prio in zip(indices, priorities):
            self.priorities[idx] = prio + 1e-5

class SafetyShield:
    """
    Rule-based safety layer to override unsafe RL actions.
    """
    def __init__(self, agent_type: str):
        self.agent_type = agent_type

    def is_safe(self, action: str, state_context: Dict[str, Any]) -> bool:
        if self.agent_type == "RED":
            # Don't attack if traps are detected and alert is high
            if action in ["T1486_ENCRYPT", "T1003_ROOTKIT", "T1055_INJECTION"]:
                if state_context.get("traps_found", 0) > 0 and state_context.get("alert_level", 1) > 3:
                    return False
            # Don't lateral move blindly if high alert
            if action == "T1021_LATERAL_MOVE" and state_context.get("alert_level", 1) >= 5:
                return False

        elif self.agent_type == "BLUE":
            # Don't restore if no backup
            if action == "RESTORE_DATA" and not state_context.get("has_backup", False):
                return False
            # Don't purge if threat level is low (save resources)
            if action == "HUNT_PROCESSES" and state_context.get("threat_count", 0) == 0:
                return False

        return True

class DoubleQLearner:
    """
    Double Q-Learning Agent.
    """
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
        # Safety Shield Check
        safe_actions = [a for a in self.actions if self.shield.is_safe(a, context)]
        if not safe_actions:
            safe_actions = ["T1589_LURK" if self.name == "RED" else "OBSERVE"]
            if safe_actions[0] not in self.actions: safe_actions = [self.actions[0]] # Fallback

        if random.random() < self.epsilon:
            return random.choice(safe_actions)

        # Greedy Selection among SAFE actions
        max_q = -float('inf')
        best_actions = []
        for a in safe_actions:
            q = self.get_q(state, a)
            if q > max_q:
                max_q = q
                best_actions = [a]
            elif q == max_q:
                best_actions.append(a)

        return random.choice(best_actions) if best_actions else random.choice(safe_actions)

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

            # Argmax action from MAIN table
            best_next_action = max(self.actions, key=lambda a: main.get(f"{next_state}_{a}", 0.0))

            # Value from TARGET table
            target_value = target.get(f"{next_state}_{best_next_action}", 0.0)

            q_target = reward + (self.gamma * target_value * (1 - int(done)))
            key = f"{state}_{action}"
            current_q = main.get(key, 0.0)

            td_error = q_target - current_q
            main[key] = current_q + (self.alpha * td_error * weights[i])

            priorities.append(abs(td_error))

        self.memory.update_priorities(indices, priorities)
        self.epsilon = max(config.RL["EPSILON_MIN"], self.epsilon * config.RL["EPSILON_DECAY"])
