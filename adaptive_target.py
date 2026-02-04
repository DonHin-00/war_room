
import time
import os
import re
import utils
import config
import logging
import random

class AdaptiveTarget:
    """An intelligent target that patches itself and attempts to heal."""
    def __init__(self):
        self.logger = utils.setup_logging("TARGET_AI", os.path.join(config.LOG_DIR, "target.log"))
        self.watch_dir = config.TARGET_DIR
        self.compromised = False
        self.defense_level = 1
        self.lockdown_mode = False

        # HIDS Baseline (Simulated)
        self.critical_files = {"/etc/passwd": "root:x:0:0:...", "/var/www/index.html": "<html>"}
        self.file_hashes = {k: utils.calculate_sha256(k) for k in self.critical_files} # Mock

        # Initial Vulnerabilities
        self.vulns = [
            (r"(?i)(SELECT|UNION|INSERT|UPDATE).*", "SQLi", self.leak_database),
            (r"(?i)(/bin/sh|nc -e|wget)", "RCE", self.spawn_shell),
            (r"(?i)(<script>|javascript:)", "XSS", self.log_xss),
        ]

        # Dynamic Blocklist (The "Learning" part)
        self.patched_patterns = []

    def leak_database(self):
        self.logger.critical("CRITICAL: Database Leaked!")
        utils.safe_file_write(os.path.join(self.watch_dir, "leaked_database.csv"), "user,pass\nadmin,12345\n")
        self.compromised = True
        return True

    def spawn_shell(self):
        self.logger.critical("CRITICAL: Reverse Shell Established!")
        utils.safe_file_write(os.path.join(self.watch_dir, "backdoor.sh"), "#!/bin/bash\n# HAHA")
        self.compromised = True
        return True

    def log_xss(self):
        self.logger.warning("ALERT: XSS Triggered.")
        return True

    def patch_vulnerability(self, attack_string):
        """Simple AI: Create a regex to block this specific payload structure."""
        # In a real AI, this would be complex. Here, we block the main keywords found.
        if "UNION" in attack_string:
            self.patched_patterns.append(r"UNION")
            self.logger.info("PATCH APPLIED: Blocking 'UNION' keyword.")
        elif "SELECT" in attack_string:
            self.patched_patterns.append(r"SELECT")
            self.logger.info("PATCH APPLIED: Blocking 'SELECT' keyword.")
        elif "script" in attack_string:
            self.patched_patterns.append(r"script")
            self.logger.info("PATCH APPLIED: Blocking 'script' tag.")

        self.defense_level += 1

    def self_heal(self):
        """Remove known artifacts."""
        try:
            for f in ["backdoor.sh", "leaked_database.csv"]:
                path = os.path.join(self.watch_dir, f)
                if os.path.exists(path):
                    utils.secure_delete(path)
                    self.logger.info(f"SELF-HEALING: Removed {f}")
        except: pass

    def handle_request(self, filepath):
        try:
            # HIDS Check (Periodic)
            if random.random() < 0.05: self.run_hids()

            # Lockdown Check
            if self.lockdown_mode:
                utils.secure_delete(filepath)
                return

            content = utils.safe_file_read(filepath)
            if not content: return

            filename = os.path.basename(filepath)
            req_id = filename.split('_')[-1].replace('.log', '')

            # 1. Check Dynamic Blocklist (Patches)
            blocked = False
            for pattern in self.patched_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    self.logger.info(f"BLOCKED: Attack matched patch '{pattern}'")
                    # Respond 403
                    utils.safe_file_write(os.path.join(self.watch_dir, f"http_resp_{req_id}_403.log"), "Forbidden")
                    blocked = True
                    break

            if blocked:
                utils.secure_delete(filepath)
                return

            # 2. Check Vulnerabilities
            attack_detected = False
            for pattern, name, effect in self.vulns:
                if re.search(pattern, content):
                    self.logger.error(f"EXPLOIT SUCCESS: {name}")
                    if effect(): # Run the effect (leak DB etc)
                        # Respond 200 (Success for Attacker)
                        utils.safe_file_write(os.path.join(self.watch_dir, f"http_resp_{req_id}_200.log"), "OK")

                        # Trigger Adaptation
                        self.patch_vulnerability(content)
                        attack_detected = True
                        break

            if not attack_detected:
                # Normal Traffic
                utils.safe_file_write(os.path.join(self.watch_dir, f"http_resp_{req_id}_200.log"), "OK")

            # Cleanup request
            utils.secure_delete(filepath)

        except Exception as e:
            self.logger.error(f"Error: {e}")

    def run(self):
        self.logger.info("Adaptive Target Online. AI Defense System Active.")
        while True:
            # Heal periodically
            if random.random() < 0.1:
                self.self_heal()

            try:
                # Process requests
                now = time.time()
                with os.scandir(self.watch_dir) as entries:
                    for entry in entries:
                        if entry.is_file() and entry.name.startswith("http_req_"):
                            if entry.stat().st_mtime < now - 1.0:
                                self.handle_request(entry.path)
            except OSError: pass

            utils.adaptive_sleep(1.0, 0.0)

    def run_hids(self):
        """Simulated Host Intrusion Detection System."""
        # Check for unexpected files in root (simulated) or modifications
        # Here we verify if we are in DEFCON 1 (Lockdown) via DB
        state = utils.DB.get_state("blue_alert_level", 1)
        if state >= 5 and not self.lockdown_mode:
            self.lockdown_mode = True
            self.logger.warning("HIDS: ENTERING LOCKDOWN MODE (DEFCON 5 detected).")
        elif state < 5 and self.lockdown_mode:
            self.lockdown_mode = False
            self.logger.info("HIDS: Lockdown lifted.")

if __name__ == "__main__":
    target = AdaptiveTarget()
    target.run()
