#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Orange Team - Facilitators)
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
    atomic_json_io,
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
C_ORANGE = "\033[38;5;208m"
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
                # 1. READ WAR STATE
                war_state = atomic_json_io(state_file)
                alert_level = war_state.get('blue_alert_level', 1)

                # 2. TABLETOP EXERCISE SIMULATION
                # Every now and then, announce a "Test Scenario" to the logs
                if random.random() < 0.01: # 1% chance
                    scenarios = ["Phishing Campaign", "DDoS Attack", "Insider Threat", "Supply Chain Compromise"]
                    topic = random.choice(scenarios)
                    logger.info(f"📢 Orange Team initiating Tabletop Exercise: {topic}")
                    audit.log("ORANGE", "TABLETOP_EXERCISE", {"topic": topic})

                # 3. OBSERVATION & METRICS
                # In a real tool, this would generate reports. Here we just log.
                if alert_level >= 4:
                    # High alert? Orange team observes "Crisis Management"
                    pass

                time.sleep(5.0)

            except Exception as e:
                logger.error(f"Error in Orange loop: {e}")
                time.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Orange Team AI Shutting Down")

if __name__ == "__main__":
    engage_facilitation()
