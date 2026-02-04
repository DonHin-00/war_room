#!/usr/bin/env python3
import re
import os
import argparse
import glob

def analyze_logs():
    log_files = glob.glob("logs/*.log")
    if not log_files:
        print("No logs found in logs/")
        return

    stats = {
        'blue_kills': 0,
        'red_impact': 0,
        'errors': 0
    }

    print(f"Analyzing {len(log_files)} log files...")

    for logfile in log_files:
        with open(logfile, 'r') as f:
            for line in f:
                if "Kill: " in line:
                    try:
                        kills = int(re.search(r'Kill: (\d+)', line).group(1))
                        stats['blue_kills'] += kills
                    except: pass

                if "Impact: " in line:
                    try:
                        impact = int(re.search(r'Impact: (\d+)', line).group(1))
                        stats['red_impact'] += impact
                    except: pass

                if "ERROR" in line:
                    stats['errors'] += 1

    print("\n--- Simulation Analysis ---")
    print(f"🛡️  Blue Team Kills: {stats['blue_kills']}")
    print(f"👹 Red Team Impact: {stats['red_impact']}")
    print(f"⚠️  Errors Detected: {stats['errors']}")

    score_diff = stats['blue_kills'] * 25 - stats['red_impact'] * 10
    print(f"\nNet Score (approx): {score_diff}")

    # Learning Analysis
    if stats['blue_kills'] + stats['red_impact'] > 0:
        ratio = stats['blue_kills'] / (stats['blue_kills'] + stats['red_impact'])
        print(f"Blue Defense Ratio: {ratio:.2f}")

    if stats['errors'] == 0:
        print("\n✅ System Stability: OPTIMAL")
    else:
        print("\n⚠️ System Stability: DEGRADED")

if __name__ == "__main__":
    analyze_logs()
