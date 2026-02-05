# Swarm Architecture: Active Cyber War Emulation

This repository has evolved from a simple file scanner into a comprehensive Multi-Agent Swarm Simulation.

## Components

### 1. Agents (`agents/`)
- **BlueDefender (`blue_brain.py`):**
  - **Capabilities:** Process Hunting (`PROCESS_SCAN`), Data Loss Prevention (`DLP_SCAN`), Network Defense (`NETWORK_SCAN`), Integrity Checks.
  - **Innovation:** Uses "Drone" threads for parallel filesystem scanning (optimized `os.scandir`) and "BabyBrain" for pattern learning.
- **RedAttacker (`red_brain.py`):**
  - **Capabilities:** Active Payloads (`T1204`), Network Exfiltration (`T1048`), Ransomware (`T1486`), Masquerading (`T1036`).
  - **Innovation:** Communicates with a local C2 server via HTTP.
- **BotWAF (`bot_brain.py`):**
  - **Capabilities:** Reverse Proxy (Port 9000 -> 8081), Anomaly Detection (Burst/Slow Drip), Shadow Banning.
  - **Innovation:** Uses `Mirage` to generate high-fidelity deception content.
- **YellowSRE (`yellow_brain.py`):**
  - **Capabilities:** Infrastructure Management, Auto-Scaling, Vulnerable Service Hosting (Active RCE).
- **GreenIntegrator (`green_brain.py`):**
  - **Capabilities:** User Simulation (Traffic Generation), Business Document Creation.
- **APT_29 (`apt_brain.py`):**
  - **Capabilities:** State-Level Actor emulation (Low & Slow Exfil, Persistence).

### 2. Infrastructure (`tools/`)
- **C2 Server (`c2_server.py`):** HTTP Command & Control listener (Port 8888).
- **Orchestrator (`simulation_runner.py`):** Manages the lifecycle of all 7 agents.
- **Stress Test (`tests/stress_simulation.py`):** Validates stability under heavy load.

### 3. Shared Utilities (`utils.py`)
- **Security Primitives:** `luhn_verify` (Credit Cards), `calculate_entropy`.
- **Atomic I/O:** `safe_file_write`/`read` with `fcntl` locking.

## Running the Simulation
Execute the orchestrator to start the full swarm:
```bash
python3 simulation_runner.py
```

## Legacy Support
Root-level `blue_brain.py` and `red_brain.py` serve as shims to launch the new agent classes, ensuring backward compatibility.
