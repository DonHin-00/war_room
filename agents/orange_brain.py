#!/usr/bin/env python3
import sys
import os
import time
import json
import logging
import uuid
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
                        if "RCE" in str(entry) or "exec" in str(entry):
                            attack_counts["RCE"] += 1
                    except: pass
        except: pass

        # Map to MITRE / CWE
        cwe_map = {
            "SQL_INJECTION": "CWE-89",
            "XSS": "CWE-79",
            "RCE": "CWE-78",
            "NETWORK": "T1046 (Network Service Scanning)"
        }

        # Generate Standards
        standards = {
            "timestamp": time.time(),
            "priorities": {},
            "cwe_map": cwe_map
        }

        for attack, count in attack_counts.items():
            urgency = "LOW"
            if count > 5: urgency = "MEDIUM"
            if count > 20: urgency = "HIGH"
            standards["priorities"][attack] = urgency

        logger.info(f"🎓 WORKSHOP: Identified priorities: {standards['priorities']}")
        utils.safe_json_write(self.standards_file, standards)

        # Generate Human-Readable Report
        with open("workshop_report.txt", "w") as f:
            f.write(f"ORANGE TEAM THREAT INTELLIGENCE REPORT - {time.ctime()}\n")
            f.write("===================================================\n")
            for attack, count in attack_counts.items():
                cwe = cwe_map.get(attack, "Unknown")
                f.write(f"- {attack} ({cwe}): {count} incidents\n")

            # Export STIX-like JSON (Simplified)
            with open("threat_report.json", "w") as tr:
                json.dump({"report_id": str(uuid.uuid4()), "incidents": dict(attack_counts)}, tr)

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
