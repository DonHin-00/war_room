# Sentinel Security Guidelines 🛡️

This repository is protected by the Sentinel protocol. All agents and contributors must adhere to the following security standards.

## Core Directives

1.  **Trust Nothing, Verify Everything**: Validate all inputs, check file paths, and verify permissions.
2.  **Defense in Depth**: Implement multiple layers of security.
3.  **Fail Securely**: Errors should not leak sensitive information or leave the system in an insecure state.

## Coding Standards

### Python
-   **File I/O**:
    -   Do not use `/tmp` for shared state. Use `./simulation_data/`.
    -   Check for symlinks before deleting (`os.path.islink`).
    -   Use `os.open` with `O_CREAT | O_EXCL` for atomic file creation.
-   **Logging**:
    -   Use the `logging` module, not `print`.
    -   Log security events (access violations, errors).
    -   Do not log sensitive data (passwords, keys).
-   **Secrets**:
    -   Use `secrets` module for cryptographic randomness and tokens.
    -   Never hardcode secrets. Use environment variables.

## Pre-Commit Checks

Before submitting code, run:
```bash
python3 tools/security_scan.py
python3 tools/verify_permissions.py
```

## Critical Vulnerabilities to Watch
-   Symlink races (TOCTOU)
-   Path traversal
-   Code injection (eval/exec)
-   Insecure permissions
