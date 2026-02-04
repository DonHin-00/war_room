#!/usr/bin/env python3
"""
Offline Threat Feed Generator.
Simulates an external threat intelligence provider pushing updates securely.
"""
import sys
import os
import time
import random
import hashlib
import logging

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from utils import atomic_json_io, setup_logging

# Configure logging
setup_logging(config.file_paths['log_file'])
logger = logging.getLogger("FeedGenerator")

def generate_random_hash():
    return hashlib.sha256(os.urandom(32)).hexdigest()

def generate_feed(filepath):
    logger.info("Generating new Threat Intelligence Feed...")

    current_feed = atomic_json_io(filepath)
    if not current_feed:
        current_feed = {"metadata": {"version": 0}, "iocs": []}

    # Ensure version is int
    try:
        ver = int(current_feed['metadata'].get('version', 0))
    except:
        ver = 0

    # Simulate adding new IOCs
    new_iocs = []

    # 1. Random Hashes (Simulate polymorphic malware signatures)
    for _ in range(5):
        new_iocs.append({
            "type": "hash",
            "algorithm": "sha256",
            "value": generate_random_hash(),
            "confidence": random.randint(70, 99),
            "created": time.time()
        })

    # 2. Filenames (Simulate known bad tools)
    tools = ["mimikatz.exe", "nmap.exe", "winpeas.exe", "linpeas.sh"]
    for tool in tools:
        if random.random() > 0.5:
            new_iocs.append({
                "type": "filename",
                "value": f"{tool}_{random.randint(100,999)}",
                "confidence": 85,
                "created": time.time()
            })

    # Update Feed
    if 'metadata' not in current_feed:
        current_feed['metadata'] = {}

    current_feed['metadata']['updated'] = time.time()
    current_feed['metadata']['version'] = ver + 1

    if 'iocs' not in current_feed:
        current_feed['iocs'] = []

    current_feed['iocs'].extend(new_iocs)

    # Keep feed size manageable (rolling window)
    if len(current_feed['iocs']) > 1000:
        current_feed['iocs'] = current_feed['iocs'][-1000:]

    # Secure Write
    atomic_json_io(filepath, current_feed)
    logger.info(f"Feed updated. Version: {current_feed['metadata']['version']} | Total IOCs: {len(current_feed['iocs'])}")

if __name__ == "__main__":
    feed_path = os.path.join(config.BASE_DIR, "intelligence/threat_feed.json")
    generate_feed(feed_path)
