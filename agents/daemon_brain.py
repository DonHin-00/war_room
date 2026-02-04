#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Daemon - Chaos/Stress Tester)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: Chaos Engineering
"""

import os
import sys
import time
import random
import logging
import string
from typing import Optional

# Adjust path to import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import setup_logging
import config

# --- SYSTEM CONFIGURATION ---
setup_logging(config.file_paths['log_file'])
logger = logging.getLogger("DaemonBrain")

# --- VISUALS ---
C_GREY = "\033[90m"
C_RESET = "\033[0m"

# --- MAIN LOOP ---

def engage_daemon(max_iterations: Optional[int] = None) -> None:

    msg = f"[SYSTEM] Daemon Agent Initialized. Role: Stress Tester"
    print(f"{C_GREY}{msg}{C_RESET}")
    logger.info(msg)

    watch_dir = config.file_paths['watch_dir']

    iteration = 0
    try:
        while True:
            if max_iterations is not None and iteration >= max_iterations:
                break
            iteration += 1

            try:
                # FLOOD ATTACK: Create many files rapidly
                if random.random() < 0.5:
                    burst_size = random.randint(10, 50)
                    logger.info(f"Initiating Flood: {burst_size} files")

                    for _ in range(burst_size):
                        # Edge Case: Zero byte file
                        if random.random() < 0.2:
                            fname = f"daemon_zero_{time.time_ns()}.tmp"
                            with open(os.path.join(watch_dir, fname), 'w') as f: pass

                        # Edge Case: Deep nesting (simulated with long name)
                        elif random.random() < 0.2:
                            long_name = "nested_" + "dir_" * 10 + str(time.time_ns()) + ".log"
                            # Note: We aren't creating actual dirs to avoid cleanup hell, just long names
                            with open(os.path.join(watch_dir, long_name), 'w') as f: f.write("x")

                        # Edge Case: Rapid create/delete (Flicker)
                        elif random.random() < 0.3:
                            fname = f"daemon_flicker_{time.time_ns()}.dat"
                            fpath = os.path.join(watch_dir, fname)
                            with open(fpath, 'w') as f: f.write("FLICKER")
                            try: os.remove(fpath)
                            except: pass

                        else:
                            # Standard noise
                            fname = f"daemon_noise_{time.time_ns()}. junk"
                            with open(os.path.join(watch_dir, fname), 'w') as f:
                                f.write(os.urandom(100).hex())

                time.sleep(random.uniform(0.1, 0.5)) # Very fast cycle

            except Exception as e:
                logger.error(f"Error in Daemon loop: {e}")
                time.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Daemon Agent Shutting Down")

if __name__ == "__main__":
    engage_daemon()
