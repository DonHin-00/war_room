#!/usr/bin/env python3
"""
Green Team: User Simulation.
Generates noise, business value (files), and vulnerability (clicks).
"""

import os
import sys
import time
import random
import signal
import secrets

# Add parent dir to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils

# --- VISUALS ---
C_GREEN = "\033[92m"
C_RESET = "\033[0m"

class GreenUser:
    def __init__(self):
        self.running = True
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        self.setup()

    def setup(self):
        print(f"{C_GREEN}[SYSTEM] Green Team (Users) Initialized.{C_RESET}")

    def shutdown(self, signum, frame):
        print(f"\n{C_GREEN}[SYSTEM] Green Team going home...{C_RESET}")
        self.running = False
        sys.exit(0)

    def work(self):
        """Create benign business files."""
        doc_type = secrets.choice(["invoice", "report", "memo", "notes"])
        fname = os.path.join(config.WAR_ZONE_DIR, f"{doc_type}_{int(time.time())}.txt")

        content = f"Business Value: {secrets.token_hex(16)}\nConfidential info."
        try:
            with open(fname, 'w') as f:
                f.write(content)
            # print(f"{C_GREEN}[USER] Created {os.path.basename(fname)}{C_RESET}")
        except: pass

    def browse(self):
        """Simulate activity / noise."""
        time.sleep(random.uniform(0.1, 0.5))

    def mistake(self):
        """Simulate executing a random script (Social Engineering victim)."""
        if not os.path.exists(config.WAR_ZONE_DIR): return

        files = [f for f in os.listdir(config.WAR_ZONE_DIR) if f.endswith(".sh") or f.endswith(".py")]
        if files:
            target = secrets.choice(files)
            # Only click 10% of the time
            if secrets.randbelow(10) == 0:
                print(f"{C_GREEN}[USER] Oops! Clicked {target}{C_RESET}")
                try:
                    path = os.path.join(config.WAR_ZONE_DIR, target)
                    # Simulate execution by touching/accessing
                    utils.read_file_head(path)
                    # If we really wanted to punish, we'd exec it, but that might spawn infinite loops in this single-threaded sim wrapper.
                    # Red Team already has auto-exec logic for payloads.
                except: pass

    def run(self):
        while self.running:
            try:
                action = secrets.choice(["WORK", "WORK", "BROWSE", "MISTAKE"])

                if action == "WORK":
                    self.work()
                elif action == "BROWSE":
                    self.browse()
                elif action == "MISTAKE":
                    self.mistake()

                time.sleep(random.uniform(1.0, 3.0))
            except Exception:
                time.sleep(1)

if __name__ == "__main__":
    bot = GreenUser()
    bot.run()
