import os
import re
from typing import List, Dict, Any
from rich.console import Console
from rich.progress import track

console = Console()

class AutoRecon:
    """
    Mass Scale Reconnaissance.
    Clears the noise by scanning thousands of files for low-hanging fruit.
    """
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.findings = []
        self.critical_paths = []

    def scan_mass_scale(self):
        """
        Scans all files for patterns.
        """
        console.print("[RED CAMPAIGN] 🛰️ Initiating Mass Scale Recon...", style="bold red")

        # Simulated "Mass" scan of the repo
        files = []
        for root, dirs, files_in_dir in os.walk(self.root_dir):
            if ".git" in root or "__pycache__" in root: continue
            for f in files_in_dir:
                files.append(os.path.join(root, f))

        for filepath in track(files, description="Scanning Sector..."):
            self._scan_file(filepath)

        console.print(f"[RED CAMPAIGN] Scan Complete. {len(self.findings)} findings. {len(self.critical_paths)} CRITICAL.")

    def _scan_file(self, filepath: str):
        try:
            with open(filepath, 'r', errors='ignore') as f:
                content = f.read()

            # 1. Secret Scavenging (Noise)
            if "API_KEY" in content or "PASSWORD" in content:
                self.findings.append({"type": "secret", "file": filepath})

            # 2. Critical Logic (Major)
            if "eval(" in content or "subprocess.call" in content:
                self.critical_paths.append({"type": "RCE", "file": filepath, "snippet": "eval/subprocess detected"})

            if "admin" in filepath and ".py" in filepath:
                self.critical_paths.append({"type": "HighValueTarget", "file": filepath})

        except: pass

    def get_noise_report(self) -> List[Dict]:
        return self.findings

    def get_critical_intel(self) -> List[Dict]:
        return self.critical_paths
