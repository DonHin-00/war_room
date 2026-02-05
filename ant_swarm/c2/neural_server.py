from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
import base64
import zlib
import os
import sys
import inspect
from rich.console import Console

# We need to access the source code of our own modules to stream them
import ant_swarm.red.campaign
import ant_swarm.red.strategist
import ant_swarm.red.pivot

console = Console()

class CodeStreamer:
    """
    Extracts source code from local disk and prepares it for streaming.
    """
    @staticmethod
    def pack_module(module_name):
        """
        Reads the source of a module, compresses, and encodes it.
        """
        try:
            # Map name to file path
            if module_name == "campaign":
                path = ant_swarm.red.campaign.__file__
            elif module_name == "strategist":
                path = ant_swarm.red.strategist.__file__
            elif module_name == "pivot":
                path = ant_swarm.red.pivot.__file__
            else:
                return None

            with open(path, 'r') as f:
                source = f.read()

            # Obfuscation Layer (Simulated "Quad Obfuscation")
            # 1. Compress
            compressed = zlib.compress(source.encode())
            # 2. Base64
            encoded = base64.b64encode(compressed).decode()

            return encoded
        except Exception as e:
            console.print(f"[BRAIN] ❌ Pack Error: {e}")
            return None

class NeuralHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/stream?module='):
            module_name = self.path.split('=')[1]
            console.print(f"[BRAIN] 🧠 Request for Ephemeral Logic: {module_name}")

            payload = CodeStreamer.pack_module(module_name)
            if payload:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({"payload": payload}).encode())
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

class NeuralServer:
    def __init__(self, port=9090):
        self.port = port
        self.server = HTTPServer(('0.0.0.0', port), NeuralHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def start(self):
        console.print(f"[BRAIN] 🔮 Neural Logic Server Online on port {self.port}")
        self.thread.start()

    def stop(self):
        self.server.shutdown()
