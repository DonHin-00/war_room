#!/usr/bin/env python3
import sys
import os
import time
import json
import logging
from collections import Counter

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils

logger = utils.setup_logging("OrangeEducator", "logs/orange.log")

class OrangeEducator:
    """The Educator: Analyzes attacks to improve coding standards."""
    def __init__(self):
        self.running = True
        self.standards_file = os.path.join(config.BASE_DIR, "coding_standards.json")

    def analyze_attacks(self):
        """Analyze audit logs to find prevalent attacks."""
        if not os.path.exists(config.AUDIT_LOG): return

        attack_counts = Counter()
        try:
            with open(config.AUDIT_LOG, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        # We look for Red Team activity or Blue Team detections
                        if "IOC_Found" in str(entry) or "NET_ATTACK" in str(entry):
                            attack_counts["NETWORK"] += 1
                        if "SQLi" in str(entry):
                            attack_counts["SQL_INJECTION"] += 1
                        if "XSS" in str(entry):
                            attack_counts["XSS"] += 1
                    except: pass
        except: pass

        # Generate Standards
        standards = {
            "timestamp": time.time(),
            "priorities": {}
        }

        for attack, count in attack_counts.items():
            urgency = "LOW"
            if count > 10: urgency = "MEDIUM"
            if count > 50: urgency = "HIGH"
            standards["priorities"][attack] = urgency

        logger.info(f"🎓 WORKSHOP: Identified priorities: {standards['priorities']}")
        utils.safe_json_write(self.standards_file, standards)

        # Generate Human-Readable Report
        with open("workshop_report.txt", "w") as f:
            f.write(f"ORANGE TEAM WORKSHOP REPORT - {time.ctime()}\n")
            f.write("========================================\n")
            for attack, count in attack_counts.items():
                f.write(f"- {attack}: {count} incidents\n")

    def run(self):
        logger.info("🍊 Orange Educator Team Online.")
        while self.running:
            self.analyze_attacks()
            time.sleep(15) # Periodic workshops

if __name__ == "__main__":
    agent = OrangeEducator()
    try:
        agent.run()
    except KeyboardInterrupt:
        pass
