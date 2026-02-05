#!/usr/bin/env python3
"""
Threat Intelligence Module 2.0
Parallel fetching, rigorous validation, and SQLite persistence.
"""

import json
import time
import urllib.request
import urllib.error
import concurrent.futures
import ipaddress
import re
import logging
from .db_manager import DatabaseManager

try:
    from . import config
except ImportError:
    class Config:
        THREAT_FEEDS = {}
    config = Config()

class ThreatIntel:
    def __init__(self):
        self.db = DatabaseManager()

    def validate_ip(self, ip):
        """Strict IP validation."""
        try:
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast or ip_obj.is_reserved:
                return False
            if str(ip) == "0.0.0.0": return False
            return True
        except ValueError:
            return False

    def validate_domain(self, domain):
        """Basic Domain validation."""
        if not domain or len(domain) > 255: return False
        if domain.count(".") < 1: return False
        allowed = re.compile(r"(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
        return all(allowed.match(x) for x in domain.split("."))

    def _fetch_single_feed(self, name, url):
        """Worker function for concurrent fetching."""
        print(f"[ThreatIntel] Fetching {name}...")
        iocs_found = set()
        ioc_type = "ip" # Default

        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'WarRoom-Simulation/2.0'}
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                content = response.read().decode('utf-8', errors='ignore')

                # Parsing Logic
                if "hash" in name.lower() or "malware" in name.lower() or "fox" in name.lower():
                    ioc_type = "hash"
                    # Regex for SHA256
                    hash_pattern = re.compile(r'\b[a-fA-F0-9]{64}\b')
                    found = hash_pattern.findall(content)
                    for h in found:
                        iocs_found.add(h)

                elif "domain" in name.lower() or "url" in name.lower() or "phish" in name.lower():
                    ioc_type = "domain"
                    # Simple regex for domains/URLs
                    # This is rough but fast. Better parsers exist but this is stdlib only.
                    lines = content.splitlines()
                    for line in lines:
                        line = line.strip()
                        if not line or line.startswith('#'): continue
                        # Try to extract hostname from URL or just line
                        # If comma separated, take 2nd or 3rd column?
                        parts = line.replace('"', '').split(',')
                        for p in parts:
                            p = p.strip()
                            # Check if valid domain
                            if self.validate_domain(p):
                                iocs_found.add(p)

                else:
                    # IP Parsing
                    ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
                    found = ip_pattern.findall(content)
                    for ip in found:
                        if self.validate_ip(ip):
                            iocs_found.add(ip)

        except Exception as e:
            print(f"[ThreatIntel] Error {name}: {e}")
            return None

        return (name, list(iocs_found), ioc_type)

    def update_feeds(self):
        """Fetch all feeds in parallel and update DB."""
        print("[ThreatIntel] Starting parallel update...")
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(self._fetch_single_feed, name, url): name for name, url in config.THREAT_FEEDS.items()}

            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    name, iocs, ioc_type = result
                    if iocs:
                        self.db.add_iocs(iocs, ioc_type, name)
                        print(f"[ThreatIntel] {name}: Added {len(iocs)} {ioc_type}s.")
                    else:
                        print(f"[ThreatIntel] {name}: No valid IOCs found.")

        print(f"[ThreatIntel] Update complete in {time.time() - start_time:.2f}s. Total IOCs: {self.db.count_iocs()}")

    def get_c2_ip(self):
        return self.db.get_random_ioc("ip")

    def get_malicious_domain(self):
        return self.db.get_random_ioc("domain")

    def is_known_threat(self, ioc):
        return self.db.is_malicious(ioc)

if __name__ == "__main__":
    ti = ThreatIntel()
    ti.update_feeds()
