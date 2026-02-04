
import logging
import time
import random

class VirtualProcess:
    def __init__(self, pid, name, parent_id=0):
        self.pid = pid
        self.name = name
        self.parent_id = parent_id
        self.status = "RUNNING"

import json
import os

class VirtualFileSystem:
    def __init__(self):
        self.files = {"/": {"type": "dir", "children": ["etc", "bin", "home"]}}

    def write(self, path, content):
        # Simplified FS logic
        self.files[path] = {"type": "file", "size": len(content), "mtime": time.time()}
        return True

    def delete(self, path):
        if path in self.files:
            del self.files[path]
            return True
        return False

    def export_state(self):
        return self.files

    def import_state(self, state):
        self.files = state

class VirtualNetwork:
    def __init__(self):
        self.connections = [] # (src, dst, port)

    def connect(self, src_pid, dst_ip, port):
        # Simulated Latency
        time.sleep(random.uniform(0.01, 0.05))
        self.connections.append((src_pid, dst_ip, port))
        return True

class Sandbox:
    """A safe emulation environment for Proxy vs Proxy warfare."""
    def __init__(self, persistence_file="emulator_state.json"):
        self.fs = VirtualFileSystem()
        self.network = VirtualNetwork()
        self.processes = {}
        self.pid_counter = 1000
        self.syscall_log = []
        self.persistence_file = persistence_file
        self.load_state()

    def save_state(self):
        state = {
            "fs": self.fs.export_state(),
            "pid_counter": self.pid_counter
        }
        try:
            with open(self.persistence_file, 'w') as f:
                json.dump(state, f)
        except: pass

    def load_state(self):
        if os.path.exists(self.persistence_file):
            try:
                with open(self.persistence_file, 'r') as f:
                    state = json.load(f)
                    self.fs.import_state(state.get("fs", {}))
                    self.pid_counter = state.get("pid_counter", 1000)
            except: pass

    def spawn_process(self, name):
        pid = self.pid_counter
        self.pid_counter += 1
        self.processes[pid] = VirtualProcess(pid, name)
        self.log_syscall(pid, "execve", name)
        self.save_state() # Persist on change
        return pid

    def kill_process(self, pid):
        if pid in self.processes:
            self.processes[pid].status = "KILLED"
            self.log_syscall(0, "kill", str(pid))
            return True
        return False

    def log_syscall(self, pid, call, args):
        event = {
            "timestamp": time.time(),
            "pid": pid,
            "syscall": call,
            "args": args
        }
        self.syscall_log.append(event)
        # Keep log size managed
        if len(self.syscall_log) > 1000:
            self.syscall_log.pop(0)

    def get_events(self):
        return self.syscall_log

    # --- Emulated Actions ---
    def emul_ransomware(self, pid):
        self.log_syscall(pid, "encrypt", "/home/user/documents/*")
        # Virtually encrypt
        self.fs.write("/home/user/documents/report.docx.enc", "ENCRYPTED")
        return "SUCCESS"

    def emul_c2_beacon(self, pid, ip):
        self.log_syscall(pid, "connect", f"{ip}:443")
        self.network.connect(pid, ip, 443)
        return "CONNECTED"

    def emul_cleanup(self, pid):
        self.log_syscall(pid, "unlink", "/var/log/syslog")
        return "DELETED"
