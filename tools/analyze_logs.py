#!/usr/bin/env python3
"""
Log Analyzer / Scraper
Scrapes logs and DB for stats, trends, and agent behavior analysis.
"""

import os
import sys
import json
import sqlite3
from collections import Counter

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
import utils

def analyze_audit_log():
    log_file = config.PATHS['AUDIT_LOG']
    if not os.path.exists(log_file):
        print("[ANALYZER] No audit log found.")
        return

    print(f"\n[ANALYZER] Scraping {log_file}...")

    stats = Counter()
    actor_stats = Counter()

    with open(log_file, 'r') as f:
        for line in f:
            try:
                event = json.loads(line)
                stats[event['action']] += 1
                actor_stats[event['actor']] += 1
            except: pass

    print("\n--- Event Distribution ---")
    for action, count in stats.most_common():
        print(f"  {action}: {count}")

    print("\n--- Actor Activity ---")
    for actor, count in actor_stats.most_common():
        print(f"  {actor}: {count}")

def analyze_db():
    print(f"\n[ANALYZER] Scraping SQLite DB ({config.PATHS['DB_PATH']})...")
    conn = utils.DB.get_connection()
    c = conn.cursor()

    # 1. Threat Intel
    c.execute("SELECT type, count(*) FROM threat_intel GROUP BY type")
    print("\n--- Threat Intel ---")
    for row in c.fetchall():
        print(f"  {row[0]}: {row[1]}")

    # 2. Q-Table Size
    c.execute("SELECT agent, count(*) FROM q_tables GROUP BY agent")
    print("\n--- Knowledge Base Size ---")
    for row in c.fetchall():
        print(f"  {row[0]}: {row[1]} states")

    conn.close()

if __name__ == "__main__":
    print("=== DEVIANCY SCRAPER & ANALYZER ===")
    analyze_audit_log()
    analyze_db()
