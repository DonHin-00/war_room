#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Orange Team - Interaction/Facilitators)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: Simulation
"""

import os
import sys
import time
import random
import logging
from typing import Optional, List, Dict, Any

# Adjust path to import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    atomic_json_io,
    atomic_json_update,
    setup_logging,
    AuditLogger
)
from utils.trace_logger import trace_errors
import config

# --- SYSTEM CONFIGURATION ---
setup_logging(config.file_paths['log_file'])
logger = logging.getLogger("OrangeBrain")
audit = AuditLogger(config.file_paths['audit_log'])

# --- VISUALS ---
C_ORANGE = "\033[38;5;208m" # ANSI 256 for Orange
C_RESET = "\033[0m"

# --- MAIN LOOP ---

@trace_errors
def engage_facilitation(max_iterations: Optional[int] = None) -> None:

    msg = f"[SYSTEM] Orange Team AI Initialized. Role: Facilitation & Communication"
    print(f"{C_ORANGE}{msg}{C_RESET}")
    logger.info(msg)

    state_file = config.file_paths['state_file']

    iteration = 0
    try:
        while True:
            if max_iterations is not None and iteration >= max_iterations:
                break
            iteration += 1

            try:
                # 1. TABLETOP EXERCISE (Communication)
                # Orange ensures that insights are shared. In this sim, it boosts learning rates.
                if random.random() < 0.1: # 10% chance
                    logger.info("🗣️  Orange Team conducting Tabletop Exercise")
                    # We can't easily modify the running agents' memory directly without complex IPC.
                    # Instead, we'll log a "Game Day" event which Purple could pick up, or we assume
                    # the agents read a shared "learning_boost" flag.
                    # For now, let's just log it as a simulation event.
                    audit.log("ORANGE", "TABLETOP_EXERCISE", {"topic": "Incident Response"})

                # 2. FORCE GAME DAY (Chaos Injection / Stress Test Coordination)
                # Orange coordinates with Daemon/Red to test Blue.
                if random.random() < 0.05:
                    logger.info("🔥 Orange Team initiating GAME DAY scenario")
                    def set_game_day(state):
                        state['game_day_active'] = True
                        return state
                    atomic_json_update(state_file, set_game_day)

                    # Wait for a bit then disable
                    time.sleep(5)
                    def end_game_day(state):
                        state['game_day_active'] = False
                        return state
                    atomic_json_update(state_file, end_game_day)
                    logger.info("🏁 Game Day concluded")

                time.sleep(3.0)

            except Exception as e:
                logger.error(f"Error in Orange loop: {e}")
                time.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Orange Team AI Shutting Down")

if __name__ == "__main__":
    engage_facilitation()
