from ant_swarm.support.gatekeeper import SecureGateway
from ant_swarm.red.loot_bag import LootBag
from rich.console import Console

console = Console()

class HardenedTarget:
    """
    A simulated Critical Asset protected by a Gatekeeper WAF.
    """
    def __init__(self):
        self.gateway = SecureGateway()
        self.loot_assembler = [] # Simulates a buffer on the inside

    def attempt_access(self, ip: str, payload: str) -> bool:
        """
        Tries to send a payload through the Gatekeeper.
        """
        result = self.gateway.process_ingress(ip, payload)

        if result["status"] == "ACCEPTED":
            # If accepted, it reaches the inner logic
            # Simulating an application that might reassemble chunks (e.g. TCP stream or File Upload)
            self.loot_assembler.append(result["payload"])
            return True
        else:
            return False

    def execute_internal_logic(self):
        """
        The internal system processing the data.
        If the Red Team smuggled a payload in, it might execute here.
        """
        # Try to decode what we have using the Red Team's own smuggler logic
        # (Simulating the Red Team reassembling their tool on the inside)
        from ant_swarm.red.loot_bag import ShadowSmuggler
        smuggler = ShadowSmuggler()

        # If we have fragments
        if self.loot_assembler:
            console.print("[TARGET] ⚙️ Processing Internal Data Stream...")
            # Ideally the Red Team would have a way to trigger assembly.
            # We check if the data *looks* like a weapon.
            reassembled = smuggler.reconstruct_payload(self.loot_assembler)
            if "print" in reassembled or "os.system" in reassembled:
                console.print(f"[TARGET] 💀 CRITICAL BREACH: Payload Executed! -> {reassembled}")
                return True
        return False
