import os
import socket
from typing import List, Dict, Any
from rich.console import Console
from rich.progress import track

console = Console()

class AutoRecon:
    """
    Mass Scale Reconnaissance.
    Refactored for REAL Port Scanning and File Scanning.
    ENHANCED: SUID & History Scanning.
    """
    def __init__(self, target: str):
        self.target = target
        self.findings = []
        self.critical_paths = []

    def scan_mass_scale(self):
        if os.path.exists(self.target) or self.target == ".":
            self._scan_filesystem(self.target)
        else:
            self._scan_network(self.target)

    def _scan_filesystem(self, root_dir):
        console.print(f"[RED CAMPAIGN] 📂 Scanning Filesystem: {root_dir}", style="bold red")

        # 1. History Scraping
        self._scrape_history()

        files = []
        for root, dirs, files_in_dir in os.walk(root_dir):
            if ".git" in root or "__pycache__" in root: continue
            for f in files_in_dir:
                files.append(os.path.join(root, f))

        for filepath in track(files, description="Scanning Files..."):
            self._analyze_file(filepath)
            self._check_suid(filepath)

    def _scrape_history(self):
        history_files = [os.path.expanduser("~/.bash_history"), os.path.expanduser("~/.zsh_history")]
        for hf in history_files:
            if os.path.exists(hf):
                try:
                    with open(hf, 'r', errors='ignore') as f:
                        for line in f:
                            if "sudo" in line and "-S" in line: # sudo with pipe password
                                self.critical_paths.append({"type": "HistoryCreds", "file": hf, "snippet": line.strip()})
                except: pass

    def _check_suid(self, filepath):
        try:
            st = os.stat(filepath)
            if st.st_mode & 0o4000:
                self.critical_paths.append({"type": "SUID_Binary", "file": filepath})
        except: pass

    def _scan_network(self, ip):
        console.print(f"[RED CAMPAIGN] 📡 Scanning Network Target: {ip}", style="bold red")
        ports = [21, 22, 80, 443, 3306, 8080]
        for port in track(ports, description="Scanning Ports..."):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                result = s.connect_ex((ip, port))
                if result == 0:
                    banner = self._grab_banner(s, ip, port)
                    console.print(f"  [green]OPEN PORT[/]: {port} ({banner})")
                    self.findings.append({"type": "open_port", "ip": ip, "port": port, "banner": banner})
                s.close()
            except: pass

    def _grab_banner(self, sock, ip, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect((ip, port))
            if port == 80 or port == 8080:
                s.send(b'HEAD / HTTP/1.0\r\n\r\n')
            banner = s.recv(1024).decode().strip()
            s.close()
            return banner[:50]
        except: return "No Banner"

    def _analyze_file(self, filepath: str):
        try:
            with open(filepath, 'r', errors='ignore') as f:
                content = f.read()
            if "API_KEY" in content:
                self.findings.append({"type": "secret", "file": filepath})
            if "eval(" in content:
                self.critical_paths.append({"type": "RCE", "file": filepath, "snippet": "eval() detected"})
        except: pass

    def get_noise_report(self) -> List[Dict]:
        return self.findings

    def get_critical_intel(self) -> List[Dict]:
        return self.critical_paths
