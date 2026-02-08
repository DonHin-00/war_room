#!/usr/bin/env python3
"""
Blue Team Tools
Advanced Forensics: Process Auditing, Beacon Analysis, Log Hunting
"""

import os
import re
import subprocess
import time
import collections

class ProcessAuditor:
    def scan_proc(self):
        """
        Scans /proc for suspicious processes.
        - Deleted binaries (fileless execution)
        - Executing from /tmp or /dev/shm
        """
        suspicious = []
        try:
            # Iterate over all PIDs
            for pid in os.listdir('/proc'):
                if not pid.isdigit(): continue
                try:
                    exe_link = os.readlink(f'/proc/{pid}/exe')
                    cmdline = open(f'/proc/{pid}/cmdline').read().replace('\0', ' ')

                    reason = None
                    if "deleted" in exe_link:
                        reason = "Deleted Binary"
                    elif exe_link.startswith('/tmp') or exe_link.startswith('/dev/shm'):
                        reason = "Suspicious Path"

                    if reason:
                        suspicious.append({'pid': int(pid), 'exe': exe_link, 'reason': reason})
                except (FileNotFoundError, PermissionError):
                    continue
        except Exception:
            pass
        return suspicious

class BeaconHunter:
    def __init__(self):
        self.history = collections.defaultdict(list) # IP -> [timestamps]

    def analyze_network(self, ti_module):
        """
        Scans active connections (ss) and checks against Threat Intel.
        Also builds history for behavioral analysis (future feature).
        """
        hits = []
        try:
            output = subprocess.check_output(["ss", "-tunap"], text=True)
            for line in output.splitlines():
                # Extract Remote IP
                match = re.search(r'\s+(\d+\.\d+\.\d+\.\d+):(\d+)\s+users:\(\(".*?",pid=(\d+)', line)
                if match:
                    remote_ip = match.group(1)
                    pid = int(match.group(3))

                    if ti_module.is_known_threat(remote_ip):
                        hits.append({'pid': pid, 'ip': remote_ip, 'type': 'Known IOC'})
        except Exception:
            pass
        return hits

class ArtifactScanner:
    def scan_persistence(self):
        """Checks for the Red Team's known persistence artifacts."""
        artifacts = []

        # Cron
        if os.path.exists("/tmp/malicious.cron"):
            artifacts.append("/tmp/malicious.cron")

        # Bashrc
        if os.path.exists("/tmp/.bashrc_backdoor"):
            artifacts.append("/tmp/.bashrc_backdoor")

        return artifacts

if __name__ == "__main__":
    pa = ProcessAuditor()
    print(pa.scan_proc())
