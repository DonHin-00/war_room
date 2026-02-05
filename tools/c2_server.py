#!/usr/bin/env python3
"""
Simple C2 Server (Emulation)
Listens for HTTP POST beacons from Red Team agents.
"""

import http.server
import socketserver
import logging
import sys
import threading

# Configuration
PORT = 8080
LOG_FILE = "c2_server.log"

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(message)s')

class C2Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        data_str = post_data.decode('utf-8', errors='ignore')

        if "type=EXFIL" in data_str:
             logging.info(f"🚨 EXFILTRATION DETECTED: {self.client_address[0]} - {data_str[:100]}...")
             self.wfile.write(b"ACK_EXFIL")
        else:
             logging.info(f"BEACON RECEIVED: {self.client_address[0]} - {data_str}")
             self.wfile.write(b"ACK_CMD:SLEEP")

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

    def log_message(self, format, *args):
        return # Squelch stdout logging

def run_server():
    try:
        with socketserver.TCPServer(("", PORT), C2Handler) as httpd:
            print(f"💀 C2 Server listening on port {PORT}")
            httpd.serve_forever()
    except OSError:
        print(f"⚠️ Port {PORT} busy, C2 Server might already be running.")

if __name__ == "__main__":
    run_server()
