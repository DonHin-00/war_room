import os
import ctypes
from apex_framework.ops.syscalls import RawInvoker, SyscallTable
from rich.console import Console

console = Console()

class StealthOperations:
    """
    High-Level Abstractions over Raw Syscalls.
    """
    def __init__(self):
        self.invoker = RawInvoker()

    def ghost_write(self, filepath: str, content: str):
        """
        Writes a file bypassing Python's open().
        """
        console.print(f"[STEALTH] 👻 GhostWriting to {filepath}...")

        # O_WRONLY | O_CREAT | O_TRUNC = 577 (approx) on Linux
        # Let's use 0o1 | 0o100 | 0o1000 = 577 decimal
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        mode = 0o644

        fd = self.invoker.raw_open(filepath, flags, mode)
        if fd < 0:
            console.print(f"[STEALTH] ❌ Syscall open failed: {fd}")
            return False

        res = self.invoker.raw_write(fd, content.encode())
        self.invoker.raw_close(fd)

        console.print(f"[STEALTH] ✅ Bytes Written: {res}")
        return True

    def memfd_exec(self, payload_code: str):
        """
        Fileless Execution via memfd_create.
        Writes python code to RAM file, then executes it via subprocess (simulated execve).
        """
        console.print(f"[STEALTH] 🧠 Creating MemFD (Fileless Storage)...")

        # 1. Create RAM File
        fd = self.invoker.raw_memfd_create("anon_payload", 0)
        if fd < 0:
            console.print("[STEALTH] ❌ MemFD Failed.")
            return

        # 2. Write Payload
        self.invoker.raw_write(fd, payload_code.encode())

        # 3. Execute
        # Since we can't easily fork/execve inside this python script without replacing ourself,
        # we will use /proc/self/fd/FD as a path to pass to a new python instance.
        # This proves the content is readable and executable without a disk path.
        magic_path = f"/proc/self/fd/{fd}"
        console.print(f"[STEALTH] 🚀 Executing via {magic_path}...")

        import subprocess
        try:
            # We must keep FD open for the child to see it?
            # No, CLOEXEC usually closes it. But let's try.
            # We call python3 /proc/self/fd/N
            subprocess.run(["python3", magic_path])
        except Exception as e:
            console.print(f"[STEALTH] ⚠️ Execution Error: {e}")

        self.invoker.raw_close(fd)
