#!/usr/bin/env python3
import json
import os
import sys

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils

def export_graphviz():
    topo_file = config.TOPOLOGY_FILE
    if not os.path.exists(topo_file):
        print("No topology data found.")
        return

    try:
        topo = utils.safe_json_read(topo_file, {})
    except Exception as e:
        print(f"Error reading topology: {e}")
        return

    print("digraph SentinelNetwork {")
    print("  rankdir=LR;")
    print("  node [fontname=\"Arial\"];")

    # Red Nodes
    print("\n  subgraph cluster_red {")
    print("    label = \"Red Mesh\";")
    print("    style=filled; color=lightpink;")
    print("    node [style=filled,color=red];")
    for k, v in topo.items():
        if v['type'] == 'RED':
            genes = v.get('genes', {})
            label = f"{k[:4]}\\nJ:{genes.get('jitter',0):.1f}"
            print(f"    \"{k}\" [label=\"{label}\"];")
    print("  }")

    # Blue Nodes
    print("\n  subgraph cluster_blue {")
    print("    label = \"Blue Swarm\";")
    print("    style=filled; color=lightblue;")
    print("    node [style=filled,color=blue,fontcolor=white];")
    for k, v in topo.items():
        if v['type'] == 'BLUE':
            print(f"    \"{k}\" [label=\"{k[:4]}\"];")
    print("  }")

    # Edges
    print("\n  # Connections")
    for k, v in topo.items():
        peers = v.get('peers', [])
        for p in peers:
            if p == "SWARM": continue
            # Only draw if target exists or just draw it
            print(f"  \"{k}\" -> \"{p}\" [style=dotted];")

    print("}")

if __name__ == "__main__":
    export_graphviz()
