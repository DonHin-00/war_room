import socket
import threading
import time
import json
from rich.console import Console

console = Console()

class SwarmLink:
    """
    Real Mesh Networking.
    Uses UDP Broadcast to find peers and synchronize.
    """
    def __init__(self, port: int = 1337):
        self.port = port
        self.running = False
        self.peers = set()

    def start_beacon(self):
        self.running = True
        threading.Thread(target=self._broadcast_loop, daemon=True).start()
        threading.Thread(target=self._listen_loop, daemon=True).start()
        console.print(f"[SWARM LINK] 📡 Mesh Network Active on Port {self.port}")

    def stop_beacon(self):
        self.running = False

    def _broadcast_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while self.running:
            msg = json.dumps({"type": "BEACON", "id": "NODE_ALPHA"}).encode()
            try:
                sock.sendto(msg, ('<broadcast>', self.port))
            except: pass
            time.sleep(2)

    def _listen_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', self.port))
        while self.running:
            try:
                data, addr = sock.recvfrom(1024)
                msg = json.loads(data.decode())
                if msg['type'] == "BEACON" and addr[0] not in self.peers:
                    self.peers.add(addr[0])
                    console.print(f"[SWARM LINK] 🔗 New Peer Discovered: {addr[0]}")
            except: pass
