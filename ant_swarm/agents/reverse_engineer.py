import ast
import os
import networkx as nx
from typing import Dict, Any, List
from rich.console import Console
from ant_swarm.core.hive import HiveMind

console = Console()

class ASTWalker(ast.NodeVisitor):
    def __init__(self):
        self.functions = []
        self.imports = []
        self.calls = [] # (caller, callee)
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

            # Build Graph
            G = nx.DiGraph()
            G.add_nodes_from(walker.functions)
            G.add_edges_from(walker.calls)

            # Calculate Centrality (Critical Infrastructure)
            if len(G) > 0:
                centrality = nx.degree_centrality(G)
                most_critical = max(centrality, key=centrality.get)
            else:
                most_critical = "None"

            report = {
                "functions": walker.functions,
                "imports": walker.imports,
                "complexity": walker.complexity_score,
                "critical_node": most_critical
            }

            # Broadcast findings
            self.hive.broadcast("ANALYSIS_COMPLETE", report, self.name)

            if walker.complexity_score > 50:
                console.print(f"[{self.name}] ⚠️ High Complexity ({walker.complexity_score}). Critical Node: {most_critical}")
                self.hive.memory.set_mood("CRITICAL_THINKING")

        except Exception as e:
            console.print(f"[{self.name}] Failed to analyze: {e}")
