#!/usr/bin/env python3
"""
Watchdog / SIEM Tool
Monitors the Audit Log for anomalies and high-frequency attacks.
"""

import os
import sys
import time
import json
from collections import deque

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
import utils

C_RED = "\033[91m"
C_YELLOW = "\033[93m"
C_RESET = "\033[0m"

class Watchdog:
    def __init__(self):
        self.log_file = config.PATHS['AUDIT_LOG']
        self.events = deque(maxlen=100) # Keep last 100 events

    def tail_log(self):
        print(f"[WATCHDOG] Monitoring {self.log_file}...")
        try:
            with open(self.log_file, 'r') as f:
                # Seek to end
                f.seek(0, os.SEEK_END)

                while True:
                    line = f.readline()
                    if not line:
                        time.sleep(0.1)
                        continue

                    try:
                        event = json.loads(line)
                        self.analyze_event(event)
                    except json.JSONDecodeError:
                        pass
        except FileNotFoundError:
            print("[WATCHDOG] Log file not found. Waiting...")
            time.sleep(2)
            self.tail_log()

    def analyze_event(self, event):
        timestamp = event.get('timestamp')
        actor = event.get('actor')
        action = event.get('action')

        self.events.append(event)

        # Simple Rule: Frequency Analysis
        # Count events in the last 1 second
        recent = [e for e in self.events if e['timestamp'] > time.time() - 1.0]

        if len(recent) > 5:
            print(f"{C_RED}[ALERT] High Traffic Detected! ({len(recent)} events/sec){C_RESET}")

        # Simple Rule: Ransomware Detection
        if action == "ATTACK_RANSOMWARE":
             print(f"{C_YELLOW}[ALERT] Ransomware Activity Detected: {event['target']}{C_RESET}")

        # Log output
        print(f"[{time.strftime('%H:%M:%S')}] {actor} -> {action}")

if __name__ == "__main__":
    dog = Watchdog()
    dog.tail_log()
