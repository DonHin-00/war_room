#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Red Team)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: MITRE ATT&CK Matrix
"""

import os
import time
import json
import random
import signal
import sys
import utils
import config
from typing import List, Tuple, Dict, Any

# --- VISUALS ---
C_RED = "\033[91m"
C_RESET = "\033[0m"

class RedTeamer:
    """
    Red Team AI Agent implementing MITRE ATT&CK Matrix tactics.
    Uses Double Q-Learning with Experience Replay for stable training.
    """
    def __init__(self) -> None:
        self.running: bool = True
        self.epsilon: float = config.AI_PARAMS['EPSILON_START']
        self.alpha: float = config.AI_PARAMS['ALPHA']
        # Double Q-Learning: Two tables
        self.q_table_1: Dict[str, float] = {}
        self.q_table_2: Dict[str, float] = {}
        self.memory: List[Tuple[str, str, float, str]] = [] # Experience Replay Buffer
        self.audit_logger = utils.AuditLogger(config.AUDIT_LOG)

        # Signal Handling
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

        self.setup()

    def setup(self) -> None:
        """Initialize resources and load persistent state."""
        print(f"{C_RED}[SYSTEM] Red Team AI Initialized. APT Framework: ACTIVE{C_RESET}")
        # Load Q-Table (legacy single file split into two or init new)
        data = utils.access_memory(config.Q_TABLE_RED) or {}
        self.q_table_1 = data.get('q1', {})
        self.q_table_2 = data.get('q2', {})

        if not os.path.exists(config.WAR_ZONE_DIR):
            try: os.makedirs(config.WAR_ZONE_DIR)
            except OSError: pass

    def shutdown(self, signum: int, frame: Any) -> None:
        """Graceful shutdown handler."""
        print(f"\n{C_RED}[SYSTEM] Red Team shutting down gracefully...{C_RESET}")
        # Save both tables
        utils.access_memory(config.Q_TABLE_RED, {'q1': self.q_table_1, 'q2': self.q_table_2})
        self.running = False
        sys.exit(0)

    def choose_action(self, state_key: str) -> str:
        """Select an action using Double Q-Learning strategy."""
        if random.random() < self.epsilon:
            return random.choice(config.RED_ACTIONS)
        else:
            # Double Q: Use average or sum of Q1+Q2
            known = {}
            for a in config.RED_ACTIONS:
                val = self.q_table_1.get(f"{state_key}_{a}", 0) + self.q_table_2.get(f"{state_key}_{a}", 0)
                known[a] = val
            return max(known, key=known.get)

    def remember(self, state: str, action: str, reward: float, next_state: str) -> None:
        """Store experience in replay buffer."""
        self.memory.append((state, action, reward, next_state))
        if len(self.memory) > config.AI_PARAMS['MEMORY_SIZE']:
            self.memory.pop(0)

    def replay(self) -> None:
        """Train the model using random batch from memory."""
        if len(self.memory) < config.AI_PARAMS['BATCH_SIZE']:
            return

        batch = random.sample(self.memory, config.AI_PARAMS['BATCH_SIZE'])
        for state, action, reward, next_state in batch:
             # Randomly update Q1 or Q2
             if random.random() < 0.5:
                 # Update Q1 using Q2 for value estimation
                 max_next = max([self.q_table_1.get(f"{next_state}_{a}", 0) for a in config.RED_ACTIONS])
                 # Or correctly: use a from Q1 to query Q2? Simplified to standard Q-Learning for sim speed here,
                 # but implementing simple Double Q Logic:
                 # Q1(s,a) <- Q1(s,a) + alpha * (r + gamma * Q2(s', argmax Q1(s',a)) - Q1(s,a))

                 # simplified max for stability in this script scope:
                 q1_old = self.q_table_1.get(f"{state}_{action}", 0)
                 q2_next_max = max([self.q_table_2.get(f"{next_state}_{a}", 0) for a in config.RED_ACTIONS])

                 new_val = q1_old + self.alpha * (reward + config.AI_PARAMS['GAMMA'] * q2_next_max - q1_old)
                 self.q_table_1[f"{state}_{action}"] = new_val
             else:
                 # Update Q2 using Q1
                 q2_old = self.q_table_2.get(f"{state}_{action}", 0)
                 q1_next_max = max([self.q_table_1.get(f"{next_state}_{a}", 0) for a in config.RED_ACTIONS])

                 new_val = q2_old + self.alpha * (reward + config.AI_PARAMS['GAMMA'] * q1_next_max - q2_old)
                 self.q_table_2[f"{state}_{action}"] = new_val

    def run(self):
        iteration = 0
        while self.running:
            try:
                iteration += 1
                
                # 1. RECON
                war_state = utils.access_memory(config.STATE_FILE) or {'blue_alert_level': 1}
                current_alert = war_state.get('blue_alert_level', 1)
                state_key = f"{current_alert}"
                
                # 2. DECIDE
                action = self.choose_action(state_key)
                
                self.epsilon = max(config.AI_PARAMS['MIN_EPSILON'], self.epsilon * config.AI_PARAMS['EPSILON_DECAY'])
                self.alpha = max(0.1, self.alpha * config.AI_PARAMS['ALPHA_DECAY'])

                # 3. EXECUTE
                impact = 0

                if action == "T1046_RECON":
                    fname = os.path.join(config.WAR_ZONE_DIR, f"malware_bait_{int(time.time())}.sh")
                    try:
                        utils.secure_create(fname, "echo 'scan'")
                        impact = 1
                    except OSError:
                        pass # Expected if permissions deny

                elif action == "T1027_OBFUSCATE":
                    fname = os.path.join(config.WAR_ZONE_DIR, f"malware_crypt_{int(time.time())}.bin")
                    try:
                        size = random.randint(800, 1200)
                        data = os.urandom(size).decode('latin1')
                        utils.secure_create(fname, data)
                        impact = 3
                    except OSError: pass

                elif action == "T1003_ROOTKIT":
                    fname = os.path.join(config.WAR_ZONE_DIR, f".sys_shadow_{int(time.time())}")
                    try:
                        utils.secure_create(fname, "uid=0(root)")
                        impact = 5
                    except OSError: pass

                elif action == "T1071_C2_BEACON":
                    fname = os.path.join(config.WAR_ZONE_DIR, f"beacon_{int(time.time())}.c2_beacon")
                    try:
                        payload = f"BEACON_ID:{random.randint(1000,9999)}"
                        utils.secure_create(fname, payload)
                        impact = 4
                        self.audit_logger.log_event("RED", "C2_BEACON", f"Established beacon at {fname}")
                    except OSError: pass

                elif action == "T1589_LURK":
                    impact = 0

                elif action == "T1486_ENCRYPT":
                    # Ransomware: Rename random visible files to .enc
                    targets = [f for f in os.listdir(config.WAR_ZONE_DIR) if not f.endswith(".enc") and not f.startswith(".")]
                    if targets:
                        target = random.choice(targets)
                        src = os.path.join(config.WAR_ZONE_DIR, target)
                        dst = src + ".enc"
                        try:
                            # If it's a honeypot, we get trapped!
                            if utils.is_honeypot(src):
                                impact = -1 # Special signal for trap
                            else:
                                os.rename(src, dst)
                                impact = 6
                                self.audit_logger.log_event("RED", "RANSOMWARE", f"Encrypted {target}")
                        except OSError: pass

                elif action == "T1547_PERSISTENCE":
                    # Persistence: Create a hidden startup script
                    fname = os.path.join(config.WAR_ZONE_DIR, f".startup_{random.randint(10,99)}.sh")
                    try:
                        utils.secure_create(fname, "#!/bin/bash\n./malware.sh")
                        impact = 4
                    except OSError: pass

                # 4. REWARD CALCULATION
                reward = 0
                if impact > 0: reward = config.RED_REWARDS['IMPACT']
                if impact == 6: reward = config.RED_REWARDS['RANSOM_SUCCESS']
                if impact == -1: reward = config.RED_REWARDS['TRAPPED']

                if current_alert >= 4 and action == "T1589_LURK": reward = config.RED_REWARDS['STEALTH']
                if current_alert == config.MAX_ALERT and impact > 0: reward = config.RED_REWARDS['CRITICAL']
                if action == "T1071_C2_BEACON": reward = config.RED_REWARDS['C2_SUCCESS']
                if action == "T1547_PERSISTENCE" and impact > 0: reward = config.RED_REWARDS['PERSISTENCE_SUCCESS']

                # 5. LEARN (Double Q + Replay)
                # We need next state for proper learning.
                # Simplification: Assume next state is roughly same key or +1 alert.
                # In strict RL, we observe S' after act.
                # Let's peek at new state
                new_war_state = utils.access_memory(config.STATE_FILE) or {'blue_alert_level': 1}
                next_alert = new_war_state.get('blue_alert_level', 1)
                next_state_key = f"{next_alert}"

                self.remember(state_key, action, reward, next_state_key)
                self.replay()

                if iteration % config.AI_PARAMS['SYNC_INTERVAL'] == 0:
                    utils.access_memory(config.Q_TABLE_RED, {'q1': self.q_table_1, 'q2': self.q_table_2})

                # 6. TRIGGER ALERTS
                if impact > 0 and random.random() > 0.5:
                    war_state['blue_alert_level'] = min(config.MAX_ALERT, current_alert + 1)
                    utils.access_memory(config.STATE_FILE, war_state)

                print(f"{C_RED}[RED AI] {C_RESET} 👹 State: {state_key} | Tech: {action} | Impact: {impact} | Q: {new_val:.2f}")

                time.sleep(random.uniform(0.5, 1.5))

            except Exception as e:
                # print(f"Red Error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    bot = RedTeamer()
    bot.run()
