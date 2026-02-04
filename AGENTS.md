# Sentinel Security Guidelines 🛡️

This repository is protected by the Sentinel protocol. All agents and contributors must adhere to the following security standards.

## Core Directives

1.  **Trust Nothing, Verify Everything**: Validate all inputs, check file paths, and verify permissions.
2.  **Defense in Depth**: Implement multiple layers of security.
3.  **Fail Securely**: Errors should not leak sensitive information or leave the system in an insecure state.

## Coding Standards

### Python
-   **File I/O**:
    -   Do not use `/tmp` for shared state. Use `config.SIMULATION_DATA_DIR`.
    -   Use `utils.safe_json_read` and `utils.safe_json_write` for state files (prevents race conditions).
    -   Use `utils.secure_create` for atomic file creation.
    -   Check for symlinks before deleting (`os.path.islink`).
-   **Logging**:
    -   Use `utils.setup_logging`. Do not use `print`.
    -   Log security events (access violations, errors).
-   **Configuration**:
    -   Use `config.py` for all constants and paths.
    -   Do not hardcode paths.
-   **Secrets**:
    -   Use `secrets` module for cryptographic randomness and tokens.
    -   Never hardcode secrets. Use environment variables.

## Pre-Commit Checks

Before submitting code, run:
```bash
python3 tools/pre_commit.py
```

## Critical Vulnerabilities to Watch
-   Symlink races (TOCTOU)
-   Path traversal
-   Code injection (eval/exec)
-   Insecure permissions
-   Race conditions on shared state

## Tools
-   `tools/security_scan.py`: Static analysis for common vulnerabilities.
-   `tools/verify_permissions.py`: Check file/directory permissions.
-   `tools/analyze_logs.py`: View simulation metrics.
-   `tools/check_env.py`: Verify environment readiness.
-   `tools/clean.py`: Safe cleanup.
