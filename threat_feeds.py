
import json
import os
import time
import urllib.request
import utils
import logging
import csv
import io
import re
import config

class FeedFetcher:
    """Robust feed fetcher with retry logic and user-agent rotation."""
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
            'Mozilla/5.0 (X11; Linux x86_64)'
        ]

    def fetch(self, url, retries=3):
        for i in range(retries):
            try:
                # Random UA
                ua = self.user_agents[i % len(self.user_agents)]
                req = urllib.request.Request(
                    url,
                    headers={'User-Agent': ua}
                )
                print(f"Fetching {url} (Attempt {i+1})...")
                with urllib.request.urlopen(req, timeout=15) as response:
                    return response.read().decode('utf-8', errors='ignore')
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                time.sleep(1 * (i + 1)) # Backoff
        return None

class ThreatAggregator:
    def __init__(self, db_path="threat_db.json"):
        self.db_path = db_path
        self.feeds = config.threat_feeds
        self.fetcher = FeedFetcher()
        self.stats = {
            "total_rows": 0,
            "valid_rows": 0,
            "invalid_rows": 0,
            "duplicates": 0,
            "by_source": {}
        }
        self.data = {
            "hashes": set(),
            "filenames": set(),
            "last_updated": 0,
            "metadata": {} # source tracking
        }

    def validate(self, value, pattern):
        if not pattern or not value: return True
        return re.match(pattern, value) is not None

    def sanitize_filename(self, filename):
        if not filename or filename == 'unknown': return None
        # Remove paths
        fname = os.path.basename(filename)
        # Remove common placeholder names
        if fname.lower() in ['unknown', 'file', 'sample', 'none', '-']: return None
        return fname

    def process_feed(self, feed_config):
        content = self.fetcher.fetch(feed_config['url'])
        if not content:
            print(f"FAILED to fetch {feed_config['name']}")
            return

        source_name = feed_config['name']
        self.stats["by_source"][source_name] = {"valid": 0, "invalid": 0}

        # Determine format handling
        lines = content.splitlines()
        if feed_config.get('format') == 'abuse_ch':
            lines = [l for l in lines if not l.startswith('#')]

        reader = csv.reader(lines)
        cols = feed_config['columns']
        validations = feed_config.get('validation', {})

        for row in reader:
            self.stats["total_rows"] += 1
            if not row: continue

            try:
                # 1. Process Hash
                if 'hash_sha256' in cols and len(row) > cols['hash_sha256']:
                    val = row[cols['hash_sha256']].strip()
                    if self.validate(val, validations.get('hash_sha256')):
                        if val not in self.data['hashes']:
                            self.data['hashes'].add(val)
                            self.stats["valid_rows"] += 1
                            self.stats["by_source"][source_name]["valid"] += 1
                        else:
                            self.stats["duplicates"] += 1
                    else:
                        self.stats["invalid_rows"] += 1
                        self.stats["by_source"][source_name]["invalid"] += 1

                # 2. Process Filename
                if 'filename' in cols and len(row) > cols['filename']:
                    raw_name = row[cols['filename']].strip()
                    name = self.sanitize_filename(raw_name)

                    if name and self.validate(name, validations.get('filename')):
                        if name not in self.data['filenames']:
                            self.data['filenames'].add(name)
            except IndexError:
                pass

        print(f"Processed {source_name}: {self.stats['by_source'][source_name]}")

    def update(self):
        print("Starting OCD Threat Aggregation...")
        start_time = time.time()

        for feed in self.feeds:
            self.process_feed(feed)

        self.data["last_updated"] = time.time()
        self.save()

        duration = time.time() - start_time
        print("\n--- Aggregation Report ---")
        print(f"Time Taken: {duration:.2f}s")
        print(f"Total Processed Rows: {self.stats['total_rows']}")
        print(f"Valid IOCs: {self.stats['valid_rows']}")
        print(f"Invalid/Skipped: {self.stats['invalid_rows']}")
        print(f"Duplicates: {self.stats['duplicates']}")
        print(f"Unique Hashes: {len(self.data['hashes'])}")
        print(f"Unique Filenames: {len(self.data['filenames'])}")
        print("--------------------------\n")

    def save(self):
        # Convert sets to lists for JSON
        output = {
            "hashes": list(self.data["hashes"]),
            "filenames": list(self.data["filenames"]),
            "last_updated": self.data["last_updated"],
            "stats": self.stats
        }
        utils.safe_json_write(self.db_path, output)

if __name__ == "__main__":
    aggregator = ThreatAggregator()
    aggregator.update()
