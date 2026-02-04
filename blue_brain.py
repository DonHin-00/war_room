#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Blue Team)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: NIST SP 800-61, MITRE Shield
"""

import os
import time
import json
import random
import math
import sys
import signal
import argparse

# Import utils from current directory
try:
    import utils
except ImportError:
    # If running from a different directory, try to append current dir
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    import utils
import config

# --- SYSTEM CONFIGURATION ---
Q_TABLE_FILE = config.PATHS['BLUE_Q_TABLE']
STATE_FILE = config.PATHS['STATE_FILE']
WATCH_DIR = config.PATHS['BATTLEFIELD']
SIGNATURE_DB = config.PATHS['SIGNATURE_DB']

# --- AI HYPERPARAMETERS ---
ACTIONS = config.BLUE['ACTIONS']
ALPHA = config.HYPERPARAMETERS['ALPHA']
ALPHA_DECAY = config.HYPERPARAMETERS['ALPHA_DECAY']
GAMMA = config.HYPERPARAMETERS['GAMMA']
EPSILON = config.HYPERPARAMETERS['EPSILON']
EPSILON_DECAY = config.HYPERPARAMETERS['EPSILON_DECAY']
MIN_EPSILON = config.HYPERPARAMETERS['MIN_EPSILON']

# --- REWARD CONFIGURATION (AI PERSONALITY) ---
R_MITIGATION = config.BLUE['REWARDS']['MITIGATION']
R_PATIENCE = config.BLUE['REWARDS']['PATIENCE']
P_WASTE = config.BLUE['REWARDS']['WASTE']
P_NEGLIGENCE = config.BLUE['REWARDS']['NEGLIGENCE']
MAX_ALERT = config.BLUE['ALERTS']['MAX']
MIN_ALERT = config.BLUE['ALERTS']['MIN']

# --- VISUALS ---
C_BLUE = "\033[94m"
C_CYAN = "\033[96m"
C_RESET = "\033[0m"

# --- DEFENSIVE UTILITIES ---

def calculate_shannon_entropy(filepath):
    """Detects High Entropy (Encrypted/Obfuscated) files."""
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
            if not data: return 0
            return utils.calculate_entropy(data)
    except Exception:
        return 0

def access_memory(filepath, data=None):
    """Atomic JSON I/O."""
    if data is not None:
        utils.safe_json_write(filepath, data)

    # safe_json_read handles empty/missing file
    return utils.safe_json_read(filepath)

# --- MAIN LOOP ---

class BlueDefender:
    def __init__(self, reset=False):
        self.running = True
        self.q_table = {}
        self.signatures = {}
        self.audit = utils.AuditLogger()

        if reset:
            print(f"{C_BLUE}[BLUE AI] Resetting Q-Table...{C_RESET}")
            self.q_table = {}
            self.signatures = {}
            access_memory(Q_TABLE_FILE, self.q_table)
            access_memory(SIGNATURE_DB, self.signatures)
        else:
            # Load initial Q-table and Signatures
            self.q_table = access_memory(Q_TABLE_FILE)
            self.signatures = access_memory(SIGNATURE_DB)

        # Setup signal handlers
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)

    def handle_shutdown(self, signum, frame):
        print(f"\n{C_CYAN}[SYSTEM] Blue Team AI Shutting Down...{C_RESET}")
        self.save_state()
        self.running = False
        sys.exit(0)

    def save_state(self):
        access_memory(Q_TABLE_FILE, self.q_table)
        access_memory(SIGNATURE_DB, self.signatures)

    def learn_signature(self, filepath):
        """Memorize the signature of a confirmed threat."""
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
                # Simple hash for signature (using entropy as a proxy key for now,
                # but a checksum would be better. Let's use simple size+entropy as a signature)
                entropy = utils.calculate_entropy(content)
                sig_key = f"{len(content)}_{entropy:.4f}"
                self.signatures[sig_key] = "MALICIOUS"
                self.audit.log_event("BLUE", "LEARN_SIGNATURE", sig_key, {"entropy": entropy})
        except: pass

    def check_signature(self, filepath):
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
                entropy = utils.calculate_entropy(content)
                sig_key = f"{len(content)}_{entropy:.4f}"
                return sig_key in self.signatures
        except: return False

    def run(self):
        global EPSILON, ALPHA
        print(f"{C_CYAN}[SYSTEM] Blue Team AI Initialized. Policy: NIST SP 800-61{C_RESET}")

        while self.running:
            try:
                # 1. PREPARATION
                war_state = access_memory(STATE_FILE)
                if not war_state: war_state = {'blue_alert_level': 1}

                current_alert = war_state.get('blue_alert_level', 1)

                # 2. DETECTION
                visible_threats = []
                hidden_threats = []
            
                try:
                    with os.scandir(WATCH_DIR) as entries:
                        for entry in entries:
                            if entry.is_file():
                                if entry.name.startswith('malware_'):
                                    visible_threats.append(entry.path)
                                elif entry.name.startswith('.sys_'):
                                    hidden_threats.append(entry.path)
                except OSError:
                    pass # Directory might not exist or be inaccessible

                all_threats = visible_threats + hidden_threats
                threat_count = len(all_threats)
                state_key = f"{current_alert}_{threat_count}"

                # 3. DECISION
                if random.random() < EPSILON:
                    action = random.choice(ACTIONS)
                else:
                    known = {a: self.q_table.get(f"{state_key}_{a}", 0) for a in ACTIONS}
                    action = max(known, key=known.get)

                EPSILON = max(MIN_EPSILON, EPSILON * EPSILON_DECAY)
                ALPHA = max(0.1, ALPHA * ALPHA_DECAY) # Stabilize learning over time

                # 4. ERADICATION
                mitigated = 0

                if action == "SIGNATURE_SCAN":
                    for t in visible_threats:
                        # Check against known signatures first (Fast Path)
                        if self.check_signature(t):
                             try:
                                 os.remove(t); mitigated += 1
                                 self.audit.log_event("BLUE", "MITIGATE_KNOWN", t)
                             except: pass
                        else:
                            # Basic cleanup
                            try:
                                os.remove(t); mitigated += 1
                                self.audit.log_event("BLUE", "MITIGATE_BASIC", t)
                            except: pass

                elif action == "HEURISTIC_SCAN":
                    for t in all_threats:
                        # Policy: Delete if .sys (Hidden) OR Entropy > 3.5 (Obfuscated)
                        # If we find something high entropy, learn it!
                        is_threat = False
                        if ".sys" in t:
                            is_threat = True
                        elif calculate_shannon_entropy(t) > 3.5:
                            is_threat = True
                            self.learn_signature(t)

                        if is_threat:
                            try:
                                os.remove(t); mitigated += 1
                                self.audit.log_event("BLUE", "MITIGATE_HEURISTIC", t)
                            except: pass

                elif action == "OBSERVE": pass
                elif action == "IGNORE": pass

                # 5. REWARD CALCULATION
                reward = 0
                if mitigated > 0: reward = R_MITIGATION
                if action == "HEURISTIC_SCAN" and threat_count == 0: reward = P_WASTE
                if current_alert >= 4 and action == "OBSERVE": reward = R_PATIENCE
                if action == "IGNORE" and threat_count > 0: reward = P_NEGLIGENCE

                # 6. LEARN
                old_val = self.q_table.get(f"{state_key}_{action}", 0)
                next_max = max([self.q_table.get(f"{state_key}_{a}", 0) for a in ACTIONS])
                new_val = old_val + ALPHA * (reward + GAMMA * next_max - old_val)
                self.q_table[f"{state_key}_{action}"] = new_val

                # Save every iteration (safe but slow) or rely on shutdown?
                # Let's save every 10 iterations to improve IO?
                # For this task, sticking to correctness first.
                access_memory(Q_TABLE_FILE, self.q_table)

                # 7. UPDATE WAR STATE
                if mitigated > 0 and current_alert < MAX_ALERT:
                    war_state['blue_alert_level'] = min(MAX_ALERT, current_alert + 1)
                elif mitigated == 0 and current_alert > MIN_ALERT and action == "OBSERVE":
                    war_state['blue_alert_level'] = max(MIN_ALERT, current_alert - 1)

                access_memory(STATE_FILE, war_state)

                # LOG
                icon = "🛡️" if mitigated == 0 else "⚔️"
                print(f"{C_BLUE}[BLUE AI]{C_RESET} {icon} State: {state_key} | Action: {action} | Kill: {mitigated} | Q: {new_val:.2f}")

                time.sleep(0.5 if current_alert >= 4 else 1.0)

            except Exception as e:
                # print(f"Error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset Q-Table")
    parser.add_argument("--debug", action="store_true", help="Debug mode (unused for now)")
    args = parser.parse_args()

    defender = BlueDefender(reset=args.reset)
    defender.run()
