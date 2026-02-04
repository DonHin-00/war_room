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
import signal
import subprocess
import logging
import re
from threat_intel import ThreatIntel
import config

# --- SETUP LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [BLUE] - %(message)s')

class BlueDefender:
    def __init__(self):
        self.threat_intel = ThreatIntel()
        self.threat_intel.fetch_feed()
        self.q_table = self.load_memory(config.Q_TABLE_BLUE)
        self.state = {'blue_alert_level': 1}
        self.running = True

        # Hyperparameters
        self.epsilon = config.EPSILON_START
        self.alpha = config.ALPHA
        self.gamma = config.GAMMA

    def load_memory(self, filepath):
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f: return json.load(f)
            except: return {}
        return {}

    def save_memory(self, filepath, data):
        try:
            with open(filepath, 'w') as f: json.dump(data, f, indent=4)
        except: pass

    def get_state_key(self):
        # Read alert level
        return str(self.state.get('blue_alert_level', 1))

    def choose_action(self, state_key):
        if random.random() < self.epsilon:
            return random.choice(config.BLUE_ACTIONS)
        else:
            values = {a: self.q_table.get(f"{state_key}_{a}", 0) for a in config.BLUE_ACTIONS}
            if not values: return random.choice(config.BLUE_ACTIONS)
            return max(values, key=values.get)

    def learn(self, state_key, action, reward, next_state_key):
        old_val = self.q_table.get(f"{state_key}_{action}", 0)

        next_values = [self.q_table.get(f"{next_state_key}_{a}", 0) for a in config.BLUE_ACTIONS]
        next_max = max(next_values) if next_values else 0

        new_val = old_val + self.alpha * (reward + self.gamma * next_max - old_val)
        self.q_table[f"{state_key}_{action}"] = new_val
        self.save_memory(config.Q_TABLE_BLUE, self.q_table)

    # --- DEFENSIVE UTILITIES ---

    def network_hunt(self):
        """Scan active connections for IOCs"""
        logging.info("Scanning network connections (ss -tunap)...")
        hits = 0
        try:
            # Run ss to get all TCP/UDP connections with process info
            # -t: tcp, -u: udp, -n: numeric, -a: all, -p: processes
            output = subprocess.check_output(["ss", "-tunap"], text=True)
            
            for line in output.splitlines():
                # Parse remote IP
                # Example: tcp ESTAB 0 0 10.0.0.1:45322 1.2.3.4:80 users:(("python3",pid=123,fd=3))
                # Regex to extract remote IP and PID
                match = re.search(r'\s+(\d+\.\d+\.\d+\.\d+):(\d+)\s+users:\(\(".*?",pid=(\d+)', line)
                if match:
                    remote_ip = match.group(1)
                    remote_port = match.group(2)
                    pid = int(match.group(3))
                    
                    if self.threat_intel.is_malicious(remote_ip):
                        logging.warning(f"IOC DETECTED! Process {pid} connected to malicious IP {remote_ip}:{remote_port}")
                        self.terminate_threat(pid)
                        hits += 1

                    # Also check against local "known bad" from Red Team logs/state if we want to cheat (simulation)
                    # But we are doing emulation, so we stick to the feed.
            
            return 20 if hits > 0 else -1 # High reward for catch, slight penalty for waste
        except Exception as e:
            logging.error(f"Network scan failed: {e}")
            return 0

    def terminate_threat(self, pid):
        try:
            # Verify it's not a critical system process (simple check)
            if pid < 1000:
                logging.warning(f"Refusing to kill system PID {pid}")
                return

            # Check process name
            try:
                with open(f"/proc/{pid}/cmdline", 'r') as f:
                    cmd = f.read()
                    logging.info(f"Terminating PID {pid}: {cmd}")
            except: pass

            os.kill(pid, signal.SIGKILL)
            logging.info(f"Process {pid} KILLED.")
            self.escalate_alert()
        except ProcessLookupError:
            logging.info(f"Process {pid} already dead.")
        except Exception as e:
            logging.error(f"Failed to kill {pid}: {e}")

    def file_scan_heuristic(self):
        """Scan for suspicious files (persistence)"""
        logging.info("Scanning for persistence artifacts...")
        hits = 0
        # Check ~/.config/autostart
        target_dir = os.path.expanduser("~/.config/autostart")
        if os.path.exists(target_dir):
            for f in os.listdir(target_dir):
                # Heuristic: Only target our known simulation pattern "system_update_"
                if f.endswith(".desktop") and f.startswith("system_update_"):
                    full_path = os.path.join(target_dir, f)
                    try:
                        os.remove(full_path)
                        logging.warning(f"Removed suspicious persistence file: {full_path}")
                        hits += 1
                        self.escalate_alert()
                    except: pass

        # Check /tmp/ for suspicious scripts
        for f in os.listdir("/tmp"):
            if f.startswith("malware_") or f.startswith(".sys_") or f == ".rootkit_marker":
                try:
                    os.remove(os.path.join("/tmp", f))
                    logging.warning(f"Removed artifact: {f}")
                    hits += 1
                except: pass
                
        return 10 if hits > 0 else -1

    def escalate_alert(self):
        self.state['blue_alert_level'] = min(config.MAX_ALERT_LEVEL, self.state['blue_alert_level'] + 1)
        self.save_memory(config.STATE_FILE, self.state)

    def deescalate_alert(self):
        self.state['blue_alert_level'] = max(config.MIN_ALERT_LEVEL, self.state['blue_alert_level'] - 1)
        self.save_memory(config.STATE_FILE, self.state)

    def run(self):
        logging.info("Blue Defender Active. Monitoring...")
        while self.running:
            try:
                state_key = self.get_state_key()
                action = self.choose_action(state_key)

                logging.info(f"Action: {action} (Alert Level: {state_key})")
                reward = 0

                if action == "NETWORK_HUNT":
                    reward = self.network_hunt()
                elif action == "HEURISTIC_SCAN":
                    reward = self.file_scan_heuristic()
                elif action == "SIGNATURE_SCAN":
                    # Placeholder for signature scan
                    time.sleep(1)
                    reward = 0
                elif action == "OBSERVE":
                    time.sleep(1)
                    # Small reward for patience if alert is high
                    if int(state_key) > 3: reward = 5
                elif action == "IGNORE":
                    time.sleep(1)
                    reward = -5 # Don't ignore things

                # Decay epsilon
                self.epsilon = max(config.EPSILON_MIN, self.epsilon * config.EPSILON_DECAY)

                # Learn
                next_state_key = self.get_state_key()
                self.learn(state_key, action, reward, next_state_key)

                # Cooldown
                time.sleep(random.uniform(1, 2))

            except KeyboardInterrupt:
                logging.info("Blue Team standing down.")
                self.running = False
            except Exception as e:
                logging.error(f"Blue Brain Crash: {e}")
                time.sleep(1)

if __name__ == "__main__":
    defender = BlueDefender()
    defender.run()
