
import json
import os
import time
import urllib.request
import utils
import logging
import csv
import io
import config

class ThreatAggregator:
    def __init__(self, db_path="threat_db.json"):
        self.db_path = db_path
        self.feeds = config.threat_feeds
        self.data = {
            "hashes": set(),
            "filenames": set(),
            "last_updated": 0
        }

    def fetch_feed(self, feed):
        print(f"Fetching {feed['name']}...")
        try:
            req = urllib.request.Request(
                feed['url'],
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read().decode('utf-8', errors='ignore')
                return content
        except Exception as e:
            print(f"Failed to fetch {feed['name']}: {e}")
            return None

    def parse_csv(self, content, columns):
        count = 0
        # Use csv module for robust parsing
        # Skip comment lines for abuse.ch formats
        lines = [line for line in content.splitlines() if not line.startswith('#')]
        reader = csv.reader(lines)

        for parts in reader:
            if not parts: continue

            # Extract Hash
            if "hash" in columns and len(parts) > columns["hash"]:
                val = parts[columns["hash"]]
                if len(val) == 64: # SHA256
                    self.data["hashes"].add(val)
                    count += 1

            # Extract Filename
            if "filename" in columns and len(parts) > columns["filename"]:
                val = parts[columns["filename"]]
                if val and val != "unknown":
                    self.data["filenames"].add(val)

        print(f"Parsed {count} items.")

    def update(self):
        for feed in self.feeds:
            content = self.fetch_feed(feed)
            if content:
                if feed['type'] == 'csv':
                    self.parse_csv(content, feed['columns'])

        self.data["last_updated"] = time.time()
        self.save()
        print(f"Threat DB Updated: {len(self.data['hashes'])} hashes, {len(self.data['filenames'])} filenames.")

    def save(self):
        # Convert sets to lists for JSON
        output = {
            "hashes": list(self.data["hashes"]),
            "filenames": list(self.data["filenames"]),
            "last_updated": self.data["last_updated"]
        }
        utils.safe_json_write(self.db_path, output)

if __name__ == "__main__":
    aggregator = ThreatAggregator()
    aggregator.update()
