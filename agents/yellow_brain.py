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

from utils import setup_logging
from utils.trace_logger import trace_errors
import config

# --- SYSTEM CONFIGURATION ---
setup_logging(config.file_paths['log_file'])
logger = logging.getLogger("YellowBrain")

# --- VISUALS ---
C_YELLOW = "\033[93m"
C_RESET = "\033[0m"

# --- MAIN LOOP ---

@trace_errors
def engage_construction(max_iterations: Optional[int] = None) -> None:

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
                # 1. DEPLOY NEW "SERVICES" (Files)
                # Simulates normal IT activity which might look like threats or just add noise

                # Create a "System Log" (Benign)
                log_name = f"system_log_{int(time.time())}.log"
                path = os.path.join(watch_dir, log_name)
                try:
                    with open(path, 'w') as f:
                        f.write(f"System Check OK: {time.time()}")
                except: pass

                # Create a "Config Update" (Benign but High Entropy?)
                if random.random() < 0.2:
                    conf_name = f"app_config_{random.randint(1000,9999)}.xml"
                    path = os.path.join(watch_dir, conf_name)
                    try:
                        with open(path, 'w') as f:
                            f.write("<xml><key>" + os.urandom(32).hex() + "</key></xml>")
                    except: pass

                # 2. MISCONFIGURATION SIMULATION
                # 5% chance to create a file with weak permissions (simulated via name)
                if random.random() < 0.05:
                    path = os.path.join(watch_dir, "world_writable_secrets.txt")
                    try:
                        with open(path, 'w') as f: f.write("password=guest")
                        logger.warning("⚠️  Yellow Team pushed a Misconfiguration")
                    except: pass

                time.sleep(random.uniform(3.0, 6.0)) # Builders work slower

            except Exception as e:
                logger.error(f"Error in Yellow loop: {e}")
                time.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Yellow Team AI Shutting Down")

if __name__ == "__main__":
    engage_construction()
