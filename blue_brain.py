#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Blue Team)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: NIST SP 800-61, MITRE Shield
"""

import glob
import os
import time
import json
import random
import math
import signal
import sys
import hashlib

import utils
import config

# --- VISUALS ---
C_BLUE = "\033[94m"
C_CYAN = "\033[96m"
C_RESET = "\033[0m"

class BlueDefender:
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
        print(f"{C_CYAN}[SYSTEM] Blue Team AI Initialized. Policy: NIST SP 800-61{C_RESET}")
        self.q_table = utils.access_memory(config.Q_TABLE_BLUE) or {}
        if not os.path.exists(config.INCIDENT_DIR):
            os.makedirs(config.INCIDENT_DIR)

    def shutdown(self, signum, frame):
        print(f"\n{C_CYAN}[SYSTEM] Blue Team shutting down gracefully...{C_RESET}")
        utils.access_memory(config.Q_TABLE_BLUE, self.q_table)
        self.running = False
        sys.exit(0)

    def get_state(self, current_alert):
        visible_threats = glob.glob(os.path.join(config.WAR_ZONE_DIR, 'malware_*'))
        hidden_threats = glob.glob(os.path.join(config.WAR_ZONE_DIR, '.sys_*'))
        c2_beacons = glob.glob(os.path.join(config.WAR_ZONE_DIR, '*.c2_beacon'))

        all_threats = visible_threats + hidden_threats + c2_beacons
        threat_count = len(all_threats)

        return f"{current_alert}_{threat_count}", visible_threats, hidden_threats, c2_beacons, all_threats

    def choose_action(self, state_key):
        if random.random() < self.epsilon:
            return random.choice(config.BLUE_ACTIONS)
        else:
            known = {a: self.q_table.get(f"{state_key}_{a}", 0) for a in config.BLUE_ACTIONS}
            return max(known, key=known.get)

    def report_incident(self, filepath, threat_type, action_taken):
        """Generate a forensic incident report."""
        try:
            timestamp = time.time()
            file_hash = "unknown"
            if os.path.exists(filepath):
                 with open(filepath, 'rb') as f:
                     file_hash = hashlib.sha256(f.read()).hexdigest()
            
            report = {
                'id': hashlib.md5(f"{timestamp}{filepath}".encode()).hexdigest(),
                'timestamp': timestamp,
                'threat_type': threat_type,
                'filepath': filepath,
                'file_hash': file_hash,
                'action': action_taken,
                'status': 'MITIGATED'
            }
            
            report_path = os.path.join(config.INCIDENT_DIR, f"report_{report['id']}.json")
            utils.secure_create(report_path, json.dumps(report, indent=4))
            self.audit_logger.log_event("BLUE", "INCIDENT_REPORT", f"Report {report['id']} generated for {filepath}")
        except Exception as e:
            print(f"Reporting Error: {e}")

    def run(self):
        iteration = 0
        while self.running:
            try:
                iteration += 1

                # 1. OBSERVE
                war_state = utils.access_memory(config.STATE_FILE) or {'blue_alert_level': 1}
                current_alert = war_state.get('blue_alert_level', 1)

                state_key, visible, hidden, c2, all_threats = self.get_state(current_alert)
                threat_count = len(all_threats)

                # 2. DECIDE
                action = self.choose_action(state_key)

                # Decay Epsilon/Alpha
                self.epsilon = max(config.AI_PARAMS['MIN_EPSILON'], self.epsilon * config.AI_PARAMS['EPSILON_DECAY'])
                self.alpha = max(0.1, self.alpha * config.AI_PARAMS['ALPHA_DECAY'])

                # 3. ACT
                mitigated = 0

                if action == "SIGNATURE_SCAN":
                    # Check known signatures
                    known_sigs = utils.access_memory(config.SIGNATURE_FILE) or {}
                    
                    for t in all_threats:
                        try:
                            sz = os.path.getsize(t)
                            if str(sz) in known_sigs:
                                self.report_incident(t, "KNOWN_SIGNATURE", "DELETE")
                                os.remove(t)
                                mitigated += 1
                        except: pass

                    # Visible cleanup
                    for t in visible:
                        if os.path.exists(t):
                            try:
                                self.report_incident(t, "VISIBLE_THREAT", "DELETE")
                                os.remove(t); mitigated += 1
                            except: pass

                elif action == "HEURISTIC_SCAN":
                    for t in all_threats:
                        entropy = utils.calculate_entropy(t)
                        # Detect C2 beacons (usually small, specific pattern) or High Entropy
                        is_c2 = t.endswith(".c2_beacon")

                        if ".sys" in t or entropy > 3.5 or is_c2:
                            try:
                                # Learn Signature
                                sz = os.path.getsize(t)
                                sigs = utils.access_memory(config.SIGNATURE_FILE) or {}
                                if str(sz) not in sigs:
                                    sigs[str(sz)] = entropy
                                    utils.access_memory(config.SIGNATURE_FILE, sigs)
                                    print(f"{C_BLUE}[BLUE LEARNING] Learned signature: Size {sz} | Entropy {entropy:.2f}{C_RESET}")

                                threat_type = "C2_BEACON" if is_c2 else ("HIDDEN_ROOTKIT" if ".sys" in t else "HIGH_ENTROPY")
                                self.report_incident(t, threat_type, "DELETE")

                                os.remove(t)
                                mitigated += 1
                            except: pass

                # 4. REWARD
                reward = 0
                if mitigated > 0: reward = config.BLUE_REWARDS['MITIGATION']
                if action == "HEURISTIC_SCAN" and threat_count == 0: reward = config.BLUE_REWARDS['WASTE']
                if current_alert >= 4 and action == "OBSERVE": reward = config.BLUE_REWARDS['PATIENCE']
                if action == "IGNORE" and threat_count > 0: reward = config.BLUE_REWARDS['NEGLIGENCE']
                
                # 5. LEARN (Q-Learning)
                old_val = self.q_table.get(f"{state_key}_{action}", 0)
                next_max = max([self.q_table.get(f"{state_key}_{a}", 0) for a in config.BLUE_ACTIONS])
                new_val = old_val + self.alpha * (reward + config.AI_PARAMS['GAMMA'] * next_max - old_val)
                self.q_table[f"{state_key}_{action}"] = new_val

                if iteration % config.AI_PARAMS['SYNC_INTERVAL'] == 0:
                    utils.access_memory(config.Q_TABLE_BLUE, self.q_table)

                # 6. UPDATE STATE
                if mitigated > 0 and current_alert < config.MAX_ALERT:
                    war_state['blue_alert_level'] = min(config.MAX_ALERT, current_alert + 1)
                elif mitigated == 0 and current_alert > config.MIN_ALERT and action == "OBSERVE":
                    war_state['blue_alert_level'] = max(config.MIN_ALERT, current_alert - 1)

                utils.access_memory(config.STATE_FILE, war_state)

                # LOG
                icon = "🛡️" if mitigated == 0 else "⚔️"
                print(f"{C_BLUE}[BLUE AI]{C_RESET} {icon} State: {state_key} | Action: {action} | Kill: {mitigated} | Q: {new_val:.2f}")

                time.sleep(0.5 if current_alert >= 4 else 1.0)

            except Exception as e:
                # print(f"Blue Error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    bot = BlueDefender()
    bot.run()
