import ast
import os
import networkx as nx
from typing import Dict, Any, List
from rich.console import Console
from ant_swarm.core.hive import HiveMind

console = Console()

class TaintAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.sources = set()
        self.sinks = set()
        self.tainted_vars = set()
        self.taint_detected = False

    def visit_Assign(self, node):
        # 1. Identify Sources (input, os.environ)
        # Simplified Heuristic: If right side calls 'input' or uses 'environ'
        is_source = False
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
            if node.value.func.id in ['input']:
                is_source = True

        # 2. Propagate Taint
        if is_source:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.tainted_vars.add(target.id)

        self.generic_visit(node)

    def visit_Call(self, node):
        # 3. Identify Sinks (eval, exec, subprocess)
        if isinstance(node.func, ast.Name):
            if node.func.id in ['eval', 'exec', 'system', 'popen']:
                # Check args for tainted vars
                for arg in node.args:
                    if isinstance(arg, ast.Name) and arg.id in self.tainted_vars:
                        self.taint_detected = True
                        console.print(f"[red]⚠️ TAINT FLOW DETECTED: {arg.id} -> {node.func.id}[/]")
        self.generic_visit(node)

class ASTWalker(ast.NodeVisitor):
    def __init__(self):
        self.functions = []
        self.imports = []
        self.calls = []
        self.current_func = None
        self.complexity_score = 0

    def visit_FunctionDef(self, node):
        self.functions.append(node.name)
        self.current_func = node.name
        try:
            self.complexity_score += (node.end_lineno - node.lineno)
        except: pass
        self.generic_visit(node)
        self.current_func = None

    def visit_Call(self, node):
        if self.current_func and isinstance(node.func, ast.Name):
            self.calls.append((self.current_func, node.func.id))
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
    Analyzes code structure using NetworkX Graph Analysis.
    UPTOOLED: Taint Analysis.
    """
    def __init__(self, hive: HiveMind):
        self.hive = hive
        self.name = "RevEng_Alpha"
        self.hive.bus.subscribe("FILE_CHANGED", self.analyze_file)

    def analyze_file(self, signal):
        filepath = signal.data.get("filepath")
        if not filepath or not os.path.exists(filepath): return

        console.print(f"[{self.name}] 🔍 Reverse Engineering [bold]{filepath}[/]...")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()

            tree = ast.parse(source)
            walker = ASTWalker()
            walker.visit(tree)

            # Taint Analysis
            taint = TaintAnalyzer()
            taint.visit(tree)

            # Build Graph
            G = nx.DiGraph()
            G.add_nodes_from(walker.functions)
            G.add_edges_from(walker.calls)

            if len(G) > 0:
                centrality = nx.degree_centrality(G)
                most_critical = max(centrality, key=centrality.get)
            else:
                most_critical = "None"

            report = {
                "functions": walker.functions,
                "imports": walker.imports,
                "complexity": walker.complexity_score,
                "critical_node": most_critical,
                "taint_detected": taint.taint_detected
            }

            self.hive.broadcast("ANALYSIS_COMPLETE", report, self.name)

            if walker.complexity_score > 50:
                console.print(f"[{self.name}] ⚠️ High Complexity ({walker.complexity_score}). Critical Node: {most_critical}")
                self.hive.memory.set_mood("CRITICAL_THINKING")

        except Exception as e:
            console.print(f"[{self.name}] Failed to analyze: {e}")
