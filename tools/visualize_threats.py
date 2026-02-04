#!/usr/bin/env python3
import json
import os
import sys
import collections

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def visualize():
    log_file = config.AUDIT_LOG
    if not os.path.exists(log_file):
        print("No audit log found.")
        return

    events = []
    with open(log_file, 'r') as f:
        for line in f:
            try:
                events.append(json.loads(line))
            except: pass

    if not events:
        print("No events found.")
        return

    print("\n=== 📊 THREAT INTELLIGENCE HEATMAP ===\n")

    # 1. Event Types Histogram
    event_counts = collections.Counter([e['event'] for e in events if e['event'] != "GENESIS"])
    max_count = max(event_counts.values()) if event_counts else 1

    print("Attack Vectors & Responses:")
    for event, count in event_counts.most_common():
        bar = "█" * int((count / max_count) * 40)
        print(f"{event:<25} | {bar} ({count})")

    # 2. Agent Activity
    agent_counts = collections.Counter([e['agent'] for e in events if e['agent'] != "SYSTEM"])
    print("\nAgent Activity:")
    total = sum(agent_counts.values())
    if total > 0:
        red_pct = agent_counts['RED'] / total * 100
        blue_pct = agent_counts['BLUE'] / total * 100
        print(f"RED:  {'#' * int(red_pct/2)} {red_pct:.1f}%")
        print(f"BLUE: {'=' * int(blue_pct/2)} {blue_pct:.1f}%")

    print("\n======================================\n")

if __name__ == "__main__":
    visualize()
