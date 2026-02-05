#!/usr/bin/env python3
"""
Shim for backward compatibility.
Runs the BlueDefender agent from the new agents package.
"""
import sys
import os

# Ensure we can find the agents package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.blue_brain import BlueDefender

if __name__ == "__main__":
    agent = BlueDefender()
    agent.run()
