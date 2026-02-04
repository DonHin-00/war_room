#!/usr/bin/env python3
"""
Lab Export
Simulates publishing signatures to a threat feed.
Exports HASHES ONLY.
"""

import json
import time
import os
import lab_config
from evolution import EvolutionLab

class FeedExporter:
    def __init__(self):
        self.lab = EvolutionLab()
        self.export_file = lab_config.EXPORT_FILE

    def generate_and_publish(self):
        print("[FeedExporter] Initializing Malware Evolution Lab...")
        print("[FeedExporter] Breeding samples...")

        # Run the GA
        hashes = self.lab.evolve()
        unique_hashes = list(set(hashes))

        # Prepare Export Data
        feed_data = {
            "timestamp": time.time(),
            "source": "Internal_Evolution_Lab",
            "type": "SHA256_Signatures",
            "count": len(unique_hashes),
            "signatures": unique_hashes
        }

        # Write to "Feed"
        with open(self.export_file, "w") as f:
            json.dump(feed_data, f, indent=4)

        print(f"[FeedExporter] Published {len(unique_hashes)} signatures to {self.export_file}")
        return len(unique_hashes)

if __name__ == "__main__":
    exporter = FeedExporter()
    exporter.generate_and_publish()
