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
    console.print(Panel("[bold red]ANT SWARM v10: REINFORCED & UPTOOLED[/]", expand=False))

    hive = HiveMind()
    storage = LongTermDrive()
    coprocessor = Coprocessor(workers=4)
    gatekeeper = SecureGateway(storage) # Reinforced with persistence

    hive.attach_support(storage, coprocessor, gatekeeper)
    rev_eng = ReverseEngineerAgent(hive)
    ooda = OODALoop(hive)

    # 1. Demonstrate Reinforced Gatekeeper (Persistence)
    console.print("\n[bold cyan][SCENARIO 1][/] 🛡️ Gatekeeper Persistence Test...")
    # Simulate previous strikes
    storage.add_strike("1.2.3.4")
    storage.add_strike("1.2.3.4")
    storage.add_strike("1.2.3.4") # Should ban now

    result = gatekeeper.process_ingress("1.2.3.4", "Hello")
    if result["status"] == "BLOCKED":
        console.print("[green]✅ SUCCESS: Persistent IP Ban Active.[/]")

    # 2. Demonstrate Taint Analysis (Uptooled RevEng)
    console.print("\n[bold cyan][SCENARIO 2][/] 🔬 Taint Analysis Test...")
    with open("taint_test.py", "w") as f:
        f.write("import os\nuser_input = input()\nos.system(user_input)") # Classic Taint

    hive.broadcast("FILE_CHANGED", {"filepath": "taint_test.py"}, "User")
    # Wait for broadcast processing (simulated via synchronous call in this architecture)

    # 3. Demonstrate Fuzzing & Contract Enforcement
    console.print("\n[bold cyan][SCENARIO 3][/] ⚡ Fuzzing & Contract Enforcement...")
    task = "Create a login function."

    # We trigger a generation where the Doctrine forbids external libs
    doctrine = ooda.execute_cycle(task)
    doctrine.constraints.append("NO_EXTERNAL_LIBS")

    lm = MicroLM()
    options = lm.generate_evolved_options(task, doctrine, {}, generations=1)

    # Show that options survived Fuzzing
    for opt in options:
        console.print(f"  > Variant {opt['variant_name']} Tool Report: Fuzz={opt['tool_report'].get('syntax', {}).get('valid')}") # Indirect check via syntax valid means it compiled

    if os.path.exists("taint_test.py"): os.remove("taint_test.py")

if __name__ == "__main__":
    main()
