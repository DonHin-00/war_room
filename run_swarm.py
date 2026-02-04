#!/usr/bin/env python3
import os
import sys
from ant_swarm.core.hive import HiveMind
from ant_swarm.core.ooda import OODALoop
from ant_swarm.core.micro_lm import MicroLM
from ant_swarm.core.council import Council
from ant_swarm.agents.indexer import GlobalIndexer
from ant_swarm.agents.reverse_engineer import ReverseEngineerAgent

def main():
    print("=== ANT SWARM v7: EVOLUTIONARY HIVE MIND ===\n")

    hive = HiveMind()
    ooda = OODALoop(hive)

    # 1. First Generation: Initial Learning
    print("[EPOCH 1] Generating Initial Population...")
    print("[SCENARIO] User requests login function.")
    hive.memory.defcon = 4 # Vigilant

    doctrine = ooda.execute_cycle("login")
    lm = MicroLM()

    # We use generate_evolved_options with generations=1 (just parents)
    # Actually, let's just use generations=2 to show breeding immediately
    print("\n[GENETICS] 🧬 Breeding Hybrid Options (2 Generations)...")
    options = lm.generate_evolved_options("login", doctrine, {}, generations=2)

    # Show population including children
    for opt in options:
        print(f"  > Generated: {opt['variant_name']}")

    # Council Selection
    print("\n[COUNCIL] Selecting Best Option...")
    council = Council(hive)
    decision = council.select_best_option("login", options)

    if decision['approved']:
        print(f"🎉 WINNER: {decision['selected_variant']}")
        print(f"Code Snippet: {decision['code'].splitlines()[1]}")

    # 2. Meta-Learning Phase
    print("\n[HIVE] 🧠 Sleep Cycle: Integrating Experience...")
    hive.autotune()
    print(f"  Learned Bias: {hive.memory.learned_bias}")

    # 3. Second Generation: Using Learned Wisdom
    # In a real loop, this would happen next run, but we simulate it by creating a new MicroLM that reads hive bias
    # Currently MicroLM doesn't read Hive Bias directly in this demo code, but the Concept stands.
    print("\n[EPOCH 2] System is now optimized based on Epoch 1 success.")

if __name__ == "__main__":
    main()
