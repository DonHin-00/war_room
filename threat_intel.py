#!/usr/bin/env python3
"""
Threat Intelligence Module
Fetches and manages real-world threat data from multiple free sources.
Implements rigorous validation to prevent data poisoning.
"""

import json
import os
import time
import urllib.request
import urllib.error
import random
import logging
import ipaddress
import re

try:
    import config
except ImportError:
    # Fallback if config is not in python path
    class Config:
        THREAT_FEEDS = {}
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

    def validate_ip(self, ip):
        """
        Validates an IP address.
        Returns True if the IP is valid, public, and not reserved/local.
        Prevents data poisoning where feeds inject localhost/LAN IPs.
        """
        try:
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast or ip_obj.is_reserved:
                return False
            # IPv4 specific check for 0.0.0.0
            if str(ip) == "0.0.0.0":
                return False
            return True
        except ValueError:
            return False

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
                with urllib.request.urlopen(req, timeout=10) as response:
                    content = response.read().decode('utf-8', errors='ignore')
                    if not content:
                        print(f"[ThreatIntel] Empty response from {name}.")
                        continue

                    # Determine format and parse
                    parsed_ips = set()

                    # Heuristic for JSON vs Text
                    if content.strip().startswith('{') or content.strip().startswith('['):
                        parsed_ips = self._parse_json(content)
                    else:
                        parsed_ips = self._parse_text(content)

                    # Validate extracted IPs
                    valid_ips = set()
                    for ip in parsed_ips:
                        if self.validate_ip(ip):
                            valid_ips.add(ip)

                    print(f"[ThreatIntel] {name}: Found {len(valid_ips)} valid IPs (from {len(parsed_ips)} raw).")
                    new_ips.update(valid_ips)

            except (urllib.error.URLError, TimeoutError) as e:
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
        """Parses JSON feeds."""
        ips = set()
        try:
            data = json.loads(content)
            # Flatten if dict
            if isinstance(data, dict):
                 data = data.values() # Try to iterate values if it's a dict wrapper

            # Recursive search or specific keys?
            # Given the variety, we'll try specific keys from known feeds
            if isinstance(data, list):
                for entry in data:
                    if isinstance(entry, dict):
                        # Feodo / ThreatFox keys
                        for key in ['ip_address', 'dst_ip', 'ioc_value', 'ip']:
                            if key in entry and entry[key]:
                                ips.add(entry[key])
                                break
        except json.JSONDecodeError:
            pass
        return ips

    def _parse_text(self, content):
        """Parses plain text/CSV feeds."""
        ips = set()
        ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')

        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('//'):
                continue

            # Extract all IPs in the line using Regex
            # This handles CSVs, Hostfiles, and plain lists
            found = ip_pattern.findall(line)
            for ip in found:
                ips.add(ip)
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
