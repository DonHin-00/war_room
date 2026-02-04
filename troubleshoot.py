#!/usr/bin/env python3
"""
Troubleshoot & Diagnostics Tool for AI Cyber War Simulation
Scans war zones for errors, crashes, and health metrics.
"""

import os
import glob
import json
import re

def analyze_log(filepath):
    """Scan a log file for errors and return a list of issues."""
    issues = []
    if not os.path.exists(filepath):
        return ["Log file not found."]

    with open(filepath, 'r', errors='ignore') as f:
        for i, line in enumerate(f, 1):
            if "Traceback" in line:
                issues.append(f"Line {i}: Traceback detected")
            if "Error" in line or "Exception" in line:
                # Ignore common "expected" errors if any, but report others
                issues.append(f"Line {i}: {line.strip()}")
            if "died" in line:
                issues.append(f"Line {i}: Process died detected")

    return issues

def check_json_health(filepath):
    """Check if a JSON file is valid and not empty."""
    if not os.path.exists(filepath):
        return "File missing"
    try:
        if os.path.getsize(filepath) == 0:
            return "File empty"
        with open(filepath, 'r') as f:
            json.load(f)
        return "OK"
    except json.JSONDecodeError:
        return "Corrupted JSON"

def main():
    print("🔍 Starting Diagnostics Scan...")

    # Find all war zones
    war_zones = glob.glob("war_zone_*")
    if not war_zones:
        print("❌ No war zones found.")
        return

    for zone in sorted(war_zones):
        print(f"\n📂 Scanning {zone}...")

        # 1. Check Log Files
        logs = ["war_room.log", "blue_stdout.log", "red_stdout.log"]
        has_errors = False

        for log in logs:
            path = os.path.join(zone, log)
            issues = analyze_log(path)
            if issues:
                has_errors = True
                print(f"  ❌ Issues in {log}:")
                for issue in issues[:5]: # Show max 5 errors
                    print(f"    - {issue}")
                if len(issues) > 5:
                    print(f"    ... and {len(issues)-5} more.")
            else:
                # print(f"  ✅ {log} is clean.")
                pass

        if not has_errors:
            print("  ✅ Logs look clean.")

        # 2. Check State Files
        files = {
            "State": "war_state.json",
            "Blue Q": "blue_q_table.json",
            "Red Q": "red_q_table.json"
        }

        for name, fname in files.items():
            path = os.path.join(zone, fname)
            status = check_json_health(path)
            if status != "OK":
                print(f"  ⚠️ {name} issue: {status}")
            else:
                # print(f"  ✅ {name} is healthy.")
                pass

if __name__ == "__main__":
    main()
