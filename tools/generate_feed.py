#!/usr/bin/env python3
"""
Threat Intelligence Feed Generator.
Analyses Audit Logs and generates IoCs (Indicators of Compromise).
Simulates a Purple Team / ISAC sharing capability.
"""

import os
import sys
import json
import time

# Add parent dir to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils

def generate_feed():
    print("[INTEL] Analyzing Audit Logs...")

    iocs = {
        "hashes": [],
        "filenames": [],
        "ips": ["127.0.0.1"] # Always local for this sim
    }

    if not os.path.exists(config.AUDIT_LOG):
        return

    with open(config.AUDIT_LOG, 'r') as f:
        for line in f:
            try:
                entry = json.loads(line)
                details = entry.get('details', '')

                # Extract filename from details
                if "generated for" in details:
                    path = details.split("generated for ")[-1]
                    filename = os.path.basename(path)
                    iocs["filenames"].append(filename)

                if "Encrypted" in details:
                    path = details.split("Encrypted ")[-1]
                    filename = os.path.basename(path)
                    iocs["filenames"].append(filename)

            except: pass

    # Deduplicate
    iocs["hashes"] = list(set(iocs["hashes"]))
    iocs["filenames"] = list(set(iocs["filenames"]))

    feed_path = os.path.join(config.BASE_DIR, "intelligence", "threat_feed.json")
    try:
        utils.safe_file_write(feed_path, json.dumps(iocs, indent=4))
        print(f"[INTEL] Threat Feed Updated: {len(iocs['filenames'])} indicators.")
    except: pass

if __name__ == "__main__":
    generate_feed()
