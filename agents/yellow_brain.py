#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Yellow Team - Builders/Admins)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: Simulation
"""

import os
import sys
import time
import random
import logging
from typing import Optional

# Adjust path to import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    setup_logging,
    AuditLogger
)
from utils.trace_logger import trace_errors
import config

# --- SYSTEM CONFIGURATION ---
setup_logging(config.file_paths['log_file'])
logger = logging.getLogger("YellowBrain")
audit = AuditLogger(config.file_paths['audit_log'])

# --- VISUALS ---
C_YELLOW = "\033[93m"
C_RESET = "\033[0m"

# --- MAIN LOOP ---

@trace_errors
def engage_build(max_iterations: Optional[int] = None) -> None:

    msg = f"[SYSTEM] Yellow Team AI Initialized. Role: Builders & Admins"
    print(f"{C_YELLOW}{msg}{C_RESET}")
    logger.info(msg)

    watch_dir = config.file_paths['watch_dir']

    iteration = 0
    try:
        while True:
            if max_iterations is not None and iteration >= max_iterations:
                break
            iteration += 1

            try:
                # 1. DEVELOPMENT (Create Infrastructure)
                if random.random() < 0.2:
                    app_name = f"app_v{random.randint(1,10)}_{int(time.time())}.py"
                    filepath = os.path.join(watch_dir, app_name)
                    try:
                        with open(filepath, 'w') as f:
                            f.write("print('Hello World')\n# TODO: Add security")
                        logger.info(f"🏗️  Yellow Team Deployed: {app_name}")
                    except: pass

                # 2. PATCH MANAGEMENT (Hardening)
                # "Patch" an app by updating its timestamp/content
                if random.random() < 0.1:
                    try:
                        with os.scandir(watch_dir) as it:
                            for entry in it:
                                if entry.is_file() and entry.name.startswith("app_v"):
                                    # Simulate patching
                                    os.utime(entry.path, None)
                                    logger.info(f"🛡️  Yellow Team Patched: {entry.name}")
                                    break
                    except: pass

                # 3. MISCONFIGURATION (The "Insider Mistake")
                if random.random() < 0.05:
                    try:
                        with os.scandir(watch_dir) as it:
                            for entry in it:
                                if entry.is_file() and entry.name.startswith("malware_"):
                                    new_name = f"authorized_tool_{int(time.time())}.exe"
                                    new_path = os.path.join(watch_dir, new_name)
                                    os.rename(entry.path, new_path)
                                    logger.warning(f"⚠️  Yellow Team Misconfiguration! Renamed {entry.name} -> {new_name}")
                                    audit.log("YELLOW", "MISCONFIGURATION", {"original": entry.name, "new": new_name})
                                    break
                    except: pass

                # 4. SHADOW IT (Unsanctioned Tools)
                if random.random() < 0.05:
                    tool_name = f"debug_tool_{random.randint(100,999)}.exe"
                    filepath = os.path.join(watch_dir, tool_name)
                    try:
                        with open(filepath, 'wb') as f:
                            f.write(os.urandom(512))
                        logger.info(f"💾 Yellow Team Installed Tool: {tool_name}")
                    except: pass

                time.sleep(random.uniform(2.0, 4.0))

            except Exception as e:
                logger.error(f"Error in Yellow loop: {e}")
                time.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Yellow Team AI Shutting Down")

if __name__ == "__main__":
    engage_build()
