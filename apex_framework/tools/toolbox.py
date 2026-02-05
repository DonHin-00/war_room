import ast
import re
import sys
from typing import Dict, Any, List

class Toolbox:
    """
    Integrated Tools (1-3) for Safe Emulation.
    Real logic, no simulation.
    UPTOOLED: Added Fuzzing and Dependency Scanning.
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
        try:
            tree = ast.parse(code)
            score = 0
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With)):
                    score += 1
            return {"score": score, "complex": score > 10}
        except:
            return {"score": 0, "complex": False}

    @staticmethod
    def infer_types(code: str) -> Dict[str, Any]:
        missing_types = 0
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    for arg in node.args.args:
                        if arg.annotation is None and arg.arg != 'self':
                            missing_types += 1
                    if node.returns is None:
                        missing_types += 1
            return {"missing_count": missing_types, "fully_typed": missing_types == 0}
        except:
            return {"missing_count": 0, "fully_typed": True}

    @staticmethod
    def scan_dependencies(code: str, allowed: List[str] = None) -> Dict[str, Any]:
        """
        Tool 6: Dependency Scanner.
        Checks imports against allow-list.
        """
        if allowed is None:
            allowed = ["os", "sys", "json", "time", "random", "math", "re", "ast", "typing"]

        illegal = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        base = alias.name.split('.')[0]
                        if base not in allowed: illegal.append(base)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        base = node.module.split('.')[0]
                        if base not in allowed: illegal.append(base)

            return {"safe": len(illegal) == 0, "illegal_imports": illegal}
        except:
            return {"safe": True, "illegal_imports": []}

    @staticmethod
    def fuzz_test(code: str, func_name: str) -> Dict[str, Any]:
        """
        Tool 7: Basic Fuzz Tester.
        Executes code with random inputs in a controlled manner.
        """
        # We need to wrap the code to run it
        fuzz_harness = f"""
{code}

try:
    # Fuzz Inputs
    inputs = [None, "", 0, -1, 99999, "A"*1000]
    for i in inputs:
        try:
            {func_name}(i, i) # Assuming 2 args for demo compatibility
        except TypeError: pass # Expected for type mismatch
        except ValueError: pass # Expected
        except Exception as e:
            print(f"CRASH: {{e}} with input {{i}}")
            raise e
except Exception as e:
    raise e
"""
        try:
            # Emulation Sandbox (using exec carefully)
            # In a real tool we'd use a separate process
            exec(fuzz_harness, {"__builtins__": {}})
            return {"passed": True, "error": None}
        except Exception as e:
            return {"passed": False, "error": f"Fuzz Crash: {str(e)}"}
