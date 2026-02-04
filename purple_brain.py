#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Purple Team)
Role: Referee / Safety Valve / Rules of Engagement Enforcer
"""

import os
import time
import json
import signal
import sys

try:
    import utils
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    import utils
import config

STATE_FILE = config.PATHS['STATE_FILE']
BLUE_Q = config.PATHS['BLUE_Q_TABLE']
RED_Q = config.PATHS['RED_Q_TABLE']
BATTLEFIELD = config.PATHS['BATTLEFIELD']

class PurpleReferee:
    def __init__(self):
        self.running = True
        self.audit = utils.AuditLogger()
        self.config = config.PURPLE

        # Setup signal handlers
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)

    def handle_shutdown(self, signum, frame):
        print(f"\n\033[95m[SYSTEM] Purple Team (Referee) Shutting Down...\033[0m")
        self.running = False
        sys.exit(0)

    def penalize_agent(self, agent_q_file, penalty):
        """Apply a massive penalty to an agent's Q-Table to discourage unsafe behavior."""
        q_table = utils.safe_json_read(agent_q_file)
        if not q_table: return

        # Penalize ALL recent actions to suppress the behavior globally
        for key in q_table:
            q_table[key] += penalty

        utils.safe_json_write(agent_q_file, q_table)

    def enforce_roe(self):
        """Check for Rules of Engagement violations."""
        try:
            files = os.listdir(BATTLEFIELD)
            file_count = len(files)

            # 1. Check for Spamming/DoS (Red Team going crazy)
            if file_count > self.config['THRESHOLDS']['MAX_FILES']:
                print(f"\033[95m[PURPLE] ROE VIOLATION: Too many files ({file_count}). Penalizing Red Team.\033[0m")
                self.audit.log_event("PURPLE", "PENALTY_DOS", "RED")
                self.penalize_agent(RED_Q, self.config['PENALTY'])

                # Cleanup
                for f in files:
                    try: os.remove(os.path.join(BATTLEFIELD, f))
                    except: pass

            # 2. Check for "Scorched Earth" (Blue Team deleting everything too fast? hard to track count without state)
            # Instead, let's look at the state file
            state = utils.safe_json_read(STATE_FILE)
            alert = state.get('blue_alert_level', 1)

            # If alert is MAX for too long, dampen it (Safety Valve)
            # This prevents Blue from staying in "Panic Mode" forever
            # Realism: Simulates leadership de-escalation
            if alert == 5:
                # Randomly de-escalate
                if time.time() % 10 < 1:
                    print(f"\033[95m[PURPLE] INTERVENTION: De-escalating Alert Level.\033[0m")
                    state['blue_alert_level'] = 3
                    utils.safe_json_write(STATE_FILE, state)
                    self.audit.log_event("PURPLE", "DE_ESCALATE", "BLUE")

        except Exception as e:
            pass # Referee shouldn't crash

    def run(self):
        print(f"\033[95m[SYSTEM] Purple Team Referee Initialized. Enforcing RoE.\033[0m")
        while self.running:
            self.enforce_roe()
            time.sleep(1)

if __name__ == "__main__":
    referee = PurpleReferee()
    referee.run()
