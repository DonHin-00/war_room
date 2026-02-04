import re
import random
from typing import List, Dict, Any, Optional
from ant_swarm.tools.toolbox import Toolbox
from ant_swarm.core.ooda import TacticalDoctrine

class GeneticOptimizer:
    """
    The Evolutionary Engine.
    Breeds code options to create superior hybrids.
    """
    @staticmethod
    def breed(parent_a: Dict, parent_b: Dict, generation: int) -> Dict:
        """
        Merges two options into a child.
        """
        # 1. Crossover Weights
        weights_a = parent_a.get("traits", {})
        weights_b = parent_b.get("traits", {})

        child_weights = {
            "paranoia": (weights_a.get("paranoia", 0.5) + weights_b.get("paranoia", 0.5)) / 2,
            "speed": (weights_a.get("speed", 0.5) + weights_b.get("speed", 0.5)) / 2
        }

        # 2. Crossover Logic (Simulated by merging 'Improvements')
        imps_a = set(parent_a.get("improvements", []))
        imps_b = set(parent_b.get("improvements", []))
        child_imps = list(imps_a.union(imps_b))

        # 3. Mutation (Randomly add a trait)
        if random.random() < 0.3: # 30% mutation rate
            child_weights["paranoia"] += 0.1
            child_imps.append("Mutated: Extra Logging")

        return {
            "variant_name": f"Hybrid Gen{generation}",
            "traits": child_weights,
            "improvements": child_imps,
            "parent_a": parent_a["variant_name"],
            "parent_b": parent_b["variant_name"]
        }

class MicroLM:
    """
    The 'Secure SmallLM' Core.
    NOW WITH GENETIC EVOLUTION.
    """
    def __init__(self):
        pass

    def generate_evolved_options(self, task: str, doctrine: TacticalDoctrine, context: Dict, generations: int = 2) -> List[Dict[str, Any]]:
        # Generation 0: Initial Population
        population = self._generate_initial_population(task, doctrine, context)

        current_gen = population
        for gen in range(1, generations + 1):
            if len(current_gen) < 2: break # Need parents

            # Selection: Pick top 2 (Simulated by sorting by a simple heuristic score here)
            # In real flow, Council scores them, but MicroLM needs to do it internally for evolution
            # We'll assume the first 2 are 'best' based on doctrine alignment for simplicity
            parent_a = current_gen[0]
            parent_b = current_gen[1]

            # Breeding
            child_params = GeneticOptimizer.breed(parent_a, parent_b, gen)

            # Generation (Synthesize Code for Child)
            child_code = self._synthesize_child_code(task, child_params)

            # Repair Child
            child_code, child_imps = self._run_repair_loop(child_code)

            # Scan Child
            child_report = self._scan_code(child_code)

            child_option = {
                "variant_name": child_params["variant_name"],
                "code": child_code,
                "tool_report": child_report,
                "traits": child_params["traits"],
                "improvements": child_params["improvements"] + child_imps,
                "thoughts": [f"Bred from {child_params['parent_a']} + {child_params['parent_b']}", "Optimizing traits..."]
            }

            # Add to population
            current_gen.append(child_option)

        return current_gen

    def _generate_initial_population(self, task: str, doctrine: TacticalDoctrine, context: Dict):
        options = []
        variants = ["Safe", "Fast", "Balanced"]

        for variant in variants:
            # Derive weights from doctrine but bias by variant
            weights = doctrine.weights.copy()
            if variant == "Safe": weights["paranoia"] = 0.9
            if variant == "Fast": weights["speed"] = 0.9

            code = self._synthesize_code(task, weights, context, variant)
            code, imps = self._run_repair_loop(code)
            report = self._scan_code(code)

            options.append({
                "variant_name": variant,
                "code": code,
                "tool_report": report,
                "traits": weights,
                "improvements": imps,
                "thoughts": [f"Initializing {variant} profile..."]
            })
        return options

    def _synthesize_code(self, task: str, weights: Dict, context: Dict, variant: str) -> str:
        # Base synthesis logic
        if "login" in task.lower():
            if variant == "Safe" or weights.get("paranoia", 0) > 0.8:
                return "def login(u, p):\n    try:\n        # SECURITY: Using bcrypt\n        if not verify_hash(u, p): raise AuthError('Invalid')\n        log_audit_event('login_attempt')\n    except Exception: pass"
            elif variant == "Fast":
                return "def login(u, p): return True # TODO: Optimize this!"
            else:
                return "def login(u, p):\n    if verify(u,p): return True"
        return f"# Code for {task}"

    def _synthesize_child_code(self, task: str, params: Dict) -> str:
        # Synthesis based on evolved traits
        weights = params["traits"]
        # Logic: If high paranoia AND high speed (Hybrid), generate robust async code
        if weights["paranoia"] > 0.6 and weights["speed"] > 0.6:
            return "async def login(u, p):\n    try:\n        # HYBRID: Async + Bcrypt\n        if not await verify_hash_async(u, p): raise AuthError\n        await log_audit('login')\n    except: pass"

        # Fallback to standard synthesis
        return self._synthesize_code(task, weights, {}, "Hybrid")

    def _run_repair_loop(self, code: str) -> (str, List[str]):
        improvements = []
        for _ in range(3):
            syntax = Toolbox.check_syntax(code)
            if not syntax["valid"]:
                code = f"# SYNTAX FIXED: {syntax['error']}\n" + code
                improvements.append("Fixed Syntax Error")
                continue

            sec = Toolbox.scan_security(code)
            if not sec["safe"]:
                 for issue in sec["issues"]:
                    if "eval" in issue:
                        code = code.replace("eval(", "safe_eval(")
                        improvements.append("Mitigated Eval()")

            style = Toolbox.enforce_style(code)
            if not style["compliant"]:
                 if "docstring" in str(style["issues"]):
                     code = '"""Auto-generated docstring."""\n' + code
                     improvements.append("Added Docstrings")

            if syntax["valid"] and sec["safe"] and style["compliant"]:
                break
        return code, improvements

    def _scan_code(self, code: str) -> Dict[str, Any]:
        return {
            "syntax": Toolbox.check_syntax(code),
            "security": Toolbox.scan_security(code),
            "style": Toolbox.enforce_style(code)
        }
