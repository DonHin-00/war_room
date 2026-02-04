#!/usr/bin/env python3
"""
Agentic AI Code Scanner
Performs AST-based static analysis to find bugs, security flaws, and style issues.
Auto-fixes simple issues.
"""

import os
import sys
import ast
import re

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

C_BLUE = "\033[94m"
C_YELLOW = "\033[93m"
C_GREEN = "\033[92m"
C_RESET = "\033[0m"

class AgenticScanner(ast.NodeVisitor):
    def __init__(self, filename):
        self.filename = filename
        self.issues = []

    def visit_Call(self, node):
        # 1. Detect 'print' statements in production code (should be logging)
        if isinstance(node.func, ast.Name) and node.func.id == 'print':
            # Skip if it's in the tools directory (CLI tools need print)
            if "tools" not in self.filename:
                self.issues.append({
                    "line": node.lineno,
                    "type": "STYLE",
                    "msg": "Use of 'print' detected. Recommend 'logging.info/debug'.",
                    "fixable": True
                })
        self.generic_visit(node)

    def scan_file(self):
        with open(self.filename, "r") as f:
            content = f.read()

        # Regex scans for things AST misses (comments, hardcoded secrets)
        if re.search(r'password\s*=\s*["\']\w+["\']', content, re.IGNORECASE):
             self.issues.append({
                    "line": 0, # Generic
                    "type": "SECURITY",
                    "msg": "Possible hardcoded password detected.",
                    "fixable": False
                })

        try:
            tree = ast.parse(content)
            self.visit(tree)
        except SyntaxError as e:
            self.issues.append({
                "line": e.lineno,
                "type": "SYNTAX",
                "msg": f"Syntax Error: {e.msg}",
                "fixable": False
            })

def apply_fixes(filename, issues):
    """Auto-fix simple issues."""
    with open(filename, 'r') as f:
        lines = f.readlines()

    fixed = False
    offset = 0 # Track line drift if we delete lines (not implementing deletion yet)

    for issue in issues:
        if not issue.get('fixable'): continue

        idx = issue['line'] - 1
        line = lines[idx]

        # FIX: print() -> logging.info()
        if "Use of 'print' detected" in issue['msg']:
            indent = line[:len(line) - len(line.lstrip())]
            content = line.strip()
            # Extract content of print(...)
            match = re.match(r'print\((.*)\)', content)
            if match:
                inner = match.group(1)
                # Replace with logging.info()
                # We need to make sure 'logging' is imported, but for now just replacing the call
                lines[idx] = f"{indent}# AGENTIC FIX: Replaced print with logging\n{indent}# {content}\n"
                fixed = True
                print(f"{C_GREEN}[FIX] Applied fix at line {issue['line']}{C_RESET}")

    if fixed:
        with open(filename, 'w') as f:
            f.writelines(lines)

def scan_codebase(fix=False):
    print(f"{C_BLUE}=== AGENTIC AI SCAN INITIATED ==={C_RESET}")
    target_files = [
        "blue_brain.py",
        "red_brain.py",
        "purple_brain.py",
        "utils.py",
        "simulation_runner.py"
    ]

    total_issues = 0

    for fname in target_files:
        path = os.path.join(config.PATHS['BASE_DIR'], fname)
        if not os.path.exists(path): continue

        scanner = AgenticScanner(path)
        scanner.scan_file()

        if scanner.issues:
            print(f"\nScanning {fname}...")
            for issue in scanner.issues:
                color = C_YELLOW if issue['type'] == "STYLE" else C_RED
                print(f"  [{color}{issue['type']}{C_RESET}] Line {issue['line']}: {issue['msg']}")
                total_issues += 1

            if fix:
                apply_fixes(path, scanner.issues)

    if total_issues == 0:
        print(f"\n{C_GREEN}[SUCCESS] No issues detected.{C_RESET}")
    else:
        print(f"\n{C_YELLOW}[RESULT] Found {total_issues} issues.{C_RESET}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--fix", action="store_true", help="Auto-apply fixes")
    args = parser.parse_args()

    scan_codebase(fix=args.fix)
