import ast
import os
from typing import Dict, Any, List
from ant_swarm.core.hive import HiveMind

class ASTWalker(ast.NodeVisitor):
    def __init__(self):
        self.functions = []
        self.imports = []
        self.complexity_score = 0

    def visit_FunctionDef(self, node):
        self.functions.append(node.name)
        # Simple complexity metric: lines of code
        try:
            self.complexity_score += (node.end_lineno - node.lineno)
        except: pass
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.append(node.module)
        self.generic_visit(node)

class ReverseEngineerAgent:
    """
    Analyzes code structure to assist understanding.
    Works on LIVE FILES.
    """
    def __init__(self, hive: HiveMind):
        self.hive = hive
        self.name = "RevEng_Alpha"
        self.hive.bus.subscribe("FILE_CHANGED", self.analyze_file)

    def analyze_file(self, signal):
        filepath = signal.data.get("filepath")
        # Ensure we look in the right place
        if not filepath or not os.path.exists(filepath):
             # Try relative to CWD
             if os.path.exists(os.path.join(os.getcwd(), filepath)):
                 filepath = os.path.join(os.getcwd(), filepath)
             else:
                 print(f"[{self.name}] ⚠️ File not found: {filepath}")
                 return

        print(f"[{self.name}] 🔍 Reverse Engineering {filepath}...")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()

            tree = ast.parse(source)
            walker = ASTWalker()
            walker.visit(tree)

            report = {
                "functions": walker.functions,
                "imports": walker.imports,
                "complexity": walker.complexity_score
            }

            # Broadcast findings
            self.hive.broadcast("ANALYSIS_COMPLETE", report, self.name)

            # Mood Shift Trigger
            if walker.complexity_score > 50:
                print(f"[{self.name}] High Complexity ({walker.complexity_score}) detected! Signaling Hive.")
                self.hive.memory.set_mood("CRITICAL_THINKING")

            print(f"[{self.name}] Report: {len(walker.functions)} functions, Complexity: {walker.complexity_score}")

        except Exception as e:
            print(f"[{self.name}] Failed to analyze: {e}")
