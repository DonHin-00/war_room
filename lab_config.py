# Lab Configuration

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LAB_DIR = os.path.join(BASE_DIR, "lab_samples")
EXPORT_FILE = os.path.join(BASE_DIR, "feed_export.json")

# Genetic Algorithm Settings
POPULATION_SIZE = 20
GENERATIONS = 10
MUTATION_RATE = 0.3

# Base benign payload to "evolve"
# This is a harmless math script. The goal is to mutate its structure
# without breaking its logic, simulating polymorphic evasion.
BASE_PAYLOAD = """
def calculate(a, b):
    # Perform calculation
    x = a + b
    y = a * b
    return x + y

if __name__ == "__main__":
    print(calculate(10, 20))
"""
