from rich.console import Console

console = Console()

class WindowsStrategy:
    """
    Operations for Windows Environments.
    """
    def install_persistence(self):
        console.print("[WINDOWS] 💾 Installing Registry Persistence...")
        # Simulated registry add
        key = "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        val = "ApexAgent"
        console.print(f"  > reg add {key} /v {val} /t REG_SZ /d payload.exe /f")

    def perform_recon(self):
        console.print("[WINDOWS] 📡 Running PowerShell Recon...")
        console.print("  > Get-NetTCPConnection | Where-Object {$_.State -eq 'Listen'}")

    def engage_stealth(self):
        console.print("[WINDOWS] 👻 Engaging ADS (Alternate Data Streams)...")
        console.print("  > type payload.exe > calc.exe:stream")
