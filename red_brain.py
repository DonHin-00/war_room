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
import socket
import logging
import threading
from threat_intel import ThreatIntel
import config

# --- SETUP LOGGING ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [RED] - %(message)s')

class RedAgent:
    def __init__(self):
        self.threat_intel = ThreatIntel()
        self.threat_intel.fetch_feed()
        self.q_table = self.load_memory(config.Q_TABLE_RED)
        self.state = {'alert_level': 1}
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
        # Read shared state (simulating recon)
        if os.path.exists(config.STATE_FILE):
            try:
                with open(config.STATE_FILE, 'r') as f:
                    self.state = json.load(f)
            except: pass
        return str(self.state.get('blue_alert_level', 1))

    def choose_action(self, state_key):
        if random.random() < self.epsilon:
            return random.choice(config.RED_ACTIONS)
        else:
            # Exploitation: Best known action
            values = {a: self.q_table.get(f"{state_key}_{a}", 0) for a in config.RED_ACTIONS}
            # Fallback if unknown
            if not values: return random.choice(config.RED_ACTIONS)
            return max(values, key=values.get)

    def learn(self, state_key, action, reward, next_state_key):
        old_val = self.q_table.get(f"{state_key}_{action}", 0)

        next_values = [self.q_table.get(f"{next_state_key}_{a}", 0) for a in config.RED_ACTIONS]
        next_max = max(next_values) if next_values else 0

        new_val = old_val + self.alpha * (reward + self.gamma * next_max - old_val)
        self.q_table[f"{state_key}_{action}"] = new_val
        self.save_memory(config.Q_TABLE_RED, self.q_table)

    # --- TACTICS ---

    def beacon(self):
        """T1071: Application Layer Protocol - C2 Beaconing"""
        target_ip = self.threat_intel.get_random_c2()
        if not target_ip: target_ip = "127.0.0.1"
        port = 80 # Default to HTTP port for now

        # Sometimes pick a random port 443 or 8080
        if random.random() > 0.5: port = 443

        logging.info(f"Initiating C2 beacon to {target_ip}:{port}...")

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3.0) # Hold connection state for 3s (SYN_SENT)
            result = s.connect_ex((target_ip, port))
            
            if result == 0:
                logging.info(f"C2 Connection ESTABLISHED to {target_ip}")
                time.sleep(2) # Hold the connection open
                s.close()
                return 10 # Success reward
            else:
                logging.info(f"C2 Connection failed (code {result}) to {target_ip} (expected if blocked)")
                return 2 # Partial reward for attempting
        except Exception as e:
            logging.error(f"Beacon error: {e}")
            return 0

    def persist(self):
        """T1547: Boot or Logon Autostart Execution"""
        # Create a harmless .desktop file in ~/.config/autostart/ (or /tmp/autostart for safety)
        # We'll use /tmp/ as a playground unless we want to be really annoying
        target_dir = os.path.expanduser("~/.config/autostart")
        if not os.path.exists(target_dir):
            try:
                os.makedirs(target_dir)
            except:
                target_dir = "/tmp" # Fallback

        filename = f"system_update_{int(time.time())}.desktop"
        path = os.path.join(target_dir, filename)

        content = """
[Desktop Entry]
Type=Application
Name=System Update
Exec=/bin/sleep 100
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
"""
        try:
            with open(path, 'w') as f:
                f.write(content)
            logging.info(f"Persistence established: {path}")
            return 8
        except Exception as e:
            logging.error(f"Persistence failed: {e}")
            return 0

    def recon(self):
        """T1046: Network Service Scanning"""
        logging.info("Scanning local environment...")
        time.sleep(1)
        return 1

    def run(self):
        logging.info("Engaging Red Team Operations...")
        while self.running:
            try:
                state_key = self.get_state_key()
                action = self.choose_action(state_key)
                
                logging.info(f"Executing: {action}")
                reward = 0
                
                if action == "T1071_C2_BEACON":
                    reward = self.beacon()
                elif action == "T1589_LURK":
                    logging.info("Lurking (Sleep)...")
                    time.sleep(2)
                    reward = 1
                elif action == "T1003_ROOTKIT":
                    # Simulate rootkit by touching a hidden file
                    try:
                        with open("/tmp/.rootkit_marker", "w") as f: f.write("1")
                        logging.info("Rootkit marker placed")
                        reward = 5
                    except: pass
                elif action == "T1027_OBFUSCATE":
                     # Rename process (if possible) or just log
                     logging.info("Obfuscating payload...")
                     reward = 2
                elif action == "T1046_RECON":
                    reward = self.recon()
                elif action == "T1547_PERSIST":
                    reward = self.persist()
                
                # Decay epsilon
                self.epsilon = max(config.EPSILON_MIN, self.epsilon * config.EPSILON_DECAY)

                # Learn
                next_state_key = self.get_state_key()
                self.learn(state_key, action, reward, next_state_key)

                time.sleep(random.uniform(1, 3))

            except KeyboardInterrupt:
                logging.info("Red Team withdrawing.")
                self.running = False
            except Exception as e:
                logging.error(f"Red Brain Crash: {e}")
                time.sleep(1)

if __name__ == "__main__":
    agent = RedAgent()
    agent.run()
