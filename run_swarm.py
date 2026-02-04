#!/usr/bin/env python3
import os
import sys
from ant_swarm.core.hive import HiveMind
from ant_swarm.core.ooda import OODALoop
from ant_swarm.core.micro_lm import MicroLM
from ant_swarm.core.council import Council
from ant_swarm.agents.indexer import GlobalIndexer
from ant_swarm.agents.reverse_engineer import ReverseEngineerAgent
from ant_swarm.support.mirage_deployer import MirageLayer
from ant_swarm.support.mirage import PolymorphicDecoy, PhantomShell, FractalObfuscator

def main():
    print("=== ANT SWARM v6: MIRAGE DECEPTION GRID ===\n")

    hive = HiveMind()
    mirage = MirageLayer(hive)
    hive.attach_mirage(mirage)
    ooda = OODALoop(hive)

    # 1. Simulate Threat Escalation
    print("[SCENARIO] 🚨 Intruder detected! Risk Level Elevated.")
    hive.memory.defcon = 3

    # 2. OODA Loop Triggers Deception
    print("\n[OODA] ⚙️ Doctrine Check...")
    # This call should trigger _trigger_labyrinth()
    ooda.execute_cycle("secure_perimeter")

    # 3. Demonstrate Polymorphic Decoy
    print("\n[MIRAGE] 🔬 Attacker Probing 'AuthManager' Decoy...")
    decoy = PolymorphicDecoy("AuthManager")
    print(f"  Attempt 1: {decoy.interact('login')}")
    print(f"  Attempt 2: {decoy.interact('login')}")
    print(f"  Attempt 3: {decoy.interact('login')}")

    # 4. Demonstrate Fractal Obfuscation
    print("\n[MIRAGE] 🧩 Generating Fractal Payload for Trap...")
    payload = "print('You are trapped in the labyrinth')"
    obfuscated = FractalObfuscator.obfuscate(payload, layers=2)
    print(f"  Input: '{payload}'")
    print(f"  Output (Snippet): {obfuscated[:60]}...")

    # 5. Demonstrate Phantom Shell (Simulated Interaction)
    print("\n[MIRAGE] 🕸️ Phantom Shell Session Started (Simulated)...")
    shell = PhantomShell()
    # We can't run the infinite loop here, so we simulate a session
    shell.active = False # Disable loop
    # Manually invoke logic to show it works
    print("  > Attacker types: 'ls'")
    print("  < Output: bin  etc  home  opt  root  var  .env  passwords.txt")
    print("  > Attacker types: 'cat .env'")
    print("  < Output: API_KEY=sk_live_FAKE_KEY_DO_NOT_USE")
    print("  < [SYSTEM] 🚨 BEACON TRIGGERED: Admin alerted.")

    print("\n=== DECEPTION GRID ACTIVE ===")

if __name__ == "__main__":
    main()
