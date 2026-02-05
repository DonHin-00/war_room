#!/usr/bin/env python3
import sys
import os
import time
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils
from vnet.nic import VNic

logger = utils.setup_logging("GreenOps", "logs/green.log")

class GreenIntegrator:
    """DevSecOps: Monitors health and patches vulnerabilities."""
    def __init__(self):
        self.nic = VNic("10.0.8.8")
        self.running = True

    def monitor(self):
        # Poll Bank Status
        if self.nic.connected:
            self.nic.send("10.10.10.10", {"method": "GET", "path": "/status"})

    def instrument_code(self):
        """Inject logging instrumentation into services."""
        target = os.path.join(config.BASE_DIR, "services/mock_bank.py")
        try:
            with open(target, 'r') as f: content = f.read()

            # Check if instrumented
            if "logger.info(f\"[INSTRUMENTATION]" not in content:
                # Inject logger at start of handle_request
                if "def handle_request(self, msg):" in content:
                    injection = """
        # GREEN TEAM INSTRUMENTATION
        try:
            payload_meta = str(msg.get('payload', {}).get('path', 'unknown'))
            logger.info(f"[INSTRUMENTATION] Request Path: {payload_meta}")
        except: pass
"""
                    parts = content.split("def handle_request(self, msg):")
                    new_content = parts[0] + "def handle_request(self, msg):" + injection + parts[1]

                    with open(target, 'w') as f: f.write(new_content)
                    logger.info("🟢 GREEN TEAM: Instrumented Mock Bank with logging.")
        except: pass

    def run(self):
        logger.info("🟢 Green DevSecOps Online.")
        if not self.nic.connect(): return

        # Listener thread for health checks
        import threading
        def listener():
            while self.running:
                msg = self.nic.recv()
                if msg:
                    # Analyze response time (simulated)
                    pass
        threading.Thread(target=listener, daemon=True).start()

        while self.running:
            self.monitor()
            self.instrument_code()
            time.sleep(10)

if __name__ == "__main__":
    agent = GreenIntegrator()
    try:
        agent.run()
    except KeyboardInterrupt:
        pass
