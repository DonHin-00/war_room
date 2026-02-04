#!/usr/bin/env python3
"""
Green Team: User Simulation.
Generates noise, business value (files), and vulnerability (clicks).
"""

import os
import sys
import time
import random
import signal
import secrets
import subprocess

# Add parent dir to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils

# --- VISUALS ---
C_YELLOW = "\033[93m"
C_RESET = "\033[0m"

class YellowBuilder:
    """
    Yellow Team: Builders & Developers.
    Creates infrastructure, writes code, and occasionally introduces vulnerabilities (simulated).
    """
    def __init__(self):
        self.running = True
        self.active_services = []
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        self.setup()

    def setup(self):
        print(f"{C_YELLOW}[SYSTEM] Yellow Team (Builders) Initialized.{C_RESET}")

    def shutdown(self, signum, frame):
        print(f"\n{C_YELLOW}[SYSTEM] Yellow Team finished sprint...{C_RESET}")
        # Kill running services
        for p in self.active_services:
            try: p.terminate()
            except: pass
        self.running = False
        sys.exit(0)

    def build_service(self):
        """Create and RUN a 'Service' (HTTP Server) in the War Zone."""
        service_type = secrets.choice(["app", "api", "portal"])
        port = 9000 + secrets.randbelow(1000)
        fname = os.path.join(config.WAR_ZONE_DIR, f"app_{service_type}_{port}.py")

        # Emulated Vulnerable Application (Standard Lib HTTP Server)
        content = f"""
#!/usr/bin/env python3
# Service: {service_type} on Port {port}
import http.server
import socketserver
import os
import urllib.parse

PORT = {port}

class VulnHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # SIMULATED VULNERABILITY: Logging query params to disk (LFI/Info Leak)
        parsed = urllib.parse.urlparse(self.path)
        if parsed.query:
            with open("access_log.txt", "a") as f:
                f.write(f"Query: {{parsed.query}}\\n")

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Service Running")

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    # Bind to localhost only for safety
    with socketserver.TCPServer(("127.0.0.1", PORT), VulnHandler) as httpd:
        print(f"[{service_type}] Serving on {{PORT}}")
        httpd.serve_forever()
"""
        try:
            utils.secure_create(fname, content.strip())
            os.chmod(fname, 0o755)

            # Launch it
            proc = subprocess.Popen([sys.executable, fname],
                                    cwd=config.WAR_ZONE_DIR,
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)
            self.active_services.append(proc)
            # print(f"{C_YELLOW}[YELLOW] Launched {os.path.basename(fname)} on port {port}{C_RESET}")
        except: pass

    def patch_vulnerability(self):
        """Simulate patching: Rename/Delete old artifacts."""
        if not os.path.exists(config.WAR_ZONE_DIR): return
        # Logic: Find old services or files and 'update' them
        pass

    def run(self):
        while self.running:
            try:
                # Check for Coding Standards from Orange
                standards_path = os.path.join(config.BASE_DIR, "intelligence", "coding_standards.json")
                if os.path.exists(standards_path):
                    # In a real sim, we'd read this and adjust 'vulnerability rate'
                    pass

                action = secrets.choice(["BUILD", "BUILD", "PATCH"])

                if action == "BUILD":
                    self.build_service()
                elif action == "PATCH":
                    self.patch_vulnerability()

                time.sleep(random.uniform(2.0, 5.0))
            except Exception:
                time.sleep(1)

if __name__ == "__main__":
    bot = YellowBuilder()
    bot.run()
