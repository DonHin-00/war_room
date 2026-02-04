#!/usr/bin/env python3
"""
Threat Intelligence Module
Fetches and manages real-world threat data from multiple free sources.
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
        THREAT_FEEDS = {
            "Feodo_Tracker": "https://feodotracker.abuse.ch/downloads/ipblocklist.json",
            "CINS_Army": "http://cinsscore.com/list/ci-badguys.txt",
            "GreenSnow": "https://blocklist.greensnow.co/greensnow.txt"
        }
        THREAT_FEED_CACHE = "threat_feed_cache.json"
    config = Config()

class ThreatIntel:
    def __init__(self, cache_file=None):
        self.cache_file = cache_file or config.THREAT_FEED_CACHE
        self.ips = set()
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
                print(f"[ThreatIntel] Loaded {len(self.ips)} IOCs from cache.")
            except Exception as e:
                print(f"[ThreatIntel] Cache load failed: {e}")

    def save_cache(self):
        """Saves current threat data to local cache."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump({
                    'ips': list(self.ips),
                    'last_updated': self.last_updated
                }, f)
        except Exception as e:
            print(f"[ThreatIntel] Cache save failed: {e}")

    def fetch_feed(self, force=False):
        """Fetches the latest threat feeds."""
        # Update if cache is older than 24 hours or forced
        if not force and (time.time() - self.last_updated < 86400) and self.ips:
            return

        new_ips = set()

        for name, url in config.THREAT_FEEDS.items():
            print(f"[ThreatIntel] Fetching {name} from {url}...")
            try:
                req = urllib.request.Request(
                    url,
                    headers={'User-Agent': 'WarRoom-Simulation/1.0'}
                )
                with urllib.request.urlopen(req) as response:
                    content = response.read().decode('utf-8')
                    if not content:
                        print(f"[ThreatIntel] Empty response from {name}.")
                        continue

                    # Determine format and parse
                    parsed_ips = set()
                    if url.endswith('.json'):
                        parsed_ips = self._parse_json(content)
                    else:
                        parsed_ips = self._parse_text(content)

                    print(f"[ThreatIntel] {name}: Found {len(parsed_ips)} IPs.")
                    new_ips.update(parsed_ips)

            except urllib.error.URLError as e:
                print(f"[ThreatIntel] Network error fetching {name}: {e}")
            except Exception as e:
                print(f"[ThreatIntel] Error processing {name}: {e}")

        if new_ips:
            self.ips = new_ips
            self.last_updated = time.time()
            self.save_cache()
            print(f"[ThreatIntel] Total Unique IOCs: {len(self.ips)}")
        else:
            print("[ThreatIntel] Warning: No IPs found in any feed.")

    def _parse_json(self, content):
        """Parses JSON feeds (specifically Feodo Tracker style)."""
        ips = set()
        try:
            data = json.loads(content)
            if isinstance(data, list):
                for entry in data:
                    if isinstance(entry, dict):
                        if 'ip_address' in entry:
                            ips.add(entry['ip_address'])
                        elif 'dst_ip' in entry:
                            ips.add(entry['dst_ip'])
        except json.JSONDecodeError:
            pass
        return ips

    def _parse_text(self, content):
        """Parses plain text feeds (one IP per line)."""
        ips = set()
        for line in content.splitlines():
            line = line.strip()
            # Ignore comments and empty lines
            if not line or line.startswith('#') or line.startswith('//'):
                continue
            # Simple validation: looks like an IP (contains dots, numbers)
            # We could use regex but simple checks suffice for speed
            parts = line.split() # Sometimes feeds have "IP # comment"
            potential_ip = parts[0]
            if potential_ip.count('.') == 3 and all(c.isdigit() or c == '.' for c in potential_ip):
                 ips.add(potential_ip)
        return ips

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
