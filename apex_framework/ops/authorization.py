from rich.console import Console
from rich.prompt import Confirm

console = Console()

class AuthorizationProtocol:
    """
    Protocol for Human-in-the-Loop decision making.
    """
    @staticmethod
    def request_intervention(intel: dict) -> bool:
        """
        Pauses execution and asks the Commander for orders.
        """
        console.print("\n[bold red blink]🚨 CRITICAL INTELLIGENCE ACQUIRED 🚨[/]")
        console.print(f"[bold white]Target Type:[/] {intel['type']}")
        console.print(f"[bold white]Location:[/] {intel['file']}")
        if 'snippet' in intel:
            console.print(f"[bold white]Evidence:[/] {intel['snippet']}")

        console.print("\n[dim]Automated systems have flagged this as a MAJOR strategic opportunity.[/]")

        return Confirm.ask("[bold red]❓ COMMANDER: Authorize Exploitation?[/]")
