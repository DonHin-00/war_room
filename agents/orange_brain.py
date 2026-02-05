#!/usr/bin/env python3
"""
Orange Team: Education & Training.
Analyzes attacks (Red) to teach secure coding (Yellow).
Bridging the gap between Attackers and Builders.
"""

import os
import sys
import time
import json
import random
import signal
import secrets

# Add parent dir to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils

# --- VISUALS ---
C_ORANGE = "\033[33m"
C_RESET = "\033[0m"

class OrangeEducator:
    def __init__(self):
        self.running = True
        self.tracer = utils.TraceLogger(config.TRACE_LOG)
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        self.setup()

    def setup(self):
        print(f"{C_ORANGE}[SYSTEM] Orange Team (Educators) Initialized.{C_RESET}")

    def shutdown(self, signum, frame):
        print(f"\n{C_ORANGE}[SYSTEM] Orange Team workshop closed...{C_RESET}")
        self.running = False
        sys.exit(0)

    def analyze_attacks(self):
        """Read audit logs to find successful attacks."""
        if not os.path.exists(config.AUDIT_LOG): return

        attacks_detected = 0
        try:
            with open(config.AUDIT_LOG, 'r') as f:
                for line in f:
                    if "EXFILTRATION" in line or "RANSOMWARE" in line:
                        attacks_detected += 1
        except Exception as e:
            self.tracer.capture_exception(e, context="ORANGE_ANALYZE")

        if attacks_detected > 0:
            self.publish_standards(attacks_detected)

    def publish_standards(self, urgency_level):
        """Update coding standards based on attack intel."""
        standards = {
            "require_encryption": True,
            "input_validation": "STRICT",
            "urgency": urgency_level,
            "last_updated": time.time()
        }

        path = os.path.join(config.BASE_DIR, "intelligence", "coding_standards.json")
        try:
            utils.safe_file_write(path, json.dumps(standards, indent=4))
            # print(f"{C_ORANGE}[ORANGE] Updated Secure Coding Standards (Urgency: {urgency_level}){C_RESET}")
        except Exception as e:
            self.tracer.capture_exception(e, context="ORANGE_PUBLISH")

    def run_workshop(self):
        """
        Simulate a training session by analyzing audit logs and generating a report.
        Updates coding standards based on the threat landscape.
        """
        if not os.path.exists(config.AUDIT_LOG):
            return

        report_path = os.path.join(config.BASE_DIR, "intelligence", "workshop_report.txt")
        stats = {"RANSOMWARE": 0, "EXFILTRATION": 0, "C2_BEACON": 0, "TOTAL": 0}

        try:
            # Analyze logs for specific keywords
            with open(config.AUDIT_LOG, 'r') as f:
                for line in f:
                    stats["TOTAL"] += 1
                    if "RANSOMWARE" in line: stats["RANSOMWARE"] += 1
                    if "EXFILTRATION" in line: stats["EXFILTRATION"] += 1
                    if "C2_BEACON" in line: stats["C2_BEACON"] += 1

            # Generate Report
            with open(report_path, 'w') as f:
                f.write("=== ORANGE TEAM WORKSHOP REPORT ===\n")
                f.write(f"Generated: {time.ctime()}\n")
                f.write(f"Total Incidents Analyzed: {stats['TOTAL']}\n")
                f.write("-" * 30 + "\n")
                for k, v in stats.items():
                    if k != "TOTAL":
                        f.write(f"{k}: {v}\n")
                f.write("-" * 30 + "\n")

                recommendation = "STANDARD_PROCEDURE"
                if stats["RANSOMWARE"] > 5: recommendation = "ENABLE_OFFLINE_BACKUPS"
                if stats["EXFILTRATION"] > 5: recommendation = "STRICT_EGRESS_FILTERING"

                f.write(f"RECOMMENDATION: {recommendation}\n")

            # Update Standards based on findings
            urgency = 1
            if stats["RANSOMWARE"] > 3 or stats["EXFILTRATION"] > 3:
                urgency = 5
            elif stats["TOTAL"] > 20:
                urgency = 3

            self.publish_standards(urgency)
            # print(f"{C_ORANGE}[ORANGE] Workshop Complete. Report generated.{C_RESET}")

        except Exception as e:
            self.tracer.capture_exception(e, context="ORANGE_WORKSHOP")

    def run(self):
        while self.running:
            try:
                self.analyze_attacks()

                # Run workshop periodically (10% chance per tick)
                if secrets.choice([True] + [False]*9):
                    self.run_workshop()

                time.sleep(random.uniform(5.0, 10.0))
            except Exception as e:
                self.tracer.capture_exception(e, context="ORANGE_LOOP")
                time.sleep(1)

if __name__ == "__main__":
    bot = OrangeEducator()
    bot.run()
