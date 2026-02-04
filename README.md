# AI Cyber War Simulation (Live Ops)

A realistic adversarial simulation ("Live Ops") between autonomous Red (Attacker) and Blue (Defender) agents.

## 🏗️ Architecture

*   **Orchestrator:** `simulation_runner.py` manages the lifecycle of the war.
*   **Watchdog:** `tools/watchdog.py` ensures agents remain active (Self-Healing).
*   **Configuration:** `config.py` defines all tactics, paths, and limits.
*   **Core:** `utils.py` provides hardened primitives (Atomic I/O, Resource Limits, Audit Logging).

## ⚔️ Tactics

### 🔴 Red Team (Predator) - Emulation Mode
*   **Ransomware:** Encrypts files (`T1486`).
*   **Process Injection:** Creates ghost PIDs (`T1055`).
*   **Anti-Forensics:** Wipes audit logs (`T1070`).
*   **C2:** Beacons to command server (`T1071`).
*   **Evasion:** Uses Polymorphism and Masquerading (`T1036`, `T1027`).

### 🔵 Blue Team (Sentinel) - Detection Mode
*   **Hunting:** Scans for ghost processes and beacons.
*   **Active Defense:** Deploys Tar Pits (FIFOs) and Logic Bombs.
*   **Resilience:** Backups critical data and restores if Ransomware is detected.
*   **Integrity:** Verifies file checksums.

## 🚀 Usage

1.  **Check Environment:**
    ```bash
    python3 tools/check_env.py
    ```

2.  **Start Simulation:**
    ```bash
    python3 simulation_runner.py --duration 60
    ```

3.  **View Dashboard (Live):**
    ```bash
    python3 tools/visualize_threats.py
    ```

4.  **Inject Chaos:**
    ```bash
    python3 tools/fuzz_simulation.py
    ```

5.  **Clean Up:**
    ```bash
    python3 tools/clean.py
    ```

## 📂 Structure

*   `battlefield/`: The isolated sandbox where the war happens.
*   `simulation_data/`: Stores state, logs, and incident reports.
*   `incidents/`: JSON reports of mitigated threats.
*   `audit.jsonl`: Tamper-evident operation log.
