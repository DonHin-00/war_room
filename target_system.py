
import time
import os
import re
import utils
import config
import logging

class VulnerableServer:
    """A simulated target that reacts to successful attacks."""
    def __init__(self):
        self.logger = utils.setup_logging("TARGET", os.path.join(config.LOG_DIR, "target.log"))
        self.watch_dir = config.TARGET_DIR
        self.compromised = False

        # Attack signatures (Target's vulnerabilities)
        self.vulns = [
            (r"(?i)(SELECT|UNION|INSERT|UPDATE).*", "SQLi", self.leak_database),
            (r"(?i)(/bin/sh|nc -e|wget)", "RCE", self.spawn_shell),
            (r"(?i)(<script>|javascript:)", "XSS", self.log_xss),
        ]

    def leak_database(self):
        self.logger.critical("CRITICAL: Database Leaked via SQL Injection!")
        utils.safe_file_write(os.path.join(self.watch_dir, "leaked_database.csv"), "user,pass\nadmin,12345\n")
        self.compromised = True

    def spawn_shell(self):
        self.logger.critical("CRITICAL: Reverse Shell Established via RCE!")
        utils.safe_file_write(os.path.join(self.watch_dir, "backdoor.sh"), "#!/bin/bash\n# HAHA")
        self.compromised = True

    def log_xss(self):
        self.logger.warning("ALERT: User session hijacked via XSS.")

    def process_traffic(self):
        # Scan for request logs
        try:
            # We look for files older than 2 seconds (giving Blue time to block)
            now = time.time()
            with os.scandir(self.watch_dir) as entries:
                for entry in entries:
                    if entry.is_file() and entry.name.startswith("http_req_"):
                        # Check age
                        if entry.stat().st_mtime < now - 2.0:
                            self.handle_request(entry.path)
        except OSError: pass

    def handle_request(self, filepath):
        try:
            content = utils.safe_file_read(filepath)
            if not content: return

            self.logger.info(f"Processing request: {os.path.basename(filepath)}")

            attack_detected = False
            for pattern, name, effect in self.vulns:
                if re.search(pattern, content):
                    self.logger.error(f"VULNERABILITY EXPLOITED: {name}")
                    effect()
                    attack_detected = True
                    break

            if not attack_detected:
                self.logger.info("Request processed normally (200 OK).")

            # Consume the request (Simulate processing complete)
            utils.secure_delete(filepath)

        except Exception as e:
            self.logger.error(f"Error processing request: {e}")

    def run(self):
        self.logger.info("Target Server Online. Monitoring traffic...")
        while True:
            self.process_traffic()
            utils.adaptive_sleep(1.0, 0.0) # Slow poll

if __name__ == "__main__":
    server = VulnerableServer()
    server.run()
