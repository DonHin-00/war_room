#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Red Team)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: MITRE ATT&CK Matrix

This module implements the Red Team Agent in "Emulation Mode".
It simulates an APT moving through a segregated network (DMZ -> USER -> SERVER -> CORE).
"""

import os
import time
import random
import signal
import sys
import logging
import secrets
import shutil
from typing import Dict, Any, Optional

import utils
import config

# Setup Logging
utils.setup_logging(config.PATHS["LOG_RED"])
logger = logging.getLogger("RedTeam")

class RedTeamer:
    def __init__(self):
        self.running = True
        self.iteration_count = 0
        self.audit_logger = utils.AuditLogger(config.PATHS["AUDIT_LOG"])

        utils.limit_resources(ram_mb=config.SYSTEM["RESOURCE_LIMIT_MB"])

        self.state_manager = utils.StateManager(config.PATHS["WAR_STATE"])

        # Access Progression: Starts at DMZ
        self.access_level = "DMZ"
        self.zones = ["DMZ", "USER", "SERVER", "CORE"]

        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def shutdown(self, signum, frame):
        logger.info("Shutting down emulation...")
        self.running = False
        sys.exit(0)

    def update_heartbeat(self):
        hb_file = os.path.join(config.PATHS["DATA_DIR"], "red.heartbeat")
        try:
            with open(hb_file, 'w') as f: f.write(str(time.time()))
        except: pass

    # --- TACTICS ---
    def generate_payload(self, obfuscate=False):
        base_content = b"echo 'malware_payload'"
        if obfuscate:
            # Steganography Logic: Create fake header
            header = b"\xFF\xD8\xFF\xE0" # Fake JPG header
            padding = utils.generate_high_entropy_data(random.randint(512, 4096))
            return header + padding + base_content
        return base_content

    def t1021_lateral_move(self):
        """Attempts to escalate to the next zone."""
        current_idx = self.zones.index(self.access_level)
        if current_idx < len(self.zones) - 1:
            next_zone = self.zones[current_idx + 1]
            self.access_level = next_zone
            return {"impact": 5, "new_zone": next_zone, "status": "escalated"}
        return {"impact": 0, "status": "max_level"}

    def _get_target_dir(self):
        return config.ZONES[self.access_level]

    def t1046_recon(self):
        traps = 0
        target_dir = self._get_target_dir()
        try:
            with os.scandir(target_dir) as it:
                for entry in it:
                    if utils.is_tar_pit(entry.path): traps += 1
        except: pass
        return {"impact": 1, "traps_found": traps}

    def t1027_obfuscate(self):
        target_dir = self._get_target_dir()
        fname = f"photo_{int(time.time())}_{secrets.token_hex(4)}.jpg"
        target_file = os.path.join(target_dir, fname)
        with open(target_file, 'wb') as f:
            f.write(self.generate_payload(obfuscate=True))
        return {"impact": 3, "file": fname}

    def t1003_rootkit(self):
        target_dir = self._get_target_dir()
        fname = f".sys_shadow_{int(time.time())}_{secrets.token_hex(4)}"
        target_file = os.path.join(target_dir, fname)
        with open(target_file, 'w') as f: f.write("uid=0(root)")
        return {"impact": 5, "file": fname}

    def t1036_masquerade(self):
        target_dir = self._get_target_dir()
        names = ["readme.txt", "notes.txt", "todo.list"]
        fname = f"{random.choice(names)}_{secrets.token_hex(4)}"
        target_file = os.path.join(target_dir, fname)
        with open(target_file, 'w') as f: f.write(" benign_header=1\n")
        with open(target_file, 'ab') as f:
            f.write(self.generate_payload(obfuscate=True))
        return {"impact": 4, "file": fname}

    def t1486_encrypt(self):
        target_dir = self._get_target_dir()
        try:
            targets = []
            with os.scandir(target_dir) as it:
                for entry in it:
                    if entry.is_file() and not entry.name.endswith(".enc") and not utils.is_tar_pit(entry.path):
                        targets.append(entry.path)

            if not targets: return {"impact": 0, "status": "no_targets"}

            target = random.choice(targets)
            utils.safe_file_read(target)

            encrypted_path = target + ".enc"
            with open(encrypted_path, 'wb') as f:
                f.write(b"ENCRYPTED_HEADER_V1")
                f.write(utils.generate_high_entropy_data(128))

            os.remove(target)
            return {"impact": 8, "target": os.path.basename(target)}
        except: return {"impact": 0, "status": "failed"}

    def t1071_c2_beacon(self):
        target_dir = self._get_target_dir()
        fname = "c2_beacon.dat"
        target_file = os.path.join(target_dir, fname)
        with open(target_file, 'a') as f:
            f.write(f"{int(time.time())}:HEARTBEAT\n")
        return {"impact": 2, "file": fname}

    def t1055_injection(self):
        if not os.path.exists(config.PATHS["PROC"]): return {"impact": 0}
        pid = random.randint(1000, 65535)
        path = os.path.join(config.PATHS["PROC"], str(pid))
        with open(path, 'w') as f:
            f.write(f"cmd: malicious_daemon\nstart: {time.time()}")
        return {"impact": 5, "pid": pid}

    def t1070_wipe_logs(self):
        if os.path.exists(config.PATHS["AUDIT_LOG"]):
            os.remove(config.PATHS["AUDIT_LOG"])
            return {"impact": 10, "status": "wiped"}
        return {"impact": 0}

    def t1589_lurk(self):
        return {"impact": 0, "status": "lurking"}

    # --- DECISION ENGINE ---

    def decide_action(self):
        """Selects an action based on Access Level Probabilities."""
        zone_probs = config.EMULATION["RED"].get(self.access_level, {})
        if not zone_probs:
            # Fallback to lurk if undefined
            return "T1589_LURK"

        actions = list(zone_probs.keys())
        weights = list(zone_probs.values())

        return random.choices(actions, weights=weights, k=1)[0]

    # --- MAIN LOOP ---

    def engage(self):
        logger.info("Red Team Emulation Initialized. Framework: APT / Lateral Movement")

        if not os.path.exists(config.PATHS["WAR_ZONE"]):
            os.makedirs(config.PATHS["WAR_ZONE"], exist_ok=True)

        while self.running:
            try:
                self.iteration_count += 1
                self.update_heartbeat()
                
                # Perceive (Optional in Emulation, but we check Alert Level)
                war_state = self.state_manager.get_war_state()
                current_alert = war_state.get('blue_alert_level', 1)

                # Decide
                action_name = self.decide_action()
                tactic_func = getattr(self, action_name.lower())

                # Act
                try:
                    result = tactic_func()
                    impact = result.pop("impact", 0)
                    self.audit_logger.log_event("RED", action_name, result)
                    logger.info(f"Action: {action_name} | Impact: {impact} | Zone: {self.access_level}")
                except Exception as e:
                    logger.warning(f"Failed {action_name}: {e}")
                    impact = 0

                # Trigger Alerts
                if impact > 0 and random.random() > 0.5:
                    new_level = min(config.SYSTEM["MAX_ALERT_LEVEL"], current_alert + 1)
                    if new_level != current_alert:
                         self.state_manager.update_war_state({'blue_alert_level': new_level})

                time.sleep(random.uniform(0.5, 2.0))

            except KeyboardInterrupt:
                self.shutdown(None, None)
            except Exception as e:
                logger.error(f"Loop Error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    RedTeamer().engage()
