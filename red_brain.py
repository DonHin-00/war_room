#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Red Team)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: MITRE ATT&CK Matrix

This module implements the Red Team Agent in "Emulation Mode".
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

        # Enforce Limits
        utils.limit_resources(ram_mb=config.SYSTEM["RESOURCE_LIMIT_MB"])

        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def shutdown(self, signum, frame):
        logger.info("Shutting down emulation...")
        self.running = False
        sys.exit(0)

    def update_heartbeat(self):
        """Touch a heartbeat file to signal liveness."""
        hb_file = os.path.join(config.PATHS["DATA_DIR"], "red.heartbeat")
        try:
            with open(hb_file, 'w') as f:
                f.write(str(time.time()))
        except: pass

    # --- TACTICS (Same as before) ---
    def generate_payload(self, obfuscate=False):
        base_content = b"echo 'malware_payload'"
        if obfuscate:
            padding = utils.generate_high_entropy_data(random.randint(512, 4096))
            return base_content + b"\n#PAD:" + padding
        return base_content

    def t1046_recon(self):
        traps = 0
        try:
            if os.path.exists(config.PATHS["WAR_ZONE"]):
                with os.scandir(config.PATHS["WAR_ZONE"]) as it:
                    for entry in it:
                        if utils.is_tar_pit(entry.path) or utils.is_honeypot(entry.path):
                            traps += 1
        except: pass
        return {"impact": 1, "traps_found": traps}

    def t1027_obfuscate(self):
        fname = f"malware_crypt_{int(time.time())}_{secrets.token_hex(4)}.bin"
        target_file = os.path.join(config.PATHS["WAR_ZONE"], fname)
        with open(target_file, 'wb') as f:
            f.write(self.generate_payload(obfuscate=True))
        return {"impact": 3, "file": fname}

    def t1003_rootkit(self):
        fname = f".sys_shadow_{int(time.time())}_{secrets.token_hex(4)}"
        target_file = os.path.join(config.PATHS["WAR_ZONE"], fname)
        with open(target_file, 'w') as f: f.write("uid=0(root)")
        return {"impact": 5, "file": fname}

    def t1036_masquerade(self):
        names = ["system.log", "config.ini", "update.tmp"]
        fname = f"{random.choice(names)}_{secrets.token_hex(4)}"
        target_file = os.path.join(config.PATHS["WAR_ZONE"], fname)
        with open(target_file, 'w') as f: f.write(" benign_header=1\n")
        with open(target_file, 'ab') as f:
            f.write(self.generate_payload(obfuscate=True))
        return {"impact": 4, "file": fname}

    def t1486_encrypt(self):
        try:
            targets = []
            with os.scandir(config.PATHS["WAR_ZONE"]) as it:
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
        fname = "c2_beacon.dat"
        target_file = os.path.join(config.PATHS["WAR_ZONE"], fname)
        with open(target_file, 'a') as f:
            f.write(f"{int(time.time())}:HEARTBEAT\n")
        return {"impact": 2, "file": fname}

    def t1055_injection(self):
        if not os.path.exists(config.PATHS["PROC"]):
            try: os.makedirs(config.PATHS["PROC"], mode=0o700)
            except: pass
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

    # --- MAIN LOOP ---

    def engage(self):
        logger.info("Red Team Emulation Initialized. Tactics Loaded.")

        if not os.path.exists(config.PATHS["WAR_ZONE"]):
            os.makedirs(config.PATHS["WAR_ZONE"], exist_ok=True)

        while self.running:
            try:
                self.iteration_count += 1
                self.update_heartbeat() # Liveness check
                
                actions = [
                    (self.t1046_recon, 0.3),
                    (self.t1071_c2_beacon, 0.2),
                    (self.t1027_obfuscate, 0.15),
                    (self.t1036_masquerade, 0.1),
                    (self.t1003_rootkit, 0.1),
                    (self.t1486_encrypt, 0.05),
                    (self.t1055_injection, 0.05),
                    (self.t1070_wipe_logs, 0.05)
                ]

                tactic_func, _ = random.choices(
                    actions,
                    weights=[w for _, w in actions],
                    k=1
                )[0]

                tactic_name = tactic_func.__name__.upper()

                try:
                    result = tactic_func()
                    impact = result.pop("impact", 0)
                    self.audit_logger.log_event("RED", tactic_name, result)
                    logger.info(f"Executed: {tactic_name} | Impact: {impact}")
                except Exception as e:
                    logger.warning(f"Failed {tactic_name}: {e}")

                time.sleep(random.uniform(0.5, 2.0))

            except KeyboardInterrupt:
                self.shutdown(None, None)
            except Exception as e:
                logger.error(f"Loop Error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    RedTeamer().engage()
