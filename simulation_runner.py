#!/usr/bin/env python3
"""
Cyber War Swarm Orchestrator
Manages the lifecycle of the full agent swarm.
"""

import subprocess
import sys
import os
import time
import signal
import logging

# Configuration
AGENTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agents")
TOOLS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools")
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
if not os.path.exists(LOG_DIR): os.mkdir(LOG_DIR)

AGENTS = {
    "C2_Server": "tools/c2_server.py",
    "Yellow_SRE": "agents/yellow_brain.py",
    "Bot_WAF": "agents/bot_brain.py",
    "Blue_Defense": "agents/blue_brain.py",
    "Red_Attack": "agents/red_brain.py",
    "Green_User": "agents/green_brain.py",
    "APT_State": "agents/apt_brain.py"
}

class SwarmOrchestrator:
    def __init__(self):
        self.processes = {}
        self.running = True
        self.setup_logging()

        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - SWARM - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger("Orchestrator")

    def handle_signal(self, signum, frame):
        self.logger.info("Shutdown signal received. Terminating Swarm...")
        self.running = False
        self.stop_all()

    def start_agent(self, name, script_path):
        full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_path)
        log_file = os.path.join(LOG_DIR, f"{name.lower()}.log")

        try:
            with open(log_file, "a") as f:
                p = subprocess.Popen(
                    [sys.executable, "-u", full_path],
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    cwd=os.path.dirname(os.path.abspath(__file__))
                )
            self.processes[name] = p
            self.logger.info(f"Started {name} (PID: {p.pid})")
        except Exception as e:
            self.logger.error(f"Failed to start {name}: {e}")

    def monitor_agents(self):
        """Restarts dead agents."""
        for name, p in list(self.processes.items()):
            if p.poll() is not None:
                self.logger.warning(f"Agent {name} died! Restarting...")
                script = AGENTS[name]
                self.start_agent(name, script)

    def stop_all(self):
        for name, p in self.processes.items():
            try:
                p.terminate()
            except: pass

        # Give them a moment to cleanup
        time.sleep(2)

        for name, p in self.processes.items():
            if p.poll() is None:
                try: p.kill()
                except: pass
        self.logger.info("Swarm offline.")

    def run(self):
        self.logger.info("Initializing Cyber War Swarm...")

        # Cleanup environment (optional safety)
        # os.system("rm -rf /tmp/ports /tmp/mock_pastes")

        # Start Infrastructure First
        self.start_agent("C2_Server", AGENTS["C2_Server"])
        self.start_agent("Yellow_SRE", AGENTS["Yellow_SRE"])
        time.sleep(2) # Wait for ports

        # Start Defenses
        self.start_agent("Bot_WAF", AGENTS["Bot_WAF"])
        self.start_agent("Blue_Defense", AGENTS["Blue_Defense"])
        time.sleep(1)

        # Start Actors
        self.start_agent("Red_Attack", AGENTS["Red_Attack"])
        self.start_agent("Green_User", AGENTS["Green_User"])
        self.start_agent("APT_State", AGENTS["APT_State"])

        self.logger.info("Swarm Active. Press Ctrl+C to stop.")

        while self.running:
            self.monitor_agents()
            time.sleep(5)

if __name__ == "__main__":
    orch = SwarmOrchestrator()
    orch.run()
