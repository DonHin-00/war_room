#!/usr/bin/env python3
"""
Lab Export (Real Hash Replay)
Extracts REAL malware hashes from Threat Intel feeds and generates
correlated artifact signatures for SIEM ingestion.
"""

import json
import time
import os
import sqlite3
import random
import config
from db_manager import DatabaseManager

class HashReplayEngine:
    def __init__(self):
        self.db = DatabaseManager()
        self.export_file = "real_hash_export.json"

    def fetch_real_hashes(self, limit=1000):
        """
        Fetches ACTUAL hashes collected from MalwareBazaar/ThreatFox/URLHaus
        via the ThreatIntel module's database.
        """
        conn = sqlite3.connect(config.DB_PATH) # Access the DB populated by threat_intel.py
        cursor = conn.cursor()

        # We look for IOCs that look like SHA256 (64 hex chars)
        # The threat_intel module dumps everything into 'threat_intel' table.
        # We filter for likely hashes.
        query = '''
            SELECT ioc, source FROM threat_intel
            WHERE length(ioc) = 64
            AND ioc GLOB '[0-9a-f]*'
            ORDER BY last_seen DESC
            LIMIT ?
        '''

        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        conn.close()

        return rows

    def generate_artifacts(self):
        print("[HashReplay] connecting to Threat Intelligence DB...")
        real_samples = self.fetch_real_hashes()

        if not real_samples:
            print("[HashReplay] No hashes found in DB. Ensure threat_intel.py has run.")
            return

        export_data = {
            "timestamp": time.time(),
            "source": "Real_World_Feeds",
            "type": "Malware_Hash_Replay",
            "count": len(real_samples),
            "samples": []
        }

        print(f"[HashReplay] Processing {len(real_samples)} REAL malware hashes...")

        for ioc, source in real_samples:
            # Simulate a "file object" for the SIEM
            sample_entry = {
                "sha256": ioc,
                "classification": "Malware",
                "feed_source": source,
                "file_name": f"sample_{ioc[:8]}.bin",
                "status": "Active"
            }
            export_data["samples"].append(sample_entry)

        # Write to export
        with open(self.export_file, "w") as f:
            json.dump(export_data, f, indent=4)

        print(f"[HashReplay] Exported {len(real_samples)} real hashes to {self.export_file}")

if __name__ == "__main__":
    replay = HashReplayEngine()
    replay.generate_artifacts()
