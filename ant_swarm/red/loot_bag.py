import base64
import random
import time
from typing import List, Dict, Any
from rich.console import Console

console = Console()

class StegoTunnel:
    """
    Obfuscated Exfiltration.
    Hides loot in benign traffic patterns.
    """
    @staticmethod
    def encode_loot(data: str) -> str:
        """
        Encodes data into a fake HTTP Header.
        """
        # Simple obfuscation: Base64 + Reverse + Salt
        salted = f"{random.randint(1000,9999)}_{data}"
        encoded = base64.b64encode(salted.encode()).decode()
        # Simulate an HTTP Header
        return f"X-Correlation-ID: {encoded}"

    @staticmethod
    def pulse_exfil(data_queue: List[str]):
        """
        Sends data in bursts when noise is high.
        """
        if not data_queue: return
        console.print("[LOOT BAG] 💓 C2 Pulse: Waiting for Noise Floor...", style="dim")
        # Simulate waiting
        time.sleep(0.1)
        console.print("[LOOT BAG] 📡 Transmitting Burst...")
        for item in data_queue:
            packet = StegoTunnel.encode_loot(item)
            console.print(f"  > [dim]{packet}[/]")
        data_queue.clear()

class ShadowSmuggler:
    """
    Sneaking Things In.
    Reconstructs payloads from fragmented noise.
    """
    @staticmethod
    def reconstruct_payload(fragments: List[str]) -> str:
        """
        Takes benign-looking text fragments and extracts the weapon.
        """
        console.print("[LOOT BAG] 🧛 Smuggling Payload from artifacts...")
        combined = ""
        for frag in fragments:
            # Simulated stego extraction (e.g., taking the first char of each word)
            # For demo, we just assume the fragment IS the chunk
            combined += frag

        try:
            # Decode the smuggled payload (Reverse of StegoTunnel for symmetry)
            # Assuming payload comes in base64 chunks
            decoded = base64.b64decode(combined).decode()
            return decoded
        except:
            return "ERROR: Payload Corrupted"

class LootBag:
    """
    The External Module.
    Handles Infil/Exfil.
    """
    def __init__(self):
        self.exfil_queue = []
        self.stego = StegoTunnel()
        self.smuggler = ShadowSmuggler()

    def queue_for_exfil(self, data: str):
        console.print(f"[LOOT BAG] 💰 Stashing Loot: {data[:15]}...")
        self.exfil_queue.append(data)

        # Auto-trigger if queue gets full
        if len(self.exfil_queue) >= 3:
            self.trigger_exfil()

    def trigger_exfil(self):
        self.stego.pulse_exfil(self.exfil_queue)

    def smuggle_weapon_in(self, fragments: List[str]) -> str:
        return self.smuggler.reconstruct_payload(fragments)
