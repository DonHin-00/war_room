#!/usr/bin/env python3
import os
import sys
from rich.console import Console
from rich.panel import Panel
from ant_swarm.core.hive import HiveMind
from ant_swarm.core.ooda import OODALoop
from ant_swarm.core.micro_lm import MicroLM
from ant_swarm.core.council import Council
from ant_swarm.agents.indexer import GlobalIndexer
from ant_swarm.agents.reverse_engineer import ReverseEngineerAgent
from ant_swarm.support.external_storage import LongTermDrive
from ant_swarm.support.coprocessor import Coprocessor
from ant_swarm.support.gatekeeper import SecureGateway

console = Console()

def main():
    console.print(Panel("[bold green]ANT SWARM v9: OOOMP & DEPENDENCIES[/]", expand=False))

    hive = HiveMind()

    # Initialize Support Modules
    storage = LongTermDrive()
    coprocessor = Coprocessor(workers=4)
    gatekeeper = SecureGateway()

    hive.attach_support(storage, coprocessor, gatekeeper)
    rev_eng = ReverseEngineerAgent(hive) # Attach to listen for file changes

    ooda = OODALoop(hive)

    # 1. Demonstrate Reverse Engineer (Graph Analysis)
    # We create a dummy file with calls to analyze
    with open("dummy_graph.py", "w") as f:
        f.write("def a(): b()\ndef b(): c()\ndef c(): pass")

    hive.broadcast("FILE_CHANGED", {"filepath": "dummy_graph.py"}, "User")

    # 2. Gatekeeper
    console.print("\n[bold cyan][SCENARIO][/] 🛡️ External Interface: Valid Request...")
    valid_payload = "Create a login function."
    result = gatekeeper.process_ingress("10.0.0.5", valid_payload)

    task = result["payload"]

    # 3. MicroLM Generation
    console.print(f"\n[bold cyan][ACT][/] MicroLM Processing Task: '{task}'")
    lm = MicroLM()
    doctrine = ooda.execute_cycle(task)
    options = lm.generate_evolved_options(task, doctrine, {}, generations=1)

    # 4. Council with Rich UI
    console.print("\n[bold cyan][COUNCIL][/] 🏛️ Session Convened...")
    council = Council(hive)
    decision = council.select_best_option(task, options)

    if decision['approved']:
        console.print(f"\n[bold green]🎉 WINNER:[/] {decision['selected_variant']}")
        console.print(Panel(decision['code'], title="Generated Code", border_style="green"))

    # Cleanup
    if os.path.exists("dummy_graph.py"):
        os.remove("dummy_graph.py")

if __name__ == "__main__":
    main()
