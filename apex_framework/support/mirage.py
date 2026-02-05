import time
import random
import base64
import zlib
import inspect
from typing import Any, Dict

class FractalObfuscator:
    """
    Component 3: FractalObfuscator.
    Wraps code in multiple layers of 'Matryoshka' encoding.
    """
    @staticmethod
    def obfuscate(payload: str, layers: int = 3) -> str:
        data = payload.encode()
        for i in range(layers):
            # Layer 1: Compress
            data = zlib.compress(data)
            # Layer 2: Base64
            data = base64.b64encode(data)
            # Layer 3: Reverse (Simple obfuscation)
            data = data[::-1]

        # Wrap in a decoder stub (Simulated)
        stub = f"""
import zlib, base64
_ = '{data.decode()}'
# FRACTAL LAYER {layers}: Decode logic hidden...
exec(zlib.decompress(base64.b64decode(_[::-1])))
"""
        return stub.strip()

class PhantomShell:
    """
    Component 2: PhantomShell.
    A Tarpit CLI that wastes attacker time.
    """
    def __init__(self):
        self.history = []
        self.active = True
        self.latency = 0.1

    def run_session(self):
        print("\n[PHANTOM] 🕸️ Shell Active. Type 'exit' to leave (if you can).")
        while self.active:
            try:
                # Simulate increasing latency (The Tarpit)
                time.sleep(self.latency)
                self.latency *= 1.5 # Exponential backoff
                if self.latency > 2.0: self.latency = 2.0 # Cap it so we don't wait forever in demo

                cmd = input("root@mainframe:~# ")
                self.history.append(cmd)

                if cmd == "exit":
                    print("logout")
                    break
                elif cmd == "ls":
                    print("bin  etc  home  opt  root  var  .env  passwords.txt")
                elif cmd == "cat .env":
                    print("API_KEY=sk_live_FAKE_KEY_DO_NOT_USE")
                    print("[SYSTEM] 🚨 BEACON TRIGGERED: Admin alerted.")
                elif cmd == "cat passwords.txt":
                    print("admin:hunter2")
                elif cmd == "whoami":
                    print("root (simulated)")
                else:
                    print(f"bash: {cmd}: command not found")
            except:
                break

class PolymorphicDecoy:
    """
    Component 1: PolymorphicDecoy.
    A class that rewrites its behavior when probed.
    """
    def __init__(self, name: str):
        self.name = name
        self.state = "DORMANT"

    def interact(self, method: str):
        print(f"[{self.name}] ⚠️ Probe detected on '{method}'!")

        if self.state == "DORMANT":
            self.state = "ACTIVE"
            self._rewrite_self()
            return "Access Denied: Initializing Security Protocol..."

        elif self.state == "ACTIVE":
            self.state = "TARPIT"
            return "Authenticating... (Please wait)"

        elif self.state == "TARPIT":
            # Infinite wait simulation
            time.sleep(1)
            return "Still Authenticating... (Packet Loss Detected)"

    def _rewrite_self(self):
        print(f"[{self.name}] 🧬 MUTATING: Changing internal logic structure...")
        # In a real dynamic system, we would use setattr/delattr
        # Here we simulate the effect
        self.interact = lambda method: "SYSTEM ERROR: Memory Corruption"
