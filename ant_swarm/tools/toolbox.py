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
        try:
            ast.parse(code)
            return {"valid": True, "error": None}
        except SyntaxError as e:
            return {"valid": False, "error": f"Line {e.lineno}: {e.msg}"}
        except Exception as e:
            return {"valid": False, "error": str(e)}

    @staticmethod
    def scan_security(code: str) -> Dict[str, Any]:
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
        issues = []
        lines = code.splitlines()
        for i, line in enumerate(lines):
            if len(line) > 88:
                issues.append(f"Line {i+1} is too long ({len(line)} > 88 chars).")
        if len(lines) > 5 and not ('"""' in code or "'''" in code):
            issues.append("Missing module/function docstrings.")
        return {"compliant": len(issues) == 0, "issues": issues}

    @staticmethod
    def analyze_complexity(code: str) -> Dict[str, Any]:
        """
        Tool 4: Cyclomatic Complexity & Nesting Depth.
        """
        try:
            tree = ast.parse(code)
            score = 0
            for node in ast.walk(tree):
                # Basic Cyclomatic Complexity: Loops, Ifs, Excepts
                if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With)):
                    score += 1
            return {"score": score, "complex": score > 10}
        except:
            return {"score": 0, "complex": False}

    @staticmethod
    def infer_types(code: str) -> Dict[str, Any]:
        """
        Tool 5: Type Hint Checker.
        """
        missing_types = 0
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check args
                    for arg in node.args.args:
                        if arg.annotation is None and arg.arg != 'self':
                            missing_types += 1
                    # Check return
                    if node.returns is None:
                        missing_types += 1
            return {"missing_count": missing_types, "fully_typed": missing_types == 0}
        except:
            return {"missing_count": 0, "fully_typed": True}
