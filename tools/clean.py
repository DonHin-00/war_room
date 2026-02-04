#!/usr/bin/env python3
"""
Deviancy Cleaner
Scrapes the environment for deviant artifacts (RoE violations, garbage) and sanitizes them.
"""

import os
import sys
import time
import shutil

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
import utils

def clean_battlefield():
    print("[CLEAN] Scanning Battlefield for artifacts...")
    battlefield = config.PATHS['BATTLEFIELD']

    if not os.path.exists(battlefield):
        return

    removed = 0
    for f in os.listdir(battlefield):
        path = os.path.join(battlefield, f)

        # Criteria for deviancy:
        # 1. Too old (> 1 hour) - Stale war artifacts
        # 2. Too big (> 1MB) - Resource exhaustion attempts
        # 3. Weird names (not matching standard patterns)

        try:
            stats = os.stat(path)
            age = time.time() - stats.st_mtime
            size = stats.st_size

            is_deviant = False
            reason = ""

            if age > 3600:
                is_deviant = True
                reason = "STALE"
            elif size > 1024 * 1024:
                is_deviant = True
                reason = "OVERSIZE"
            elif not (f.startswith("malware_") or f.startswith(".sys_")):
                # Check config for allowed patterns? For now, strict mode.
                # Allow '.enc'
                if not f.endswith(".enc"):
                    is_deviant = True
                    reason = "UNKNOWN_ARTIFACT"

            if is_deviant:
                print(f"  - Removing {f} [{reason}]")
                os.remove(path)
                removed += 1

        except Exception as e:
            print(f"  ! Error checking {f}: {e}")

    print(f"[CLEAN] Removed {removed} deviant artifacts.")

def clean_logs():
    print("[CLEAN] Archiving old audit logs...")
    log_file = config.PATHS['AUDIT_LOG']
    if os.path.exists(log_file):
        # Rotate if > 5MB
        if os.path.getsize(log_file) > 5 * 1024 * 1024:
            timestamp = int(time.time())
            archive = f"{log_file}.{timestamp}.bak"
            shutil.move(log_file, archive)
            print(f"  - Rotated {log_file} -> {archive}")
            # Re-create empty
            open(log_file, 'w').close()

def main():
    print("=== DEVIANCY CLEANER ===")
    clean_battlefield()
    clean_logs()
    print("[SUCCESS] Environment sanitized.")

if __name__ == "__main__":
    main()
