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

# --- VISUALS ---
C_RED = "\033[91m"
C_RESET = "\033[0m"

class RedTeamer:
    def __init__(self):
        self.running = True
        self.epsilon = config.AI_PARAMS['EPSILON_START']
        self.alpha = config.AI_PARAMS['ALPHA']
        self.q_table = {}
        self.audit_logger = utils.AuditLogger(config.AUDIT_LOG)

        # Signal Handling
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

        self.setup()

    def setup(self):
        print(f"{C_RED}[SYSTEM] Red Team AI Initialized. APT Framework: ACTIVE{C_RESET}")
        self.q_table = utils.access_memory(config.Q_TABLE_RED) or {}
        if not os.path.exists(config.WAR_ZONE_DIR):
            try: os.makedirs(config.WAR_ZONE_DIR)
            except: pass

    def shutdown(self, signum, frame):
        print(f"\n{C_RED}[SYSTEM] Red Team shutting down gracefully...{C_RESET}")
        utils.access_memory(config.Q_TABLE_RED, self.q_table)
        self.running = False
        sys.exit(0)

    def choose_action(self, state_key):
        if random.random() < self.epsilon:
            return random.choice(config.RED_ACTIONS)
        else:
            known = {a: self.q_table.get(f"{state_key}_{a}", 0) for a in config.RED_ACTIONS}
            return max(known, key=known.get)

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
                    except: pass

                elif action == "T1027_OBFUSCATE":
                    fname = os.path.join(config.WAR_ZONE_DIR, f"malware_crypt_{int(time.time())}.bin")
                    try:
                        size = random.randint(800, 1200)
                        data = os.urandom(size).decode('latin1')
                        utils.secure_create(fname, data)
                        impact = 3
                    except: pass

                elif action == "T1003_ROOTKIT":
                    fname = os.path.join(config.WAR_ZONE_DIR, f".sys_shadow_{int(time.time())}")
                    try:
                        utils.secure_create(fname, "uid=0(root)")
                        impact = 5
                    except: pass

                elif action == "T1071_C2_BEACON":
                    fname = os.path.join(config.WAR_ZONE_DIR, f"beacon_{int(time.time())}.c2_beacon")
                    try:
                        payload = f"BEACON_ID:{random.randint(1000,9999)}"
                        utils.secure_create(fname, payload)
                        impact = 4
                        self.audit_logger.log_event("RED", "C2_BEACON", f"Established beacon at {fname}")
                    except: pass

                elif action == "T1589_LURK":
                    impact = 0

                # 4. REWARD
                reward = 0
                if impact > 0: reward = config.RED_REWARDS['IMPACT']
                if current_alert >= 4 and action == "T1589_LURK": reward = config.RED_REWARDS['STEALTH']
                if current_alert == config.MAX_ALERT and impact > 0: reward = config.RED_REWARDS['CRITICAL']
                if action == "T1071_C2_BEACON": reward = config.RED_REWARDS['C2_SUCCESS']

                # 5. LEARN
                old_val = self.q_table.get(f"{state_key}_{action}", 0)
                next_max = max([self.q_table.get(f"{state_key}_{a}", 0) for a in config.RED_ACTIONS])
                new_val = old_val + self.alpha * (reward + config.AI_PARAMS['GAMMA'] * next_max - old_val)
                self.q_table[f"{state_key}_{action}"] = new_val

                if iteration % config.AI_PARAMS['SYNC_INTERVAL'] == 0:
                    utils.access_memory(config.Q_TABLE_RED, self.q_table)

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
