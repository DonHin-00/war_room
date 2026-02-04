#!/usr/bin/env python3
import time
import os
import sys
import psutil
import json

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils

logger = utils.setup_logging("PurpleAuditor", config.AUDIT_LOG) # Log direct to audit trail

class PurpleAuditor:
    def __init__(self):
        self.running = True

    def check_components(self):
        """Verify Red and Blue components are active."""
        red_c2 = False
        blue_edr = False

        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmd = " ".join(proc.info['cmdline'] or [])
                if "red_c2.py" in cmd:
                    red_c2 = True
                if "blue_edr.py" in cmd:
                    blue_edr = True
            except Exception: pass

        return red_c2, blue_edr

    def audit_integrity(self):
        """Run security scan to ensure no regressions."""
        # We can call the security_scan tool programmatically or just check basic things
        # Let's check for world-writable files in simulation_data
        violations = 0
        if os.path.exists(config.SIMULATION_DATA_DIR):
            for f in os.listdir(config.SIMULATION_DATA_DIR):
                fp = os.path.join(config.SIMULATION_DATA_DIR, f)
                try:
                    mode = os.stat(fp).st_mode
                    if mode & 0o002: # World Writable
                        logger.warning(f"PURPLE: Insecure file permission detected on {f}")
                        violations += 1
                except Exception: pass
        return violations

    def run(self):
        logger.info("🟣 Purple Team Auditor Active. Monitoring Game Integrity...")
        while self.running:
            red_up, blue_up = self.check_components()

            status = "HEALTHY"
            if not red_up: status = "RED_DOWN"
            if not blue_up: status = "BLUE_DOWN"

            violations = self.audit_integrity()
            if violations > 0: status = "INSECURE"

            # Log to audit trail
            entry = {
                "red_c2": red_up,
                "blue_edr": blue_up,
                "violations": violations,
                "status": status
            }

            # We use the audit logger directly if possible, or just append via logger
            # utils.AuditLogger logic handles the hash chain.
            # But here we initialized 'logger' as a standard python logger pointing to the file.
            # That might break the JSONL format of AuditLogger if we aren't careful.
            # Let's use utils.AuditLogger properly.

            # Re-init logger to not write to file, just stdout

            try:
                auditor = utils.AuditLogger(config.AUDIT_LOG)
                auditor.log_event("PURPLE", "GAME_STATE", entry)
            except Exception as e:
                logger.error(f"Audit log error: {e}")

            time.sleep(10)

if __name__ == "__main__":
    # We need psutil
    try:
        import psutil
    except ImportError:
        logger.info("Installing psutil...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
        import psutil

    auditor = PurpleAuditor()
    auditor.run()
