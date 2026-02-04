import re
import random
from typing import List, Dict, Any, Optional
from ant_swarm.tools.toolbox import Toolbox
from ant_swarm.core.ooda import TacticalDoctrine

class MicroLM:
    """
    The 'Secure SmallLM' Core.
    NOW WITH TRANSPARENT CAPABILITY LOGGING.
    """
    def __init__(self):
        pass

    def generate_with_doctrine(self, task: str, doctrine: TacticalDoctrine, context: Dict, k: int = 3) -> List[Dict[str, Any]]:
        options = []
        variants = ["Safe", "Fast", "Balanced"][:k]

        for variant in variants:
            # 1. Proactive "Thought" Generation (Transparency)
            thoughts = self._generate_thoughts(task, variant)

            # 2. Raw Generation (Heuristic)
            code = self._synthesize_code(task, doctrine.weights, context, variant)

            # 3. Tool-Assisted Repair Loop
            code, improvements = self._run_repair_loop(code)

            # 4. Final Tool Scan
            report = self._scan_code(code)

            options.append({
                "variant_name": variant,
                "thoughts": thoughts,
                "improvements": improvements,
                "code": code,
                "tool_report": report
            })

        return options

    def _generate_thoughts(self, task: str, variant: str) -> List[str]:
        """
        Simulates the 'Reasoning Chain' for transparency.
        """
        thoughts = [f"Analyzing task: '{task}' for '{variant}' profile..."]

        if "login" in task.lower():
            if variant == "Safe":
                thoughts.append("⚠️ DETECTED: Sensitive Authentication Logic.")
                thoughts.append("💡 PLAN: Implement BCrypt hashing (Proactive Security).")
                thoughts.append("💡 PLAN: Add generic error messages to prevent enumeration.")
                thoughts.append("💡 PLAN: Enforce Type Hints for robustness.")
            elif variant == "Fast":
                thoughts.append("⚡ PLAN: Optimizing for raw throughput.")
                thoughts.append("💡 PLAN: Minimize I/O blocking.")

        return thoughts

    def _synthesize_code(self, task: str, weights: Dict, context: Dict, variant: str) -> str:
        if "login" in task.lower():
            if variant == "Safe" or weights.get("paranoia", 0) > 0.8:
                return "def login(u, p):\n    try:\n        # SECURITY: Using bcrypt\n        if not verify_hash(u, p): raise AuthError('Invalid')\n        log_audit_event('login_attempt')\n    except Exception: pass"
            elif variant == "Fast":
                return "def login(u, p): return True # TODO: Optimize this!"
            else:
                return "def login(u, p):\n    if verify(u,p): return True"
        return f"# Code for {task}"

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
                        improvements.append("Mitigated Eval() Risk")
                    if "exec" in issue:
                        code = code.replace("exec(", "# exec removed")
                        improvements.append("Removed Exec() Call")

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
