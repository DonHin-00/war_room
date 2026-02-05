"""
Machine Learning Engine for Cyber War Simulation
Provides Reinforcement Learning components: Double Q-Learning, Replay Buffer, and Safety Shield.
"""

import random
import logging
import json
import os
import math
from typing import Dict, List, Tuple, Any, Optional

from utils import atomic_json_io, atomic_json_merge

class PrioritizedReplayBuffer:
    """
    Stores experiences (state, action, reward, next_state, done) for training.
    Simplified implementation (Random sampling, no true priorities yet).
    """
    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.buffer: List[Tuple] = []
        self.position = 0

    def push(self, state, action, reward, next_state, done):
        if len(self.buffer) < self.capacity:
            self.buffer.append(None)
        self.buffer[self.position] = (state, action, reward, next_state, done)
        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size: int) -> List[Tuple]:
        return random.sample(self.buffer, batch_size)

    def __len__(self):
        return len(self.buffer)

class SafetyShield:
    """
    Heuristic filter to override unsafe or irrational AI actions.
    """
    def __init__(self, agent_type: str):
        self.agent_type = agent_type # 'blue' or 'red'

    def is_unsafe(self, action: str, context: Dict[str, Any]) -> bool:
        """Returns True if the action violates safety constraints."""
        if self.agent_type == 'blue':
            # Example: Don't delete system files blindly if entropy is low (benign)
            if action == 'HEURISTIC_SCAN':
                # This check would happen inside the agent loop usually,
                # but the shield can warn.
                pass
            # Example: Don't ignore Critical alerts
            if action == 'IGNORE' and context.get('alert_level', 1) >= 5:
                return True

        if self.agent_type == 'red':
            # Example: Don't burn a honeypot if you know it is one (redundant check)
            pass

        return False

class DoubleQLearner:
    """
    Double Q-Learning Agent.
    Maintains two Q-tables (Q1, Q2) to reduce maximization bias.
    """
    def __init__(self,
                 actions: List[str],
                 alpha: float = 0.1,
                 gamma: float = 0.9,
                 epsilon: float = 0.1,
                 filepath: Optional[str] = None):

        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.filepath = filepath

        # Two Q-tables
        self.q1: Dict[str, float] = {}
        self.q2: Dict[str, float] = {}

        self.load()

    def load(self):
        if self.filepath:
            data = atomic_json_io(self.filepath)
            self.q1 = data.get('q1', {})
            self.q2 = data.get('q2', {})

    def save(self):
        if self.filepath:
            data = {'q1': self.q1, 'q2': self.q2}
            atomic_json_merge(self.filepath, data)

    def get_q(self, state: str, action: str, table: int = 1) -> float:
        key = f"{state}_{action}"
        if table == 1:
            return self.q1.get(key, 0.0)
        else:
            return self.q2.get(key, 0.0)

    def choose_action(self, state: str, excluded_actions: List[str] = []) -> str:
        if random.random() < self.epsilon:
            available = [a for a in self.actions if a not in excluded_actions]
            return random.choice(available) if available else self.actions[0]

        # Greedy: Maximize (Q1 + Q2) / 2
        best_action = ""
        max_val = -float('inf')

        random.shuffle(self.actions) # Break ties randomly
        for a in self.actions:
            if a in excluded_actions: continue

            val = (self.get_q(state, a, 1) + self.get_q(state, a, 2)) / 2.0
            if val > max_val:
                max_val = val
                best_action = a

        return best_action

    def learn(self, state: str, action: str, reward: float, next_state: str):
        """
        Double Q-Learning update:
        Randomly update Q1 or Q2.
        If Q1: Q1(s,a) <- Q1(s,a) + alpha * (r + gamma * Q2(s', argmax Q1(s',a)) - Q1(s,a))
        If Q2: Q2(s,a) <- Q2(s,a) + alpha * (r + gamma * Q1(s', argmax Q2(s',a)) - Q2(s,a))
        """
        key = f"{state}_{action}"

        if random.random() < 0.5:
            # Update Q1
            # Find action that maximizes Q1(next_state)
            best_next_a = max(self.actions, key=lambda a: self.get_q(next_state, a, 1))
            # Use Q2 value for that action
            q_target = self.get_q(next_state, best_next_a, 2)

            old_val = self.q1.get(key, 0.0)
            self.q1[key] = old_val + self.alpha * (reward + self.gamma * q_target - old_val)
        else:
            # Update Q2
            best_next_a = max(self.actions, key=lambda a: self.get_q(next_state, a, 2))
            q_target = self.get_q(next_state, best_next_a, 1)

            old_val = self.q2.get(key, 0.0)
            self.q2[key] = old_val + self.alpha * (reward + self.gamma * q_target - old_val)

    def decay_epsilon(self, decay_rate: float, min_epsilon: float):
        self.epsilon = max(min_epsilon, self.epsilon * decay_rate)
