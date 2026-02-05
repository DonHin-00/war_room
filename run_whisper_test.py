#!/usr/bin/env python3
import os
import sys
from rich.console import Console
from rich.panel import Panel
from apex_framework.ops.stealth_ops import StealthOperations

console = Console()

def main():
    console.print(Panel("[bold red]APEX v24: LINUX WHISPERS (DIRECT SYSCALLS)[/]", expand=False))

    ops = StealthOperations()

    # 1. Ghost Write
    console.print("\n[SCENARIO] 👻 Testing Ghost Write (Direct Syscall)...")
    target_file = "secret_whisper.txt"
    if os.path.exists(target_file): os.remove(target_file)

    success = ops.ghost_write(target_file, "This file was created via raw syscalls.")

    if success and os.path.exists(target_file):
        with open(target_file, 'r') as f:
            content = f.read()
        console.print(f"[SCENARIO] ✅ SUCCESS: File Exists. Content: '{content}'")
    else:
        console.print("[SCENARIO] ❌ FAILURE: Write failed.")

    # 2. MemFD Exec
    console.print("\n[SCENARIO] 🧠 Testing MemFD Execution (Fileless)...")
    payload = "print('Hello from the Ethereal Plane (RAM Only)')"

    # This should print the output of the python script executed from RAM
    ops.memfd_exec(payload)

    # Cleanup
    if os.path.exists(target_file): os.remove(target_file)

if __name__ == "__main__":
    main()
