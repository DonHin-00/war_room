import json
import time
import os
import logging

SIEM_LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs/siem.json")

class SIEM:
    def __init__(self):
        self.log_file = SIEM_LOG_FILE
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

    def log_event(self, source, event_type, details, severity="INFO"):
        event = {
            "timestamp": time.time(),
            "source": source,
            "type": event_type,
            "severity": severity,
            "details": details
        }
        try:
            with open(self.log_file, "a") as f:
                json.dump(event, f)
                f.write("\n")
        except Exception as e:
            print(f"SIEM ERROR: {e}")

        # Color coding for terminal output
        colors = {
            "INFO": "\033[94m",
            "WARNING": "\033[93m",
            "CRITICAL": "\033[91m",
            "HIGH": "\033[91m"
        }
        reset = "\033[0m"
        color = colors.get(severity, reset)
        print(f"{color}[SIEM] {severity} | {source} | {event_type} | {details}{reset}")

siem_logger = SIEM()
