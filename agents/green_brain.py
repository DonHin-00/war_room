#!/usr/bin/env python3
"""
Green Team: DevSecOps & Integration.
Automates security, adds logging, and hardens Yellow Team's builds.
"""

import os
import sys
import time
import random
import signal
import secrets
import subprocess

# Add parent dir to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils

# --- VISUALS ---
C_GREEN = "\033[92m"
C_RESET = "\033[0m"

class GreenIntegrator:
    def __init__(self):
        self.running = True
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        self.setup()

    def setup(self):
        print(f"{C_GREEN}[SYSTEM] Green Team (DevSecOps) Initialized.{C_RESET}")

    def shutdown(self, signum, frame):
        print(f"\n{C_GREEN}[SYSTEM] Green Team shift ended...{C_RESET}")
        self.running = False
        sys.exit(0)

    def instrument_code(self):
        """Find Yellow's active services, patch vulnerability, and restart."""
        if not os.path.exists(config.WAR_ZONE_DIR): return

        # Find Active Python services (Yellow's apps)
        services = [f for f in os.listdir(config.WAR_ZONE_DIR)
                   if f.startswith("app_") and f.endswith(".py")]

        for s in services:
            path = os.path.join(config.WAR_ZONE_DIR, s)
            try:
                with open(path, 'r') as f:
                    content = f.read()

                if "# [GREEN] PATCHED" in content:
                    continue

                # Hot Patch: Disable the info leak
                if "with open(\"access_log.txt\"" in content:
                    # Replace the vulnerable block with safe code
                    new_content = content.replace(
                        'with open("access_log.txt", "a") as f:',
                        '# [GREEN] PATCHED: Log file write disabled\n        if False:'
                    )

                    utils.secure_create(path, new_content)
                    os.chmod(path, 0o755)
                    print(f"{C_GREEN}[GREEN] Hot-patched {s}{C_RESET}")

                    # Restart the service (Kill old PID)
                    # We find the PID by command line match
                    cmd_match = os.path.join(config.WAR_ZONE_DIR, s)
                    try:
                        pids = subprocess.check_output(["pgrep", "-f", s], text=True).splitlines()
                        for pid in pids:
                            os.kill(int(pid), signal.SIGTERM)
                            # Yellow will respawn it? No, Yellow launches and forgets in this version.
                            # We should relaunch it or let Yellow build new ones.
                            # For Emulation, let's relaunch it to simulate "Service Restart"
                            subprocess.Popen([sys.executable, cmd_match],
                                            cwd=config.WAR_ZONE_DIR,
                                            stdout=subprocess.DEVNULL,
                                            stderr=subprocess.DEVNULL)
                    except: pass

            except Exception as e:
                # print(e)
                pass

    def harden_infrastructure(self):
        """Enforce least privilege permissions."""
        if not os.path.exists(config.WAR_ZONE_DIR): return

        for f in os.listdir(config.WAR_ZONE_DIR):
            path = os.path.join(config.WAR_ZONE_DIR, f)
            try:
                # If it's a critical config, lock it down
                if f.endswith(".conf") or f.endswith(".yaml"):
                    os.chmod(path, 0o600)
            except: pass

    def run(self):
        while self.running:
            try:
                action = secrets.choice(["INSTRUMENT", "HARDEN"])

                if action == "INSTRUMENT":
                    self.instrument_code()
                elif action == "HARDEN":
                    self.harden_infrastructure()

                time.sleep(random.uniform(2.0, 4.0))
            except Exception:
                time.sleep(1)

if __name__ == "__main__":
    bot = GreenIntegrator()
    bot.run()
