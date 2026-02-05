import sys
import os
from rich.console import Console

console = Console()

class PlatformHAL:
    """
    Hardware Abstraction Layer.
    Detects OS and returns the appropriate Strategy.
    """
    @staticmethod
    def detect():
        console.print("[HAL] 🌍 Analyzing Environment...")

        # 1. Android Detection
        if hasattr(sys, 'getandroidapilevel') or os.path.exists("/system/build.prop"):
            console.print("[HAL] 📱 Platform Detected: ANDROID")
            from apex_framework.ops.android import AndroidStrategy
            return AndroidStrategy()

        # 2. Windows Detection
        elif sys.platform == "win32":
            console.print("[HAL] 🪟 Platform Detected: WINDOWS")
            from apex_framework.ops.windows import WindowsStrategy
            return WindowsStrategy()

        # 3. Linux Detection (Default)
        else:
            console.print("[HAL] 🐧 Platform Detected: LINUX")
            from apex_framework.ops.linux import LinuxStrategy
            return LinuxStrategy()
