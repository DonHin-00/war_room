import json
import collections
import sys
import os
from tabulate import tabulate

def analyze_audit_log(filepath="audit_log.jsonl"):
    if not os.path.exists(filepath):
        print(f"No audit log found at {filepath}")
        return

    agent_counts = collections.Counter()
    event_counts = collections.defaultdict(collections.Counter)

    print(f"--- Analyzing {filepath} ---")

    try:
        with open(filepath, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    agent = entry.get('agent', 'unknown')
                    event = entry.get('event', 'unknown')

                    agent_counts[agent] += 1
                    event_counts[agent][event] += 1
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"Error reading log: {e}")
        return

    # Print Summary Table
    data = []
    for agent, total in agent_counts.most_common():
        events = event_counts[agent]
        top_event = events.most_common(1)[0] if events else ("None", 0)
        data.append([agent, total, f"{top_event[0]} ({top_event[1]})"])

    print(tabulate(data, headers=["Agent", "Total Actions", "Top Action"], tablefmt="grid"))

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "audit_log.jsonl"
    analyze_audit_log(path)
