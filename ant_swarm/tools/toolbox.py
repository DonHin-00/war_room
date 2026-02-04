import ast
import re
from typing import Dict, Any, List

class Toolbox:
    """
    Integrated Tools (1-3) for Safe Emulation.
    Real logic, no simulation.
    """

    @staticmethod
    def check_syntax(code: str) -> Dict[str, Any]:
        """
        Tool 1: Verifies Python syntax using AST.
        """
        try:
            ast.parse(code)
            return {"valid": True, "error": None}
        except SyntaxError as e:
            return {"valid": False, "error": f"Line {e.lineno}: {e.msg}"}
        except Exception as e:
            return {"valid": False, "error": str(e)}

    @staticmethod
    def scan_security(code: str) -> Dict[str, Any]:
        """
        Tool 2: Scans for vulnerabilities (Eval, Exec, etc).
        """
        patterns = [
            (r"eval\(", "Use of eval() detected."),
            (r"exec\(", "Use of exec() detected."),
            (r"subprocess\.call", "Unsafe subprocess call."),
            (r"base64\.b64decode", "Potential obfuscated payload."),
            (r"input\(", "Blocking input call detected.")
        ]

        issues = []
        for pat, msg in patterns:
            if re.search(pat, code):
                issues.append(msg)

        return {"safe": len(issues) == 0, "issues": issues}

    @staticmethod
    def enforce_style(code: str) -> Dict[str, Any]:
        """
        Tool 3: Checks basic PEP-8 (Line length, Docstrings).
        """
        issues = []
        lines = code.splitlines()

        # Check Line Length
        for i, line in enumerate(lines):
            if len(line) > 88: # Black default
                issues.append(f"Line {i+1} is too long ({len(line)} > 88 chars).")

        # Check Docstring (heuristic)
        if len(lines) > 5 and not ('"""' in code or "'''" in code):
            issues.append("Missing module/function docstrings.")

        return {"compliant": len(issues) == 0, "issues": issues}
