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
        self.tracer = utils.TraceLogger(config.TRACE_LOG)
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

    def build_service(self, secure_mode=False):
        """Create and RUN a 'Service' (HTTP Server) in the War Zone."""
        service_type = secrets.choice(["app", "api", "portal"])
        port = 9000 + secrets.randbelow(1000)
        fname = os.path.join(config.WAR_ZONE_DIR, f"app_{service_type}_{port}.py")

        # Logic for Secure vs Vulnerable Code
        if secure_mode:
            log_logic = """
        # SECURE: No sensitive data logging
        parsed = urllib.parse.urlparse(self.path)
        # Safe logging (stdout only, no file write)
        if parsed.query:
            print(f"Safe Log: {parsed.query}")
            """
        else:
            log_logic = """
        # SIMULATED VULNERABILITY: Logging query params to disk (LFI/Info Leak)
        parsed = urllib.parse.urlparse(self.path)
        if parsed.query:
            with open("access_log.txt", "a") as f:
                f.write(f"Query: {parsed.query}\\n")
            """

        # Emulated Application (Standard Lib HTTP Server)
        content = f"""
#!/usr/bin/env python3
# Service: {service_type} on Port {port}
# Secure Mode: {secure_mode}
import http.server
import socketserver
import os
import urllib.parse

PORT = {port}

class VulnHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
{log_logic}

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
        except Exception as e:
            self.tracer.capture_exception(e, context="YELLOW_BUILD")

    def simulate_user_activity(self):
        """
        Simulate a user interacting with files in the workspace.
        This creates the vector for Spearphishing (T1204).
        The user might accidentally execute a malicious script thinking it's a tool.
        """
        if not os.path.exists(config.WAR_ZONE_DIR): return

        try:
            # List "interesting" files that a user might click
            files = os.listdir(config.WAR_ZONE_DIR)
            interesting = [f for f in files if f.startswith("URGENT") or f.startswith("bonus") or f.startswith("deployment")]

            if interesting:
                target = secrets.choice(interesting)
                path = os.path.join(config.WAR_ZONE_DIR, target)

                # "Click" (Execute) the file
                # print(f"{C_YELLOW}[USER] Curiosity killed the cat? Executing {target}...{C_RESET}")
                subprocess.Popen([sys.executable, path],
                                cwd=config.WAR_ZONE_DIR,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        except Exception as e:
            self.tracer.capture_exception(e, context="YELLOW_USER_ERROR")

    def patch_vulnerability(self):
        """Simulate patching: Decommission old services and cleanup artifacts."""
        if not os.path.exists(config.WAR_ZONE_DIR): return

        try:
            # 1. Maintenance: Clean up process handles
            self.active_services = [p for p in self.active_services if p.poll() is None]

            # 2. Decommission oldest service if we have too many (rolling update simulation)
            if len(self.active_services) > 5:
                target = self.active_services.pop(0)
                try:
                    target.terminate()
                    target.wait(timeout=1)
                except:
                    try: target.kill()
                    except: pass

            # 3. Cleanup old files (simulating deprecation)
            now = time.time()
            for f in os.listdir(config.WAR_ZONE_DIR):
                if f.startswith("app_") and f.endswith(".py"):
                    path = os.path.join(config.WAR_ZONE_DIR, f)
                    try:
                        # If file is older than 5 minutes, delete it
                        if now - os.path.getmtime(path) > 300:
                            os.remove(path)
                    except: pass
        except Exception as e:
            self.tracer.capture_exception(e, context="YELLOW_PATCH")

    def run(self):
        secure_mode = False
        while self.running:
            try:
                # Check for Coding Standards from Orange
                standards_path = os.path.join(config.BASE_DIR, "intelligence", "coding_standards.json")
                if os.path.exists(standards_path):
                    try:
                        data = utils.access_memory(standards_path)
                        urgency = data.get("urgency", 1)
                        # Higher urgency or strict standards = Better Code
                        if urgency >= 3 or data.get("input_validation") == "STRICT":
                            secure_mode = True
                        else:
                            secure_mode = False
                    except: pass

                action = secrets.choice(["BUILD", "BUILD", "PATCH"])

                if action == "BUILD":
                    self.build_service(secure_mode=secure_mode)
                elif action == "PATCH":
                    self.patch_vulnerability()

                # Simulate Human User Error (Phishing Susceptibility)
                if secrets.randbelow(10) == 0: # 10% chance to be "curious"
                    self.simulate_user_activity()

                time.sleep(random.uniform(2.0, 5.0))
            except Exception as e:
                self.tracer.capture_exception(e, context="YELLOW_LOOP")
                time.sleep(1)

if __name__ == "__main__":
    bot = YellowBuilder()
    bot.run()
