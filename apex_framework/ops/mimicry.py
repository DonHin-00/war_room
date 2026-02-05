import time
import random
import os
import subprocess
from rich.console import Console

console = Console()

class BehavioralMimic:
    """
    Anti-AI Evasion.
    Mimics user behavior to blend into EDR logs.
    """
    def __init__(self):
        self.user_history = []
        self._learn_user_behavior()

    def _learn_user_behavior(self):
        """
        Analyzes shell history to learn typing cadence and common commands.
        """
        try:
            hist_path = os.path.expanduser("~/.bash_history")
            if os.path.exists(hist_path):
                with open(hist_path, 'r', errors='ignore') as f:
                    lines = f.readlines()
                    self.user_history = [l.strip() for l in lines[-50:]] # Learn last 50 commands
        except: pass
        if not self.user_history:
            self.user_history = ["ls -la", "cd", "git status", "cat config.json"]

    def execute_with_mimicry(self, func, *args):
        """
        Interleaves the target function with fake user activity.
        """
        console.print("[MIMIC] 🎭 Engaging Behavioral Camouflage...")

        # 1. Fake Activity
        fake_cmd = random.choice(self.user_history)
        self._simulate_typing_and_exec(fake_cmd)

        # 2. Real Activity
        console.print("[MIMIC] ⚡ Slipping in payload...")
        result = func(*args)

        # 3. Fake Activity (Cover tracks)
        self._simulate_typing_and_exec("ls")

        return result

    def _simulate_typing_and_exec(self, cmd):
        """
        Simulates typing delay and executes a benign command.
        """
        # Typing delay
        delay = len(cmd) * 0.05 # 50ms per char
        time.sleep(delay)

        # Execute benign command (carefully)
        if cmd.startswith("ls") or cmd.startswith("pwd") or cmd.startswith("whoami"):
            # subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL)
            # For demo visibility:
            console.print(f"  [dim]User> {cmd}[/]")
