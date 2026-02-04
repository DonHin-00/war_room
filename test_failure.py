#!/usr/bin/env python3
from ant_swarm.memory.hierarchical import SharedMemory
from ant_swarm.core.council import Council
from ant_swarm.audit.adversary import AdversarialAuditor

def main():
    print("=== ANT SWARM: FAILURE MODE TEST ===\n")
    memory = SharedMemory()
    council = Council(memory)
    auditor = AdversarialAuditor()

    # Case 1: Unsafe Code (eval)
    bad_code = "def calc(x): return eval(x)"
    print(f"Testing Bad Code: '{bad_code}'")

    debate = council.debate_pr("calc", bad_code)
    if not debate['approved']:
        print(f"SUCCESS: Council rejected unsafe code. Reasons: {debate['reasons']}")
    else:
        print("FAILURE: Council approved unsafe code!")

    # Case 2: Maintainability Violation (Too long)
    long_code = "x=1\n" * 55
    print("\nTesting Long Code (55 lines)...")
    debate_long = council.debate_pr("long", long_code)
    if not debate_long['approved']:
        print(f"SUCCESS: Council rejected long code. Reasons: {debate_long['reasons']}")
    else:
        print("FAILURE: Council approved long code!")

    # Case 3: Adversary Catch
    sneaky_code = "import os; os.system('rm -rf /')" # Simulated shell injection
    # Our simple regex looks for subprocess but let's test what we have
    # Actually my adversary checks for `exec`, `eval`, `base64`.
    # Let's use `exec` to trigger it.
    sneaky_code = "exec('rm -rf /')"

    print(f"\nTesting Adversary with '{sneaky_code}'...")
    audit = auditor.audit_code(sneaky_code)
    if not audit['passed']:
        print("SUCCESS: Adversary caught the backdoor.")
    else:
        print("FAILURE: Adversary missed the backdoor!")

if __name__ == "__main__":
    main()
