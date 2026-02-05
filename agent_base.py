from abc import ABC, abstractmethod
import signal
import sys
import time
import logging
import os
import random
from typing import Dict, Any, List

import utils
import config
import ml_engine

class CyberAgent(ABC):
    """
    Base class for Autonomous Cyber Agents (Red/Blue).
    Enforces standard lifecycle: Setup -> Loop [Perceive -> Decide -> Act -> Learn] -> Shutdown.
    """
    def __init__(self, agent_name: str, actions: List[str], log_path: str):
        self.name = agent_name
        self.running = True
        self.iteration_count = 0

        # Infrastructure
        utils.setup_logging(log_path)
        self.logger = logging.getLogger(agent_name)
        self.audit_logger = utils.AuditLogger(config.PATHS["AUDIT_LOG"])
        self.state_manager = utils.StateManager(config.PATHS["WAR_STATE"])

        # Brain
        self.ai = ml_engine.DoubleQLearner(actions, agent_name)

        # Limits
        utils.limit_resources(ram_mb=config.SYSTEM["RESOURCE_LIMIT_MB"])

        # Signals
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def load_memory(self):
        """Load Q-Table from disk."""
        path = config.PATHS[f"Q_TABLE_{self.name}"]
        data = self.state_manager.load_json(path)
        self.ai.load(data)
        self.logger.info("AI Memory Loaded.")

    def sync_memory(self):
        """Save Q-Table to disk."""
        path = config.PATHS[f"Q_TABLE_{self.name}"]
        data = self.ai.export()
        self.state_manager.save_json(path, data)

    def shutdown(self, signum, frame):
        """Graceful shutdown."""
        self.logger.info("Shutting down... Syncing memory.")
        self.sync_memory()
        self.running = False
        sys.exit(0)

    def update_heartbeat(self):
        """Touch heartbeat file for Watchdog."""
        hb_file = os.path.join(config.PATHS["DATA_DIR"], f"{self.name.lower()}.heartbeat")
        try:
            with open(hb_file, 'w') as f: f.write(str(time.time()))
        except: pass

    @abstractmethod
    def perceive(self) -> str:
        """Return state vector string."""
        pass

    @abstractmethod
    def get_context(self) -> Dict[str, Any]:
        """Return context for decision making."""
        pass

    @abstractmethod
    def calculate_reward(self, action: str, result: Dict[str, Any]) -> float:
        """Return reward for the action."""
        pass

    def engage(self):
        """Main Life Cycle Loop."""
        self.logger.info(f"{self.name} Agent Initialized.")
        self.load_memory()

        while self.running:
            try:
                self.iteration_count += 1
                self.update_heartbeat()

                # 1. Perceive
                state_vector = self.perceive()
                context = self.get_context()

                # 2. Decide
                action_name = self.ai.choose_action(state_vector, context)

                # 3. Act
                try:
                    tactic_func = getattr(self, action_name.lower())
                    result = tactic_func()
                    self.audit_logger.log_event(self.name, action_name, result)
                    self.logger.info(f"Action: {action_name} | Result: {result} | Q: {self.ai.get_q(state_vector, action_name):.2f}")
                except AttributeError:
                    self.logger.error(f"Action {action_name} not implemented.")
                    result = {}
                except Exception as e:
                    self.logger.warning(f"Failed {action_name}: {e}")
                    result = {}

                # 4. Reward & Learn
                reward = self.calculate_reward(action_name, result)

                # S' (Next State) - Simplified to current state for now,
                # or we could observe again if state changed immediately.
                next_state = state_vector

                self.ai.memory.push(state_vector, action_name, reward, next_state, False)
                self.ai.learn()

                # 5. Persist
                if self.iteration_count % config.RL["SYNC_INTERVAL"] == 0:
                    self.sync_memory()

                time.sleep(random.uniform(0.5, 2.0))

            except KeyboardInterrupt:
                self.shutdown(None, None)
            except Exception as e:
                self.logger.error(f"Loop Error: {e}")
                time.sleep(1)
