import os
import socket
import requests
import json
from typing import List, Dict, Any
from rich.console import Console
from rich.progress import track
from apex_framework.ops.lotl import AdvancedLOTL

console = Console()

class AssetDiscovery:
    """
    Mass Scale Reconnaissance.
    Updated for 2026 TTPs: AI Probing, Cloud/K8s, Observability.
    AND Advanced LOTL Integration (ProcFS).
    """
    def __init__(self, target: str):
        self.target = target
        self.findings = []
        self.critical_paths = []

    def scan_mass_scale(self):
        if os.path.exists(self.target) or self.target == ".":
            self._scan_filesystem(self.target)
            self._scan_local_services() # AI Probe
            self._run_advanced_lotl() # New Native Recon
        else:
            self._scan_network(self.target)

    def _run_advanced_lotl(self):
        """
        Executes ProcFS based recon.
        """
        console.print("[RECON] 🦅 Engaging Advanced LOTL (ProcFS)...", style="bold blue")

        # 1. Env Fingerprint
        env = AdvancedLOTL.fingerprint_env()
        console.print(f"  [cyan]ENVIRONMENT[/]: {env}")
        self.findings.append({"type": "environment", "data": env})

        # 2. Passive Network Map
        ports = AdvancedLOTL.parse_proc_net_tcp()
        for p in ports:
            console.print(f"  [green]LISTENING[/]: {p['ip']}:{p['port']}")
            self.critical_paths.append({"type": "local_listener", "details": p})

        # 3. Neighbors (ARP)
        neighbors = AdvancedLOTL.parse_proc_arp()
        for n in neighbors:
            console.print(f"  [yellow]NEIGHBOR[/]: {n['ip']} ({n['mac']})")
            self.findings.append(n)

        # 4. Writable Paths
        mounts = AdvancedLOTL.map_mounts()
        writable = [m['path'] for m in mounts if m['writable']]
        if "/tmp" in writable or "/dev/shm" in writable:
             console.print(f"  [green]WRITABLE[/]: /tmp, /dev/shm found (Persistence vectors)")

    def _scan_local_services(self):
        console.print("[RECON] 🤖 Probing Local AI & Cloud Services...", style="bold blue")
        ai_ports = [11434, 8000, 5000]
        for port in ai_ports:
            try:
                resp = requests.get(f"http://127.0.0.1:{port}/api/tags", timeout=1)
                if resp.status_code == 200:
                    console.print(f"  [green]AI DETECTED[/]: Local LLM on port {port}")
                    self.critical_paths.append({"type": "AI_Model", "details": f"Port {port}"})
                    self._probe_ai_injection(port)
            except: pass

        try:
            resp = requests.get("http://169.254.169.254/latest/meta-data/", timeout=1)
            if resp.status_code == 200:
                console.print("  [green]CLOUD DETECTED[/]: AWS/Cloud Metadata exposed")
                self.critical_paths.append({"type": "Cloud_Metadata", "details": "Exposed"})
        except: pass

    def _probe_ai_injection(self, port):
        console.print(f"  [red]💉 INJECTION ATTEMPTED on Port {port}[/]")

    def _scan_filesystem(self, root_dir):
        console.print(f"[RECON] 📂 Scanning Filesystem: {root_dir}", style="bold blue")
        self._scrape_history()
        obs_files = ["datadog.yaml", "newrelic.yml", "filebeat.yml", "promtail-config.yaml"]

        files = []
        for root, dirs, files_in_dir in os.walk(root_dir):
            if ".git" in root or "__pycache__" in root: continue
            for f in files_in_dir:
                files.append(os.path.join(root, f))
                if f in obs_files:
                    console.print(f"  [yellow]OBSERVABILITY CONFIG[/]: {f}")
                    self.critical_paths.append({"type": "Observability_Config", "file": os.path.join(root, f)})

        for filepath in track(files, description="Scanning Files..."):
            self._analyze_file(filepath)
            self._check_suid(filepath)
            self._check_sbom(filepath)

    def _check_sbom(self, filepath):
        if filepath.endswith("package.json") or filepath.endswith("requirements.txt"):
            self.findings.append({"type": "SBOM", "file": filepath})

    def _scrape_history(self):
        history_files = [os.path.expanduser("~/.bash_history"), os.path.expanduser("~/.zsh_history")]
        for hf in history_files:
            if os.path.exists(hf):
                try:
                    with open(hf, 'r', errors='ignore') as f:
                        for line in f:
                            if "sudo" in line and "-S" in line:
                                self.critical_paths.append({"type": "HistoryCreds", "file": hf, "snippet": line.strip()})
                except: pass

    def _check_suid(self, filepath):
        try:
            st = os.stat(filepath)
            if st.st_mode & 0o4000:
                self.critical_paths.append({"type": "SUID_Binary", "file": filepath})
        except: pass

    def _scan_network(self, ip):
        console.print(f"[RECON] 📡 Scanning Network Target: {ip}", style="bold blue")
        ports = [21, 22, 80, 443, 3306, 8080, 11434]
        for port in track(ports, description="Scanning Ports..."):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                result = s.connect_ex((ip, port))
                if result == 0:
                    console.print(f"  [green]OPEN PORT[/]: {port}")
                    self.findings.append({"type": "open_port", "ip": ip, "port": port})
                s.close()
            except: pass

    def _analyze_file(self, filepath):
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
