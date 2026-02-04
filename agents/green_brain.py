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
        """Find Yellow's services and inject logging (Instrumentation)."""
        if not os.path.exists(config.WAR_ZONE_DIR): return

        # Find Python services that aren't malware
        services = [f for f in os.listdir(config.WAR_ZONE_DIR)
                   if f.startswith("service_") and f.endswith(".py")]

        for s in services:
            path = os.path.join(config.WAR_ZONE_DIR, s)
            try:
                with open(path, 'r') as f:
                    content = f.read()

                if "# [GREEN] INSTRUMENTED" in content:
                    continue # Already secured

                # Inject logging (Simulation of adding a security agent)
                injection = f"""
# [GREEN] INSTRUMENTED
print("[SECURITY] Service {s} monitored.")
"""
                new_content = injection + content
                utils.secure_create(path, new_content)
                os.chmod(path, 0o755)
                # print(f"{C_GREEN}[GREEN] Instrumented {s}{C_RESET}")

            except: pass

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
