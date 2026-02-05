# ACE-ES: Advanced Cyber Environment Emulation Suite

A high-fidelity Red vs. Blue cyber warfare emulation platform designed for Threat Intelligence training and automated defense validation.

## Architecture

ACE-ES operates as a multi-agent system utilizing real-world Threat Intelligence and active network emulation.

### Core Components

*   **Red Team (APT)**: `red_brain.py` / `red_tools.py`
    *   **Live Emulation**: Connects to *real* malicious C2 IPs (sourced from live feeds) using encrypted, authenticated HTTP channels.
    *   **Capabilities**: HTTP Beaconing, Domain Generation Algorithms (DGA), Poly-Persistence (Cron/Bashrc), and Data Exfiltration.
    *   **Security**: Encrypts all payloads (AES-GCM) to simulate secure malware channels.

*   **Blue Team (Hunter)**: `blue_brain.py` / `blue_tools.py`
    *   **Active Defense**: Monitors system processes (`/proc`) and network connections (`ss -tunap`).
    *   **Remediation**: Terminates threats and removes persistence artifacts in real-time.

*   **Threat Intelligence**: `threat_intel.py`
    *   Aggregates 16+ free, live feeds (Feodo Tracker, URLHaus, IPSum, etc.).
    *   Validates data (rejecting private/bogon IPs) and persists to SQLite.

*   **Malware Lab**: `lab_manager.py` / `evolution.py`
    *   **Breeding**: Uses Genetic Algorithms to breed polyglot (Python/Bash) "Synthetic Beacons" with Control Flow Flattening.
    *   **Export**: Exports artifacts in industry-standard **STIX 2.1** format for SIEM ingestion.

### Usage

**Deployment:**
```bash
./deploy_ace.sh
```
This script handles dependency checks, database initialization, intel fetching, and agent orchestration.

**Logging:**
All agent activities are logged to `logs/`. Artifacts (STIX bundles) are generated in the root directory.

**Safety:**
The system is designed for professional emulation. Red Team payloads are benign (randomized JSON) but the *behavior* (connections, files) is realistic. Use with caution in production networks as it generates traffic to known malicious IPs.
