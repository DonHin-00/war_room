# Cognitive Cyber War Simulation (v1.0)

A next-generation adversarial simulation platform featuring autonomous AI agents (Red/Blue) operating in a 4-Layer Segregated SOC environment. The system utilizes Hierarchical Reinforcement Learning (HRL), Real Emulation (Process/Network), and rigorous security primitives.

## 🧠 Intelligence Engine

The core utilizes a **Hierarchical Q-Learning (HRL)** architecture (`ml_engine.py`):
*   **Strategic Layer:** Manages high-level Campaign Goals (e.g., `RECON` -> `ACCESS` -> `PERSISTENCE` -> `IMPACT`).
*   **Tactical Layer:** Executes specific MITRE ATT&CK techniques based on the active goal.
*   **Guaranteed Kill Chain:** Red Team adheres to a strict state machine, preventing out-of-sequence actions (e.g., Exfil before Access).

## 🏗️ Architecture

*   **Environment:** 4 Segregated Zones (`DMZ`, `USER`, `SERVER`, `CORE`) modeled on NIST standards.
*   **Agents:**
    *   **🔴 Red Team (APT):** Polymorphic malware, Process Injection (Real PID), C2 Exfiltration, Lateral Movement.
    *   **🔵 Blue Team (Zero-Trust):** Behavioral Analytics, HoneyTokens (Deception), Active Hunting, Immutable Backups.
*   **Infrastructure:**
    *   **Orchestrator:** `simulation_runner.py` manages the lifecycle and C2 servers.
    *   **C2 Server:** `tools/c2_server.py` handles real HTTP beacons and data exfiltration.
    *   **Watchdog:** `tools/watchdog.py` provides self-healing capabilities.

## ⚔️ Capabilities (Emulation)

### Red Team (Predator)
*   **T1041 Exfiltration:** Steals sensitive files (`passwords.txt`) and POSTs to C2.
*   **T1055 Process Injection:** Spawns actual ghost processes (`sleep`) to hide presence.
*   **T1000 Polymorphism:** Mutates payload signatures to evade static detection.
*   **T1486 Ransomware:** Encrypts high-value targets.

### Blue Team (Sentinel)
*   **Deception:** Deploys HoneyTokens (`aws_keys.json`) to lure attackers.
*   **Threat Hunting:** Scans process tables for anomalies (`real_pid`) and terminates threats.
*   **Resilience:** Atomic backups and automated recovery.

## 🚀 Usage

1.  **Start Simulation:**
    ```bash
    python3 simulation_runner.py --duration 60 --reset
    ```
    *This launches the C2 server, Watchdog, and Agents automatically.*

2.  **Monitor Operations:**
    *   **Red Logs:** `tail -f red.log`
    *   **Blue Logs:** `tail -f blue.log`
    *   **C2 Logs:** `tail -f c2_server.log`

3.  **Run Tests:**
    ```bash
    python3 tests/test_ops.py
    python3 benchmark.py
    ```

## 🛡️ Security

*   **Hardened I/O:** Atomic file writes with `fcntl` locking (`utils.safe_file_write`).
*   **Resource Limits:** strict `RLIMIT_AS` (RAM) and `RLIMIT_CPU` enforcement.
*   **Audit Logging:** Tamper-evident JSONL logging with hash chaining.

---
*Built for High-Fidelity Cyber Range Emulation.*
