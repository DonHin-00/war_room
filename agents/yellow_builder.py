#!/usr/bin/env python3
import sys
import os
import time
import random
import logging

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils
from vnet.nic import VNic

logger = utils.setup_logging("YellowBuilder", "logs/yellow.log")

class YellowBuilder:
    """The Developer: Pushes updates to the Bank Service."""
    def __init__(self):
        self.nic = VNic("10.0.5.5")
        self.running = True

    def deploy_update(self):
        """Simulate a CI/CD deployment."""
        update_type = random.choice(["FEATURE", "BUGFIX", "HOTFIX"])
        quality = random.choice(["SECURE", "VULNERABLE", "BROKEN"])

        logger.info(f"🔨 DEPLOYING {update_type} ({quality})...")

        # In a real sim, we'd modify the code.
        # Here we send a signal to the Bank via VNet to simulate "Maintenance Mode" or "New Feature"
        # Or we can just drop a file.

        msg = {
            "cmd": "DEPLOY",
            "type": update_type,
            "quality": quality
        }

        # Target: Bank
        if self.nic.connected:
            self.nic.send("10.10.10.10", msg)

    def run(self):
        logger.info("👷 Yellow Builder Team Online.")
        if not self.nic.connect():
            logger.error("Failed to connect to VNet.")
            return

        while self.running:
            # Develop...
            time.sleep(random.randint(10, 30))
            self.deploy_update()

if __name__ == "__main__":
    agent = YellowBuilder()
    try:
        agent.run()
    except KeyboardInterrupt:
        pass
