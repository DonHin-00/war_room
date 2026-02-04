#!/usr/bin/env python3
import os
import time
import signal
import socket
import sys

# Add root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config
import utils

logger = utils.setup_logging("BlueEDR", config.BLUE_LOG)

ALLOWED_PORTS = [22] # SSH is usually okay. 8080 is NOT.

def scan_network():
    """Scan for unauthorized listening ports."""
    # Method 1: Scan /proc/net/tcp
    # This maps local_address (hex) -> inode
    unauthorized = []
    try:
        with open("/proc/net/tcp", "r") as f:
            next(f) # Skip header
            for line in f:
                parts = line.strip().split()
                if not parts: continue

                local_addr = parts[1]
                state = parts[3]
                inode = parts[9]

                # 0A = LISTEN
                if state == "0A":
                    ip, port_hex = local_addr.split(':')
                    port = int(port_hex, 16)

                    if port not in ALLOWED_PORTS:
                        unauthorized.append({"port": port, "inode": inode})
    except Exception as e:
        logger.error(f"Net scan failed: {e}")

    return unauthorized

def find_pid_by_inode(inode):
    """Walk /proc to find which PID owns the socket inode."""
    for pid in os.listdir("/proc"):
        if not pid.isdigit(): continue

        try:
            fd_path = f"/proc/{pid}/fd"
            if not os.access(fd_path, os.R_OK): continue

            for fd in os.listdir(fd_path):
                try:
                    target = os.readlink(f"{fd_path}/{fd}")
                    if f"socket:[{inode}]" in target:
                        return int(pid)
                except Exception: pass
        except Exception: pass
    return None

def scan_processes():
    """Signature scan running processes (Memory Scanning Simulation)."""
    # In real life we'd dump memory. Here we hash the executable on disk.
    for pid in os.listdir("/proc"):
        if not pid.isdigit(): continue
        try:
            exe_link = os.readlink(f"/proc/{pid}/exe")
            # If it's running from our repo but isn't whitelisted?
            # Or if it matches a known hash.
            # Simplified: Look for 'red_implant' in cmdline even if renamed
            with open(f"/proc/{pid}/cmdline", 'rb') as f:
                cmdline = f.read().replace(b'\0', b' ')

            if b"red_implant" in cmdline or b"svc_worker" in cmdline:
                 return int(pid)
        except Exception: pass
    return None

def hunt():
    logger.info("🛡️ EDR Agent Active. Monitoring Network & Processes...")

    while True:
        # 1. Network Defense
        threats = scan_network()

        for threat in threats:
            port = threat['port']
            inode = threat['inode']

            logger.warning(f"🚨 UNAUTHORIZED LISTENER: Port {port}")

            pid = find_pid_by_inode(inode)
            if pid:
                logger.critical(f"🔫 TERMINATING PID {pid} (Socket Owner)")
                try:
                    os.kill(pid, signal.SIGKILL)
                    logger.info("✅ Threat Neutralized.")
                except Exception as e:
                    logger.error(f"Failed to kill {pid}: {e}")
            else:
                logger.warning(f"Could not find PID for inode {inode}")

        # 2. Process Defense (Memory/Signature)
        malware_pid = scan_processes()
        if malware_pid and malware_pid != os.getpid():
             logger.critical(f"🦠 MALWARE DETECTED IN MEMORY: PID {malware_pid}")
             try:
                 os.kill(malware_pid, signal.SIGKILL)
                 logger.info("✅ Malware Process Terminated.")
             except Exception: pass

        time.sleep(2)

if __name__ == "__main__":
    hunt()
