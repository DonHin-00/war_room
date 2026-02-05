#!/usr/bin/env python3
"""
Shim for backward compatibility.
Runs the RedAttacker agent from the new agents package.
"""
import sys
import os

# Ensure we can find the agents package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.red_brain import RedAttacker

if __name__ == "__main__":
    agent = RedAttacker()
    agent.run()
