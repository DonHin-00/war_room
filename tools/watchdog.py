#!/usr/bin/env python3
import time
import json
import os
import sys

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils

class Watchdog:
    def __init__(self):
        self.log_file = config.AUDIT_LOG
        self.last_pos = 0
        self.events_window = []
        self.WINDOW_SIZE = 5 # seconds
        self.THRESHOLD_EVENTS = 10 # events per window

    def monitor(self):
        print(f"🛡️ Sentinel Watchdog Active. Monitoring {self.log_file}...")

        # Initial seek to end
        if os.path.exists(self.log_file):
            self.last_pos = os.path.getsize(self.log_file)

        while True:
            try:
                if os.path.exists(self.log_file):
                    with open(self.log_file, 'r') as f:
                        f.seek(self.last_pos)
                        new_lines = f.readlines()
                        self.last_pos = f.tell()

                        for line in new_lines:
                            self.process_line(line)

                self.cleanup_window()
                time.sleep(1)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Watchdog Error: {e}")
                time.sleep(1)

    def process_line(self, line):
        try:
            entry = json.loads(line)
            ts = entry.get('timestamp', time.time())
            event = entry.get('event', 'UNKNOWN')
            agent = entry.get('agent', 'UNKNOWN')

            # Print Alert
            if "TRAP_TRIGGERED" in event:
                print(f"🚨 ALERT: {agent} triggered a HONEYPOT! [Active Defense]")

            if "RANSOMWARE" in event:
                print(f"⚠️  ALERT: Ransomware Activity Detected! Action: {event}")

            # Rate Limiting / DoS Detection
            self.events_window.append(ts)
            recent_events = [t for t in self.events_window if t > time.time() - self.WINDOW_SIZE]

            if len(recent_events) > self.THRESHOLD_EVENTS:
                print(f"⛔ CRITICAL: High Activity Detected ({len(recent_events)} events/5s). Possible DoS or Fuzzing!")
                # In a real system, we would ban the IP here.
                # For simulation, we just scream.

        except json.JSONDecodeError:
            pass

    def cleanup_window(self):
        self.events_window = [t for t in self.events_window if t > time.time() - self.WINDOW_SIZE]

class NetworkIDS:
    """Traffic Analysis for Command Flooding."""
    def __init__(self):
        self.packet_count = 0
        self.start_time = time.time()

    def sniff(self):
        # Simulating Multicast Sniffing
        # In reality, we'd join the group.
        # Here we check the network_bus directory or logs for 'Broadcast'
        pass

    def analyze_traffic(self):
        # Scan log for broadcast rate
        try:
            with open(config.RED_LOG, 'r') as f:
                lines = f.readlines()
                # Count recent broadcasts
                now = time.time()
                recent = [l for l in lines[-50:] if "Broadcast" in l]
                if len(recent) > 20:
                    print(f"🚨 NIDS ALERT: Beacon Storm Detected ({len(recent)}/50 events)")
                    utils.broadcast_alert("NIDS: BEACON STORM DETECTED")
        except: pass

if __name__ == "__main__":
    utils.check_root()
    w = Watchdog()
    nids = NetworkIDS()

    # Run together
    import threading
    t = threading.Thread(target=w.monitor)
    t.start()

    while True:
        nids.analyze_traffic()
        time.sleep(5)
