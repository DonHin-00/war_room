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
from utils.trace_logger import trace_errors
import config

# --- SYSTEM CONFIGURATION ---
setup_logging(config.file_paths['log_file'])
logger = logging.getLogger("DaemonBrain")

# --- VISUALS ---
C_GREY = "\033[90m"
C_RESET = "\033[0m"

# --- MAIN LOOP ---

@trace_errors
def engage_daemon(max_iterations: Optional[int] = None) -> None:

    msg = f"[SYSTEM] Daemon Agent Initialized. Role: Stress Tester"
    print(f"{C_GREY}{msg}{C_RESET}")
    logger.info(msg)

    watch_dir = config.file_paths['watch_dir']
    network_dir = config.file_paths['network_dir']
    if not os.path.exists(network_dir):
        os.makedirs(network_dir)

    iteration = 0
    try:
        while True:
            if max_iterations is not None and iteration >= max_iterations:
                break
            iteration += 1

            try:
                # 1. NETWORK FUZZING (Packet Loss Simulation)
                # Create random packet files
                if random.random() < 0.4:
                    pkt_name = f"packet_{int(time.time_ns())}.pcap"
                    try:
                        with open(os.path.join(network_dir, pkt_name), 'w') as f:
                            f.write("Fuzz data")
                    except: pass

                # Delete random packet files (Packet Loss)
                if random.random() < 0.4:
                    try:
                        with os.scandir(network_dir) as it:
                            for entry in it:
                                if random.random() < 0.5:
                                    os.remove(entry.path)
                    except: pass

                # 2. FILESYSTEM FLOOD ATTACK
                if random.random() < 0.3:
                    burst_size = random.randint(10, 30)

                    for _ in range(burst_size):
                        if random.random() < 0.2:
                            fname = f"daemon_zero_{time.time_ns()}.tmp"
                            with open(os.path.join(watch_dir, fname), 'w') as f: pass
                        else:
                            fname = f"daemon_noise_{time.time_ns()}.junk"
                            with open(os.path.join(watch_dir, fname), 'w') as f:
                                f.write(os.urandom(100).hex())

                time.sleep(random.uniform(0.1, 0.5))

            except Exception as e:
                logger.error(f"Error in Daemon loop: {e}")
                time.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Daemon Agent Shutting Down")

if __name__ == "__main__":
    engage_daemon()
