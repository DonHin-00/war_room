#!/usr/bin/env python3
"""
Evolution Engine
Simulates polymorphic mutation on Synthetic Beacon payloads.
Implements Functional Mutations: Obfuscation, Jitter, User-Agent Rotation.
"""

import ast
import random
import string
import os
import hashlib
import base64
import lab_config

class MutationEngine:
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
        "curl/7.68.0",
        "Wget/1.20.3 (linux-gnu)",
        "Python-urllib/3.8"
    ]

    def _random_var_name(self, length=6):
        return ''.join(random.choices(string.ascii_lowercase, k=length))

    def _obfuscate_string(self, code, target_string):
        """Replaces a string literal with a base64 decoded version."""
        if target_string not in code: return code

        encoded = base64.b64encode(target_string.encode()).decode()
        # Code injection: import base64 if not present (assumed present in base payload)
        # Replace the string literal with the decode logic
        replacement = f"base64.b64decode('{encoded}').decode()"
        return code.replace(f'"{target_string}"', replacement)

    def _modify_jitter(self, code):
        """Randomizes the sleep intervals."""
        new_min = random.randint(1, 10)
        new_max = new_min + random.randint(5, 20)

        code = code.replace("SLEEP_MIN = 5", f"SLEEP_MIN = {new_min}")
        code = code.replace("SLEEP_MAX = 10", f"SLEEP_MAX = {new_max}")
        return code

    def _rotate_user_agent(self, code):
        """Swaps the User-Agent string."""
        new_ua = random.choice(self.USER_AGENTS)
        # Find the current UA line? Or just regex replace?
        # Simple replace for the known base structure
        if 'USER_AGENT = "' in code:
            lines = code.splitlines()
            for i, line in enumerate(lines):
                if line.strip().startswith('USER_AGENT = "'):
                    lines[i] = f'USER_AGENT = "{new_ua}"'
                    break
            return "\n".join(lines)
        return code

    def _insert_junk(self, code):
        """Inserts junk calculation logic."""
        lines = code.splitlines()
        idx = random.randint(0, len(lines)-1)
        var = self._random_var_name()
        lines.insert(idx, f"{var} = {random.randint(1,100)} * {random.randint(1,100)}")
        return "\n".join(lines)

    def mutate(self, code):
        """Apply random mutations."""
        mutant = code

        # Functional Mutations
        if random.random() < 0.5:
            mutant = self._modify_jitter(mutant)

        if random.random() < 0.5:
            mutant = self._rotate_user_agent(mutant)

        # Obfuscation Mutations
        if random.random() < 0.3:
            # Try to obfuscate the C2 URL if it's there
            if "http://127.0.0.1:8080/beacon" in mutant:
                 mutant = self._obfuscate_string(mutant, "http://127.0.0.1:8080/beacon")

        # Structure Mutations
        if random.random() < 0.4:
            mutant = self._insert_junk(mutant)

        return mutant

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
        # print(f"[Lab] Running Generation {gen_id}...")

        for sample in self.population:
            # Mutate
            mutant = self.engine.mutate(sample)

            # Verify Fitness
            if self.engine.is_valid(mutant):
                new_pop.append(mutant)

                # Calculate Hash
                sha256 = hashlib.sha256(mutant.encode('utf-8')).hexdigest()
                self.hashes.append(sha256)
            else:
                new_pop.append(sample)

        self.population = new_pop

    def evolve(self):
        for i in range(lab_config.GENERATIONS):
            self.run_generation(i+1)
        return self.hashes

if __name__ == "__main__":
    lab = EvolutionLab()
    hashes = lab.evolve()
    print(f"Generated {len(set(hashes))} unique variant hashes.")
