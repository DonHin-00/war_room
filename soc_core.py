
import time
import os
import json
import utils
import config
import logging
from collections import deque

class SecurityOperationsCenter:
    """Centralized Intelligence & Command Unit."""
    def __init__(self):
        self.logger = utils.setup_logging("SOC", os.path.join(config.LOG_DIR, "soc.log"))
        self.blocklist_file = "global_blocklist.json"

        # SIEM State
        self.failed_auth_window = deque(maxlen=50) # Timestamps of failures
        self.attack_sources = {} # IP -> count
        self.incident_count = 0

        # Initialize blocklist
        utils.safe_json_write(self.blocklist_file, [])

    def analyze_log_line(self, line):
        try:
            # Parse unstructured logs if possible, or look for keywords
            if "CRITICAL" in line or "EXPLOIT SUCCESS" in line:
                self.trigger_incident("Confirmed Compromise", severity="CRITICAL")
            elif "BLOCKED" in line or "Forbidden" in line:
                self.track_failure()
            elif "http_req_" in line:
                # Extract IP if visible in filename (simulated log parsing)
                # Format: http_req_IP_ID.log
                parts = line.split('_')
                if len(parts) >= 3 and parts[1].replace('.', '').isdigit(): # Rough check
                    ip = parts[1]
                    self.track_source(ip)
        except: pass

    def track_failure(self):
        now = time.time()
        self.failed_auth_window.append(now)

        # Correlation: Brute Force Detection
        # If > 10 failures in 10 seconds
        if len(self.failed_auth_window) >= 10:
            if now - self.failed_auth_window[0] < 10.0:
                self.trigger_incident("Brute Force / Scan Campaign Detected", severity="HIGH")
                self.failed_auth_window.clear()

    def track_source(self, ip):
        self.attack_sources[ip] = self.attack_sources.get(ip, 0) + 1
        if self.attack_sources[ip] > 20: # Threshold
            self.ban_ip(ip)

    def ban_ip(self, ip):
        self.logger.warning(f"ISSUING GLOBAL BAN: {ip}")
        current_list = utils.safe_json_read(self.blocklist_file, [])
        if ip not in current_list:
            current_list.append(ip)
            utils.safe_json_write(self.blocklist_file, current_list)
            # Signal WAF (via shared file or DB)
            # WAF reads blocklist (we need to update WAF to do this, or WAF checks DB)

    def trigger_incident(self, name, severity="MEDIUM"):
        self.incident_count += 1
        self.logger.error(f"INCIDENT #{self.incident_count}: {name} [{severity}]")

        # Response Logic
        if severity == "CRITICAL":
            self.logger.critical("COMMAND: LOCKDOWN INITIATED. DEFCON 1.")
            utils.DB.set_state("blue_alert_level", 1) # 1 is Highest in Defcon (usually) or Max Alert?
            # In our sim, 5 is MAX ALERT (Red/Blue usage). Let's assume 5.
            utils.DB.set_state("blue_alert_level", 5)

        elif severity == "HIGH":
            current = utils.DB.get_state("blue_alert_level", 1)
            utils.DB.set_state("blue_alert_level", min(5, current + 1))

    def monitor(self):
        self.logger.info("SOC Online. Monitoring Audit Trail and Target Logs...")

        # Tail files
        files = {
            "audit": os.path.join(config.LOG_DIR, "../audit.jsonl"), # Assuming root
            "target": os.path.join(config.LOG_DIR, "target.log"),
            "waf": os.path.join(config.LOG_DIR, "waf.log")
        }

        file_handles = {}
        for k, v in files.items():
            if os.path.exists(v):
                f = open(v, 'r')
                f.seek(0, os.SEEK_END)
                file_handles[k] = f

        while True:
            for name, f in file_handles.items():
                line = f.readline()
                if line:
                    self.analyze_log_line(line.strip())
                else:
                    # Re-open if rotated/created
                    if not os.path.exists(files[name]): continue

            # Check for new files if not open
            for k, v in files.items():
                if k not in file_handles and os.path.exists(v):
                    file_handles[k] = open(v, 'r')

            utils.adaptive_sleep(0.5, 0.0)

if __name__ == "__main__":
    soc = SecurityOperationsCenter()
    soc.monitor()
