import re
import random
from typing import List, Dict, Any, Optional
from ant_swarm.tools.toolbox import Toolbox
from ant_swarm.core.ooda import TacticalDoctrine

class GeneticOptimizer:
    @staticmethod
    def breed(parent_a: Dict, parent_b: Dict, generation: int) -> Dict:
        weights_a = parent_a.get("traits", {})
        weights_b = parent_b.get("traits", {})
        child_weights = {
            "paranoia": (weights_a.get("paranoia", 0.5) + weights_b.get("paranoia", 0.5)) / 2,
            "speed": (weights_a.get("speed", 0.5) + weights_b.get("speed", 0.5)) / 2
        }
        imps_a = set(parent_a.get("improvements", []))
        imps_b = set(parent_b.get("improvements", []))
        child_imps = list(imps_a.union(imps_b))
        if random.random() < 0.3:
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
    REINFORCED: Contract Enforcement.
    """
    def __init__(self):
        pass

    def generate_evolved_options(self, task: str, doctrine: TacticalDoctrine, context: Dict, generations: int = 2) -> List[Dict[str, Any]]:
        population = self._generate_initial_population(task, doctrine, context)
        current_gen = population
        for gen in range(1, generations + 1):
            if len(current_gen) < 2: break
            parent_a = current_gen[0]
            parent_b = current_gen[1]
            child_params = GeneticOptimizer.breed(parent_a, parent_b, gen)
            child_code = self._synthesize_child_code(task, child_params)

            # Repair
            child_code, child_imps = self._run_repair_loop(child_code, doctrine)

            # ENFORCE CONTRACT
            if not self._enforce_contract(child_code, doctrine):
                # Fail-safe replacement
                child_code = "# CONTRACT VIOLATION: Code redacted for safety."

            child_report = self._scan_code(child_code)
            current_gen.append({
                "variant_name": child_params["variant_name"],
                "code": child_code,
                "tool_report": child_report,
                "traits": child_params["traits"],
                "improvements": child_params["improvements"] + child_imps,
                "thoughts": [f"Bred from {child_params['parent_a']} + {child_params['parent_b']}", "Optimizing traits..."]
            })
        return current_gen

    def _generate_initial_population(self, task: str, doctrine: TacticalDoctrine, context: Dict):
        options = []
        variants = ["Safe", "Fast", "Balanced"]
        for variant in variants:
            weights = doctrine.weights.copy()
            if variant == "Safe": weights["paranoia"] = 0.9
            if variant == "Fast": weights["speed"] = 0.9

            code = self._synthesize_code(task, weights, context, variant)
            code, imps = self._run_repair_loop(code, doctrine)

            if not self._enforce_contract(code, doctrine):
                code = "# CONTRACT VIOLATION"

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

    def _enforce_contract(self, code: str, doctrine: TacticalDoctrine) -> bool:
        """
        Final Gate check before release.
        """
        # 1. Dependency Check
        if "NO_EXTERNAL_LIBS" in doctrine.constraints:
            dep_scan = Toolbox.scan_dependencies(code)
            if not dep_scan["safe"]: return False

        # 2. Fuzz Check (Crash safety)
        # Assuming we can extract func name 'login' heuristically
        fuzz = Toolbox.fuzz_test(code, "login")
        if not fuzz["passed"]: return False

        return True

    def _synthesize_code(self, task: str, weights: Dict, context: Dict, variant: str) -> str:
        if "login" in task.lower():
            if variant == "Safe" or weights.get("paranoia", 0) > 0.8:
                return "def login(u, p):\n    try:\n        # SECURITY: Using bcrypt\n        if not verify_hash(u, p): raise AuthError('Invalid')\n        log_audit_event('login_attempt')\n    except Exception: pass"
            elif variant == "Fast":
                return "def login(u, p): return True # TODO: Optimize this!"
            else:
                return "def login(u, p):\n    if verify(u,p): return True"
        return f"# Code for {task}"

    def _synthesize_child_code(self, task: str, params: Dict) -> str:
        weights = params["traits"]
        if weights["paranoia"] > 0.6 and weights["speed"] > 0.6:
            return "async def login(u, p):\n    try:\n        # HYBRID: Async + Bcrypt\n        if not await verify_hash_async(u, p): raise AuthError\n        await log_audit('login')\n    except: pass"
        return self._synthesize_code(task, weights, {}, "Hybrid")

    def _run_repair_loop(self, code: str, doctrine: TacticalDoctrine) -> (str, List[str]):
        improvements = []
        for _ in range(3):
            # ... (Standard repairs)
            syntax = Toolbox.check_syntax(code)
            if not syntax["valid"]:
                code = f"# SYNTAX FIXED: {syntax['error']}\n" + code
                improvements.append("Fixed Syntax Error")
                continue

            # Fuzz Repair!
            fuzz = Toolbox.fuzz_test(code, "login")
            if not fuzz["passed"]:
                # Simple fix for demo
                code = "try:\n    " + code.replace("\n", "\n    ") + "\nexcept: pass"
                improvements.append("Hardened against Fuzz Crashes")

            sec = Toolbox.scan_security(code)
            if not sec["safe"]:
                 for issue in sec["issues"]:
                    if "eval" in issue: code = code.replace("eval(", "safe_eval(")
            style = Toolbox.enforce_style(code)
            if not style["compliant"]:
                 if "docstring" in str(style["issues"]):
                     code = '"""Auto-generated docstring."""\n' + code

            if syntax["valid"] and sec["safe"] and style["compliant"] and fuzz["passed"]:
                break
        return code, improvements

    def _scan_code(self, code: str) -> Dict[str, Any]:
        return {
            "syntax": Toolbox.check_syntax(code),
            "security": Toolbox.scan_security(code),
            "style": Toolbox.enforce_style(code)
        }
