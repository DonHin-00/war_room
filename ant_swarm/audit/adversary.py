import re
from typing import List, Dict, Any

class AdversarialAuditor:
    """
    The 'Adversarial Insider'.
    Trained to find backdoors and logic flaws.
    """
    def __init__(self):
        self.signatures = [
            (r"eval\(", "Unsafe Execution (eval)"),
            (r"exec\(", "Unsafe Execution (exec)"),
            (r"base64", "Potential Obfuscation"),
            (r"subprocess", "Shell Injection Risk"),
            (r"pickle", "Insecure Deserialization")
        ]

    def audit_code(self, code: str) -> Dict[str, Any]:
        """
        Scans the code for specific adversarial patterns.
        """
        print("\n[ADVERSARY] 🕵️ Starting Forensic Audit...")
        findings = []

        for pattern, risk in self.signatures:
            if re.search(pattern, code):
                findings.append(f"CRITICAL: Found {risk}")

        # Simulated Logic Probe
        if "password" in code and "hash" not in code:
             findings.append("HIGH: Password handling without hashing detected.")

        passed = len(findings) == 0

        if passed:
            print("[ADVERSARY] Audit PASSED. No obvious backdoors found.")
        else:
            print(f"[ADVERSARY] Audit FAILED. {len(findings)} issues detected.")
            for f in findings:
                print(f"  - {f}")

        return {
            "passed": passed,
            "findings": findings
        }
