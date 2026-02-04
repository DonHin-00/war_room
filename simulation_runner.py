#!/usr/bin/env python3
"""
Simulation Runner
Manages the lifecycle of Blue and Red team agents.
"""

import subprocess
import signal
import sys
import time
import os
import argparse
from config import PATHS

BLUE_SCRIPT = "blue_brain.py"
RED_SCRIPT = "red_brain.py"
PURPLE_SCRIPT = "purple_brain.py"

class SimulationRunner:
    def __init__(self, debug=False, reset=False, dashboard=False):
        self.processes = []
        self.running = True
        self.debug = debug
        self.reset = reset
        self.dashboard = dashboard

        # Forward signals
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)

    def handle_signal(self, signum, frame):
        print(f"\n[RUNNER] Received signal {signum}. Stopping agents...")
        self.running = False
        self.stop_agents()
        sys.exit(0)

    def start_agents(self):
        env = os.environ.copy()

        cmd_args = []
        if self.debug:
            cmd_args.append("--debug")
        if self.reset:
            cmd_args.append("--reset")

        # Start Dashboard if requested
        if self.dashboard:
            print(f"[RUNNER] Starting Dashboard...")
            self.processes.append(
                subprocess.Popen([sys.executable, "tools/visualize_threats.py"], env=env)
            )

        print(f"[RUNNER] Starting Blue Team ({BLUE_SCRIPT})...")
        self.processes.append(
            subprocess.Popen([sys.executable, BLUE_SCRIPT] + cmd_args, env=env)
        )

        print(f"[RUNNER] Starting Red Team ({RED_SCRIPT})...")
        self.processes.append(
            subprocess.Popen([sys.executable, RED_SCRIPT] + cmd_args, env=env)
        )

        print(f"[RUNNER] Starting Purple Team ({PURPLE_SCRIPT})...")
        self.processes.append(
            subprocess.Popen([sys.executable, PURPLE_SCRIPT], env=env)
        )

    def stop_agents(self):
        for p in self.processes:
            if p.poll() is None:
                p.send_signal(signal.SIGINT)

        # Wait for them to exit
        for p in self.processes:
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"[RUNNER] Process {p.pid} did not exit. Killing...")
                p.kill()

    def run(self):
        self.start_agents()
        print("[RUNNER] Simulation running. Press Ctrl+C to stop.")

        while self.running:
            try:
                # Check if any process died
                for p in self.processes:
                    if p.poll() is not None:
                        print(f"[RUNNER] Process {p.pid} exited unexpectedly. Stopping all...")
                        self.running = False
                        self.stop_agents()
                        sys.exit(1)
                time.sleep(1)
            except KeyboardInterrupt:
                self.handle_signal(signal.SIGINT, None)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Cyber War Simulation Runner")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--reset", action="store_true", help="Reset memory (Q-tables) before starting")
    parser.add_argument("--dashboard", action="store_true", help="Enable real-time dashboard")
    args = parser.parse_args()

    runner = SimulationRunner(debug=args.debug, reset=args.reset, dashboard=args.dashboard)
    runner.run()
