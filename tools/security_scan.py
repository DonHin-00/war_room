#!/usr/bin/env python3
import os
import re
import sys

# Patterns to search for
PATTERNS = {
    "Hardcoded Secret": r"(?i)(password|secret|key|token)\s*=\s*['\"][^'\"]+['\"]",
    "Insecure /tmp Usage": r"/tmp/",
    "Dangerous Eval": r"eval\(",
    "Dangerous Exec": r"exec\(",
    "Shell Injection": r"shell=True",
    "Print Debugging": r"print\(",
    "Bare Except": r"except\s*:",
}

def scan_file(filepath):
    """Scans a single file for security patterns."""
    issues = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            for name, pattern in PATTERNS.items():
                if re.search(pattern, line):
                    # Ignore harmless prints in this script
                    if name == "Print Debugging" and "tools/security_scan.py" in filepath:
                        continue
                    issues.append(f"[{name}] {filepath}:{i} - {line.strip()}")
    return issues

def main():
    print("🛡️ Sentinel Security Scan Initiated...")
    found_issues = False

    # Files to ignore
    ignore_files = ["AGENTS.md", "SECURITY.md"]

    for root, _, files in os.walk("."):
        if ".git" in root or "__pycache__" in root or "tools" in root:
            continue

        for file in files:
            if not file.endswith(".py"):
                continue

            filepath = os.path.join(root, file)
            if any(ignored in filepath for ignored in ignore_files):
                continue

            issues = scan_file(filepath)
            if issues:
                found_issues = True
                print(f"\nIssues found in {filepath}:")
                for issue in issues:
                    print(f"  ❌ {issue}")

    if found_issues:
        print("\n⚠️  Security Scan Failed: Vulnerabilities detected.")
        sys.exit(1)
    else:
        print("\n✅ Security Scan Passed: No obvious vulnerabilities found.")
        sys.exit(0)

if __name__ == "__main__":
    main()
