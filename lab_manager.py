#!/usr/bin/env python3
"""
Lab Manager
Orchestrates the Malware Evolution Lab and Export pipelines.
"""

import argparse
import sys
from evolution import EvolutionLab
from lab_export import HashReplayEngine, FeedExporter

class LabManager:
    def __init__(self):
        self.evolver = EvolutionLab()
        self.replay = HashReplayEngine()
        self.exporter = FeedExporter()

    def run_evolution_cycle(self, generations=5):
        print(f"[LabManager] Starting Evolution Cycle ({generations} gens)...")
        hashes = self.evolver.evolve()
        print(f"[LabManager] Evolution complete. Generated {len(hashes)} unique variants.")
        return hashes

    def run_full_pipeline(self):
        print("[LabManager] Running Full Pipeline...")

        # 1. Breed Synthetic Beacons
        self.exporter.generate_and_publish()

        # 2. Replay Real Hashes
        self.replay.generate_artifacts()

        print("[LabManager] Pipeline Complete. Check export files.")

if __name__ == "__main__":
    manager = LabManager()
    manager.run_full_pipeline()
