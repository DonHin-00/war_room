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
        self.standards_file = os.path.join(config.BASE_DIR, "coding_standards.json")

    def deploy_update(self):
        """Simulate a CI/CD deployment based on Orange's standards."""
        # Read Standards
        standards = utils.safe_json_read(self.standards_file, {})
        priorities = standards.get("priorities", {})

        # Determine Quality based on pressure
        # If SQLi urgency is HIGH, we focus on security (SECURE)
        # If no urgency, we might rush features (VULNERABLE)

        quality = "VULNERABLE" # Default rush
        secure_mode = False

        if priorities.get("SQL_INJECTION") == "HIGH" or priorities.get("NETWORK") == "HIGH":
            secure_mode = True
            quality = "SECURE"

        update_type = random.choice(["FEATURE", "BUGFIX"])

        logger.info(f"🔨 DEPLOYING {update_type} ({quality}) [SecureMode: {secure_mode}]")

        # Notify Switch/Bank
        msg = {
            "cmd": "DEPLOY",
            "type": update_type,
            "quality": quality
        }

        if self.nic.connected:
            self.nic.send("10.10.10.10", msg)

        # Actually modify the bank code (Simulated Refactor)
        # If Secure Mode, we could remove the SQLi vulnerability from mock_bank.py
        if secure_mode:
            self.patch_vulnerabilities()

    def patch_vulnerabilities(self):
        """Attempt to fix code."""
        target = os.path.join(config.BASE_DIR, "services/mock_bank.py")
        try:
            with open(target, 'r') as f: content = f.read()

            # Simple patch: Remove the SQLi bypass line
            if "' OR '1'='1" in content:
                new_content = content.replace("if \"'\" in user or \"OR\" in user:", "# PATCHED: Input Validation\n        if False:")
                with open(target, 'w') as f: f.write(new_content)
                logger.info("🛡️  YELLOW TEAM: Patched SQL Injection vulnerability.")
        except: pass

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
