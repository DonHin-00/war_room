#!/usr/bin/env python3
"""
Evolution Engine
Simulates polymorphic mutation on benign code samples.
"""

import ast
import random
import string
import os
import hashlib
import lab_config

class MutationEngine:
    def __init__(self):
        pass

    def _random_var_name(self, length=5):
        return ''.join(random.choices(string.ascii_lowercase, k=length))

    def _insert_noop(self, code):
        """Inserts a no-op line (comment or useless var assignment)."""
        lines = code.splitlines()
        idx = random.randint(0, len(lines)-1)

        noop_type = random.choice(['comment', 'var'])
        if noop_type == 'comment':
            lines.insert(idx, f"# {self._random_var_name(10)}")
        else:
            lines.insert(idx, f"{self._random_var_name()} = 0")

        return "\n".join(lines)

    def _rename_vars(self, code):
        """Simple find-replace for variable names (fragile but works for this simple payload)."""
        # Specific to the known base payload structure
        new_a = self._random_var_name()
        new_b = self._random_var_name()
        code = code.replace("a", new_a).replace("b", new_b)
        return code

    def mutate(self, code):
        """Apply random mutations."""
        if random.random() < 0.5:
            code = self._insert_noop(code)
        if random.random() < 0.3:
            code = self._rename_vars(code)
        return code

    def is_valid(self, code):
        """Checks if code compiles."""
        try:
            compile(code, '<string>', 'exec')
            return True
        except:
            return False

class EvolutionLab:
    def __init__(self):
        self.engine = MutationEngine()
        self.population = [lab_config.BASE_PAYLOAD] * lab_config.POPULATION_SIZE
        self.hashes = []

    def run_generation(self, gen_id):
        new_pop = []
        print(f"[Lab] Running Generation {gen_id}...")

        for sample in self.population:
            # Mutate
            mutant = self.engine.mutate(sample)

            # Verify Fitness (Valid Python)
            if self.engine.is_valid(mutant):
                new_pop.append(mutant)

                # Calculate Hash
                sha256 = hashlib.sha256(mutant.encode('utf-8')).hexdigest()
                self.hashes.append(sha256)
            else:
                new_pop.append(sample) # Keep parent if mutant dies

        self.population = new_pop

    def evolve(self):
        for i in range(lab_config.GENERATIONS):
            self.run_generation(i+1)

        return self.hashes

if __name__ == "__main__":
    lab = EvolutionLab()
    hashes = lab.evolve()
    print(f"Generated {len(hashes)} unique variants.")
    print(f"Sample Hash: {hashes[0]}")
