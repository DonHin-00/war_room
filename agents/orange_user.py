#!/usr/bin/env python3
import sys
import os
import time
import random
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils
from vnet.nic import VNic

logger = utils.setup_logging("OrangeUser", "logs/orange.log")

class OrangeUser:
    """The User: Generates legitimate traffic baseline."""
    def __init__(self):
        self.nic = VNic(f"10.0.99.{random.randint(2,254)}")
        self.running = True

    def browse(self):
        """Simulate user behavior."""
        actions = [
            {"method": "GET", "path": "/status", "data": {}},
            {"method": "POST", "path": "/login", "data": {"username": "user", "password": "user123"}},
            {"method": "POST", "path": "/transfer", "data": {"amount": random.randint(10, 100)}}
        ]

        action = random.choice(actions)
        if self.nic.connected:
            self.nic.send("10.10.10.10", action)

    def run(self):
        logger.info("🍊 Orange User Online.")
        if not self.nic.connect(): return

        while self.running:
            self.browse()
            time.sleep(random.uniform(0.5, 3.0)) # Random browsing interval

if __name__ == "__main__":
    agent = OrangeUser()
    try:
        agent.run()
    except KeyboardInterrupt:
        pass
