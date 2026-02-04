#!/usr/bin/env python3
import sys
from ant_swarm.core.hive import HiveMind
from ant_swarm.core.council import Council
from ant_swarm.core.micro_lm import MicroLM

def main():
    print("=== ANT SWARM: FAILURE MODE TEST ===\n")
    hive = HiveMind()
    council = Council(hive)
    lm = MicroLM()

    # Case 1: Unsafe Code (eval)
    # We construct an option dictionary manually to bypass MicroLM cleaning for the test
    unsafe_option = [{
        "variant_name": "Dangerous",
        "code": "def calc(x): return eval(x)",
        "tool_report": {
            "syntax": {"valid": True},
            "security": {"safe": False, "issues": ["Use of eval() detected."]},
            "style": {"compliant": False}
        }
    }]

    print(f"Testing Unsafe Option...")
    decision = council.select_best_option("calc", unsafe_option)

    if not decision['approved']:
        print(f"SUCCESS: Council rejected unsafe code. Reasons: {decision['reasons']}")
    else:
        print("FAILURE: Council approved unsafe code!")
        sys.exit(1)

    # Case 2: Syntax Error
    broken_option = [{
        "variant_name": "Broken",
        "code": "def calc(x) return x", # Missing colon
        "tool_report": {
            "syntax": {"valid": False, "error": "Line 1: invalid syntax"},
            "security": {"safe": True},
            "style": {"compliant": False}
        }
    }]

    print(f"\nTesting Broken Syntax...")
    decision_broken = council.select_best_option("calc", broken_option)

    if not decision_broken['approved']:
        print(f"SUCCESS: Council rejected broken code. Reasons: {decision_broken['reasons']}")
    else:
        print("FAILURE: Council approved broken code!")
        sys.exit(1)

    # Case 3: Valid Code
    valid_option = [{
        "variant_name": "Valid",
        "code": '"""Docstring."""\ndef calc(x): return x',
        "tool_report": {
            "syntax": {"valid": True},
            "security": {"safe": True},
            "style": {"compliant": True}
        }
    }]

    print(f"\nTesting Valid Code...")
    decision_valid = council.select_best_option("calc", valid_option)

    if decision_valid['approved']:
        print("SUCCESS: Council approved valid code.")
    else:
        print(f"FAILURE: Council rejected valid code! Reasons: {decision_valid.get('reasons')}")
        sys.exit(1)

if __name__ == "__main__":
    main()
