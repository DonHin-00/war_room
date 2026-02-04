
import logging
import time
import random

class VirtualProcess:
    def __init__(self, pid, name, parent_id=0):
        self.pid = pid
        self.name = name
        self.parent_id = parent_id
        self.status = "RUNNING"

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

class VirtualNetwork:
    def __init__(self):
        self.connections = [] # (src, dst, port)

    def connect(self, src_pid, dst_ip, port):
        self.connections.append((src_pid, dst_ip, port))
        return True

class Sandbox:
    """A safe emulation environment for Proxy vs Proxy warfare."""
    def __init__(self):
        self.fs = VirtualFileSystem()
        self.network = VirtualNetwork()
        self.processes = {}
        self.pid_counter = 1000
        self.syscall_log = []

    def spawn_process(self, name):
        pid = self.pid_counter
        self.pid_counter += 1
        self.processes[pid] = VirtualProcess(pid, name)
        self.log_syscall(pid, "execve", name)
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
