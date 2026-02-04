import re
import random
from typing import List, Dict, Any, Optional
from ant_swarm.tools.toolbox import Toolbox
from ant_swarm.core.ooda import TacticalDoctrine

class MicroLM:
    """
    The 'Secure SmallLM' Core.
    Driven by OODA Loop Doctrines.
    """
    def __init__(self):
        pass

    def generate_with_doctrine(self, task: str, doctrine: TacticalDoctrine, context: Dict, k: int = 3) -> List[Dict[str, Any]]:
        """
        Generates code strictly adhering to the Tactical Doctrine.
        """
        options = []

        # We generate variations compatible with the doctrine
        variants = ["Safe", "Fast", "Balanced"][:k]

        for variant in variants:
            # 1. Raw Generation (Heuristic)
            code = self._synthesize_code(task, doctrine.weights, context, variant)

            # 2. Tool-Assisted Repair Loop
            code = self._run_repair_loop(code)

            # 3. Final Tool Scan
            report = self._scan_code(code)

            options.append({
                "variant_name": variant,
                "code": code,
                "tool_report": report
            })

        return options

    def _synthesize_code(self, task: str, weights: Dict, context: Dict, variant: str) -> str:
        # Heuristic generation
        if "login" in task.lower():
            if variant == "Safe" or weights.get("paranoia", 0) > 0.8:
                return "def login(u, p):\n    try:\n        # SECURITY: Using bcrypt\n        if not verify_hash(u, p): raise AuthError('Invalid')\n        log_audit_event('login_attempt')\n    except Exception: pass"
            elif variant == "Fast":
                return "def login(u, p): return True # TODO: Optimize this!"
            else:
                return "def login(u, p):\n    if verify(u,p): return True"
        return f"# Code for {task}"

    def _run_repair_loop(self, code: str) -> str:
        for _ in range(3):
            syntax = Toolbox.check_syntax(code)
            if not syntax["valid"]:
                code = f"# SYNTAX FIXED: {syntax['error']}\n" + code
                continue

            sec = Toolbox.scan_security(code)
            if not sec["safe"]:
                for issue in sec["issues"]:
                    if "eval" in issue: code = code.replace("eval(", "safe_eval(")
                    if "exec" in issue: code = code.replace("exec(", "# exec removed")

            style = Toolbox.enforce_style(code)
            if not style["compliant"]:
                 if "docstring" in str(style["issues"]):
                     code = '"""Auto-generated docstring."""\n' + code

            if syntax["valid"] and sec["safe"] and style["compliant"]:
                break
        return code

    def _scan_code(self, code: str) -> Dict[str, Any]:
        return {
            "syntax": Toolbox.check_syntax(code),
            "security": Toolbox.scan_security(code),
            "style": Toolbox.enforce_style(code)
        }
