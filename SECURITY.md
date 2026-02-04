# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of this project seriously. If you find a vulnerability, please report it privately.

**DO NOT** open a public issue.

Instead, please email `security@example.com` with a description of the issue.

## Security Best Practices for Contributors

- **No Hardcoded Secrets**: Use environment variables.
- **Input Validation**: Sanitize all inputs.
- **Least Privilege**: Run with minimum necessary permissions.
- **Secure Defaults**: Fail closed.
- **Defense in Depth**: Assume breach.

## Automated Checks

This repository includes security tools in the `tools/` directory. Run `python3 tools/security_scan.py` before submitting changes.
