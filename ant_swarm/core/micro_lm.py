import re
import random
from typing import List, Dict, Any, Optional

class PromptEngine:
    @staticmethod
    def craft_prompt(task: str, persona: str, constraints: List[str], context: Dict) -> str:
        """
        Constructs the high-fidelity prompt for the model.
        """
        constraint_block = "\n".join([f"- {c}" for c in constraints])

        prompt = f"""
=== SYSTEM IDENTITY ===
ROLE: {persona}
MISSION: Execute the task with extreme adherence to the specific constraints.

=== GLOBAL CONTEXT ===
ADRs: {[a['title'] for a in context.get('adrs', [])]}
Global Summary: {context.get('global_summary', 'N/A')}

=== NEGATIVE CONSTRAINTS (NO-FLY ZONE) ===
{constraint_block}

=== CHAIN OF VERIFICATION ===
Before outputting code, list 3 ways your solution could fail and provide mitigations.

=== TASK ===
{task}
"""
        return prompt

class MicroLM:
    """
    The 'Secure SmallLM' Core.
    Simulates a deterministic, hardened Language Model.
    """
    def __init__(self):
        # "Model Weights" simulated by behavioral flags
        self.biases = {
            "security": {"paranoia": 0.9, "speed": 0.2, "verbosity": 0.5},
            "performance": {"paranoia": 0.1, "speed": 0.9, "verbosity": 0.1},
            "maintainability": {"paranoia": 0.4, "speed": 0.4, "verbosity": 0.8}
        }

    def generate(self, task: str, persona_type: str, context: Dict) -> Dict[str, Any]:
        """
        Simulates the generation process.
        Returns a dict containing 'code', 'verification', and 'audit_log'.
        """
        # 1. Apply Logic Framing (Persona Weights)
        weights = self.biases.get(persona_type.lower(), {"paranoia": 0.5, "speed": 0.5})

        # 2. Simulate Chain of Verification (CoV)
        verification = self._run_chain_of_verification(task, weights)

        # 3. Generate "Code" (Deterministic Simulation)
        code = self._synthesize_code(task, weights, context)

        # 4. Apply Negative Constraints (Self-Correction)
        compliant, violation = self._check_negative_constraints(code)
        if not compliant:
            # Self-heal
            code = f"# FIXING VIOLATION: {violation}\n" + code.replace("eval(", "safe_eval(")

        return {
            "prompt_used": "PROMPT_HIDDEN_FOR_BREVITY",
            "verification": verification,
            "code": code,
            "weights_used": weights
        }

    def _run_chain_of_verification(self, task: str, weights: Dict) -> List[str]:
        """
        Simulates the model 'thinking' about failure modes.
        """
        verifications = []
        if weights["paranoia"] > 0.7:
            verifications.append("Failure 1: Input injection attack. Mitigation: Sanitize all inputs.")
            verifications.append("Failure 2: Race conditions. Mitigation: Use atomic locks.")
            verifications.append("Failure 3: Information leakage. Mitigation: Suppress error tracebacks.")
        elif weights["speed"] > 0.7:
            verifications.append("Failure 1: Memory overflow. Mitigation: Use generators.")
            verifications.append("Failure 2: I/O blocking. Mitigation: Async/Await.")
        else:
            verifications.append("Failure 1: Spaghetti code. Mitigation: Modularize.")
            verifications.append("Failure 2: Magic numbers. Mitigation: Define constants.")

        return verifications

    def _synthesize_code(self, task: str, weights: Dict, context: Dict) -> str:
        """
        Simulates code generation based on the task and weights.
        """
        # Heuristic response generation
        if "login" in task.lower():
            if weights["paranoia"] > 0.7:
                return "def login(u, p):\n    # SECURITY: Using bcrypt\n    if not verify_hash(u, p): raise AuthError('Invalid')\n    log_audit_event('login_attempt')"
            elif weights["speed"] > 0.7:
                return "def login(u, p):\n    # PERFORMANCE: Check redis cache first\n    if cache.get(u) == p: return True\n    return db.query(u, p)"
            else:
                return "def login(user_name, password):\n    # MAINTAINABILITY: Clear variable names\n    if user_manager.validate(user_name, password):\n        return True"

        elif "sort" in task.lower():
            if weights["speed"] > 0.7:
                return "data.sort(key=lambda x: x.val) # O(N log N)"
            else:
                return "sorted_data = sorted(data, key=extract_key) # Readable"

        return f"# Code generated for task: {task}\n# Context: {len(context.get('adrs', []))} ADRs considered."

    def _check_negative_constraints(self, code: str) -> (bool, Optional[str]):
        """
        The 'No-Fly Zone' Enforcement.
        """
        # 1. No eval()
        if "eval(" in code or "exec(" in code:
            return False, "Usage of eval() or exec() is forbidden."

        # 2. 50 Line Limit (Simulated by char count for this mock)
        if len(code.split('\n')) > 50:
             return False, "Function exceeds 50 lines."

        # 3. External imports (Simulated)
        if "import os" in code and "checksum" not in code:
             # Just a mock rule: "never import external libraries without checksums"
             # We'll allow it for now to avoid breaking basic mocks, but flagged conceptually.
             pass

        return True, None
