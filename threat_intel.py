#!/usr/bin/env python3
"""
Threat Intelligence Module
Fetches and manages real-world threat data from Abuse.ch
"""

import json
import os
import time
import urllib.request
import urllib.error
import random
import logging

try:
    import config
except ImportError:
    # Fallback if config is not in python path
    class Config:
        THREAT_FEED_URL_IPS = "https://feodotracker.abuse.ch/downloads/ipblocklist.json"
        THREAT_FEED_CACHE = "threat_feed_cache.json"
    config = Config()

class ThreatIntel:
    def __init__(self, cache_file=None):
        self.cache_file = cache_file or config.THREAT_FEED_CACHE
        self.ips = set()
        self.raw_data = []
        self.last_updated = 0
        self.load_cache()

    def load_cache(self):
        """Loads threat data from local cache if available."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    self.ips = set(data.get('ips', []))
                    self.last_updated = data.get('last_updated', 0)
                    self.raw_data = data.get('raw_data', [])
                print(f"[ThreatIntel] Loaded {len(self.ips)} IOCs from cache.")
            except Exception as e:
                print(f"[ThreatIntel] Cache load failed: {e}")

    def save_cache(self):
        """Saves current threat data to local cache."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump({
                    'ips': list(self.ips),
                    'last_updated': self.last_updated,
                    'raw_data': self.raw_data
                }, f)
        except Exception as e:
            print(f"[ThreatIntel] Cache save failed: {e}")

    def fetch_feed(self, force=False):
        """Fetches the latest threat feed from Feodo Tracker."""
        # Update if cache is older than 24 hours or forced
        if not force and (time.time() - self.last_updated < 86400) and self.ips:
            return

        print(f"[ThreatIntel] Fetching fresh threat feed from {config.THREAT_FEED_URL_IPS}...")
        try:
            req = urllib.request.Request(
                config.THREAT_FEED_URL_IPS,
                headers={'User-Agent': 'WarRoom-Simulation/1.0'}
            )
            with urllib.request.urlopen(req) as response:
                content = response.read().decode('utf-8')
                if not content:
                    print("[ThreatIntel] Empty response from feed.")
                    return

                try:
                    data = json.loads(content)
                except json.JSONDecodeError:
                    # Try line-by-line if JSON fails (some feeds are JSONL or CSV)
                    print("[ThreatIntel] JSON decode failed, checking if raw text...")
                    return

                new_ips = set()
                # Parse Feodo Tracker JSON format
                # Expecting list of dicts with 'ip_address' or similar

                self.raw_data = data # Store raw for metadata if needed

                if isinstance(data, list):
                    for entry in data:
                        if isinstance(entry, dict):
                            if 'ip_address' in entry:
                                new_ips.add(entry['ip_address'])
                            elif 'dst_ip' in entry: # Some feeds use different keys
                                new_ips.add(entry['dst_ip'])

                if new_ips:
                    self.ips = new_ips
                    self.last_updated = time.time()
                    self.save_cache()
                    print(f"[ThreatIntel] Updated. Total IOCs: {len(self.ips)}")
                else:
                    print("[ThreatIntel] Warning: No IPs found in feed.")

        except urllib.error.URLError as e:
            print(f"[ThreatIntel] Network error fetching feed: {e}")
        except Exception as e:
            print(f"[ThreatIntel] Unexpected error: {e}")

    def is_malicious(self, ip):
        """Checks if an IP is in the threat feed."""
        return ip in self.ips

    def get_random_c2(self):
        """Returns a random C2 IP from the feed."""
        if not self.ips:
            return "127.0.0.1" # Fallback
        return random.choice(list(self.ips))

if __name__ == "__main__":
    # Test run
    ti = ThreatIntel()
    ti.fetch_feed(force=True)
    print(f"Sample C2: {ti.get_random_c2()}")
