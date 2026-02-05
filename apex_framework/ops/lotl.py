import os
import socket
import struct
from typing import List, Dict, Any
from rich.console import Console

console = Console()

class AdvancedLOTL:
    """
    Living Off The Land (Real).
    Uses /proc filesystem to map network and environment without external binaries.
    """

    @staticmethod
    def parse_proc_net_tcp() -> List[Dict]:
        """
        Parses /proc/net/tcp to find open listening ports.
        Decodes Hex IP:Port format.
        """
        results = []
        try:
            with open("/proc/net/tcp", "r") as f:
                lines = f.readlines()[1:] # Skip header

            for line in lines:
                parts = line.strip().split()
                local_addr = parts[1]
                state = parts[3]

                # State 0A = LISTEN
                if state == "0A":
                    ip_hex, port_hex = local_addr.split(':')

                    # Decode Port
                    port = int(port_hex, 16)

                    # Decode IP (Little Endian)
                    # e.g. 0100007F -> 127.0.0.1
                    packed = struct.pack("<L", int(ip_hex, 16))
                    ip = socket.inet_ntoa(packed)

                    results.append({"type": "tcp_listen", "ip": ip, "port": port})
        except Exception as e:
            console.print(f"[LOTL] ⚠️ Failed to read /proc/net/tcp: {e}")

        return results

    @staticmethod
    def parse_proc_arp() -> List[Dict]:
        """
        Parses /proc/net/arp to find neighbors (Passive Discovery).
        """
        neighbors = []
        try:
            with open("/proc/net/arp", "r") as f:
                lines = f.readlines()[1:]

            for line in lines:
                parts = line.split()
                ip = parts[0]
                mac = parts[3]
                device = parts[5]
                if mac != "00:00:00:00:00:00":
                    neighbors.append({"type": "neighbor", "ip": ip, "mac": mac, "iface": device})
        except: pass
        return neighbors

    @staticmethod
    def map_mounts() -> List[Dict]:
        """
        Parses /proc/mounts to find writable paths and container clues.
        """
        mounts = []
        try:
            with open("/proc/mounts", "r") as f:
                for line in f:
                    parts = line.split()
                    device, path, fs_type, opts = parts[0], parts[1], parts[2], parts[3]

                    writable = "rw" in opts
                    mounts.append({"path": path, "writable": writable, "fs": fs_type})
        except: pass
        return mounts

    @staticmethod
    def fingerprint_env() -> Dict[str, Any]:
        """
        Detects Containerization via cgroups.
        """
        env_type = "Bare Metal"
        try:
            with open("/proc/1/cgroup", "r") as f:
                content = f.read()
                if "docker" in content: env_type = "Docker"
                elif "kubepods" in content: env_type = "Kubernetes"
                elif "lxc" in content: env_type = "LXC"
        except: pass

        # Check for AWS/GCP
        cloud = "Unknown"
        # Check vendor in DMI
        if os.path.exists("/sys/class/dmi/id/product_uuid"):
            try:
                with open("/sys/class/dmi/id/product_version", "r") as f:
                    ver = f.read().lower()
                    if "amazon" in ver: cloud = "AWS"
                    elif "google" in ver: cloud = "GCP"
            except: pass

        return {"environment": env_type, "cloud": cloud}
