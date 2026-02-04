#!/usr/bin/env python3
"""
The Cleaner (Scraper).
Removes hidden junk, orphaned beacons, and stagnant simulation artifacts.
Can be run manually or invoked by Blue Team at MAX ALERT.
"""

import os
import sys
import shutil
import time

# Add parent dir to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def clean_junk():
    print("[CLEANER] Starting purge...")
    removed = 0

    if not os.path.exists(config.WAR_ZONE_DIR):
        print("War zone not found.")
        return

    for root, dirs, files in os.walk(config.WAR_ZONE_DIR):
        for f in files:
            path = os.path.join(root, f)

            # Logic for "Junk"
            is_hidden = f.startswith(".sys_")
            is_orphan_beacon = f.endswith(".c2_beacon")
            is_dead_ransom = f.endswith(".enc") and not os.path.exists(path.replace(".enc", ""))

            if is_hidden or is_orphan_beacon or is_dead_ransom:
                try:
                    os.remove(path)
                    print(f"[CLEANER] Removed: {f}")
                    removed += 1
                except OSError as e:
                    print(f"Error removing {f}: {e}")

        # Remove empty directories (except critical)
        for d in dirs:
            dir_path = os.path.join(root, d)
            if d == "critical": continue
            try:
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    print(f"[CLEANER] Removed empty dir: {d}")
            except OSError: pass

    print(f"[CLEANER] Purge complete. Removed {removed} artifacts.")

if __name__ == "__main__":
    clean_junk()
