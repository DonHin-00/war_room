import ctypes
import os
import struct
from typing import Any
from rich.console import Console

console = Console()

class SyscallTable:
    """
    x86_64 Syscall Numbers.
    """
    SYS_read = 0
    SYS_write = 1
    SYS_open = 2
    SYS_close = 3
    SYS_socket = 41
    SYS_connect = 42
    SYS_accept = 43
    SYS_sendto = 44
    SYS_recvfrom = 45
    SYS_execve = 59
    SYS_memfd_create = 319
    SYS_execveat = 322

class RawInvoker:
    """
    Invokes syscalls directly via Ctypes.
    """
    def __init__(self):
        # Load libc to access the 'syscall' wrapper function
        # This is the standard way on Linux to invoke raw syscalls if not writing inline asm
        try:
            self.libc = ctypes.CDLL(None)
            self.syscall = self.libc.syscall
        except Exception as e:
            console.print(f"[WHISPER] ❌ Failed to load libc: {e}")

    def invoke(self, number: int, *args) -> int:
        """
        Executes the syscall.
        """
        return self.syscall(number, *args)

    def raw_write(self, fd: int, data: bytes) -> int:
        return self.invoke(SyscallTable.SYS_write, fd, data, len(data))

    def raw_open(self, path: str, flags: int, mode: int) -> int:
        return self.invoke(SyscallTable.SYS_open, path.encode(), flags, mode)

    def raw_close(self, fd: int) -> int:
        return self.invoke(SyscallTable.SYS_close, fd)

    def raw_memfd_create(self, name: str, flags: int) -> int:
        return self.invoke(SyscallTable.SYS_memfd_create, name.encode(), flags)
