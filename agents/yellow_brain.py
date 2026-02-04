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
C_YELLOW = "\033[93m"
C_RESET = "\033[0m"

class YellowBuilder:
    """
    Yellow Team: Builders & Developers.
    Creates infrastructure, writes code, and occasionally introduces vulnerabilities (simulated).
    """
    def __init__(self):
        self.running = True
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        self.setup()

    def setup(self):
        print(f"{C_YELLOW}[SYSTEM] Yellow Team (Builders) Initialized.{C_RESET}")

    def shutdown(self, signum, frame):
        print(f"\n{C_YELLOW}[SYSTEM] Yellow Team finished sprint...{C_RESET}")
        self.running = False
        sys.exit(0)

    def build_service(self):
        """Create a 'Service' (Python script) in the War Zone."""
        service_type = secrets.choice(["api", "worker", "auth", "db_connector"])
        fname = os.path.join(config.WAR_ZONE_DIR, f"service_{service_type}_{secrets.token_hex(4)}.py")

        # Simulated source code
        content = f"""
#!/usr/bin/env python3
# Service: {service_type}
import time
import os

def run_task():
    # Processing data...
    data = "{secrets.token_hex(16)}"
    print(f"[{service_type}] Processing {{data}}")
    time.sleep(1)

if __name__ == "__main__":
    run_task()
"""
        try:
            utils.secure_create(fname, content.strip())
            os.chmod(fname, 0o755)
            # print(f"{C_YELLOW}[YELLOW] Built {os.path.basename(fname)}{C_RESET}")
        except: pass

    def patch_vulnerability(self):
        """Simulate patching: Rename/Delete old artifacts."""
        if not os.path.exists(config.WAR_ZONE_DIR): return
        # Logic: Find old services or files and 'update' them
        pass

    def run(self):
        while self.running:
            try:
                # Check for Coding Standards from Orange
                standards_path = os.path.join(config.BASE_DIR, "intelligence", "coding_standards.json")
                if os.path.exists(standards_path):
                    # In a real sim, we'd read this and adjust 'vulnerability rate'
                    pass

                action = secrets.choice(["BUILD", "BUILD", "PATCH"])

                if action == "BUILD":
                    self.build_service()
                elif action == "PATCH":
                    self.patch_vulnerability()

                time.sleep(random.uniform(2.0, 5.0))
            except Exception:
                time.sleep(1)

if __name__ == "__main__":
    bot = YellowBuilder()
    bot.run()
