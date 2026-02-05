# AI Cyber War Simulation

A multi-agent reinforcement learning simulation where **Blue Team** (Defense) and **Red Team** (Offense) AIs battle for control of a virtual network.

## 🚀 Overview

This project simulates a realistic cyber warfare environment using autonomous agents. The agents utilize **Double Q-Learning** to evolve their strategies over time.

-   **Blue Team:** Protects the system using NIST SP 800-61 incident response guidelines. Uses heuristic scanning, threat hunting, and active defenses (Tar Pits, Decoys).
-   **Red Team:** Executes APT campaigns based on the MITRE ATT&CK Matrix (Recon -> Obfuscation -> Rootkits -> Persistence -> Exfiltration).
-   **Purple Team:** Acts as the integrator and game master, managing the state and injecting scenarios.

## 📂 Architecture

The project is modularized for scalability:

-   `agents/`: Individual agent logic (Blue, Red, Green, Yellow, Orange, Purple, Daemon, Sentinel, ForceMultiplier).
-   `ml_engine.py`: Shared Reinforcement Learning core (Double Q-Learning, Replay Buffers, Safety Shields).
-   `utils/`: Hardened utility primitives (Atomic I/O with file locking, Audit Logging).
-   `config.py`: Centralized configuration for rewards, file paths, and simulation constraints.
-   `simulation_runner.py`: The main orchestrator that launches and manages the swarm.
-   `tools/`: Analysis and visualization tools (`visualize_threats.py`).
-   `docs/`: Detailed architectural documentation (`ARCHITECTURE.md`).

## 🛠️ Usage

### Local Installation
```bash
pip install -r requirements.txt
python3 simulation_runner.py
```

### 🐳 Docker Deployment
The recommended way to run the simulation is via Docker, which isolates the "battlefield" from your host system.

1.  **Build and Run:**
    ```bash
    docker-compose up --build -d
    ```
2.  **View Logs:**
    ```bash
    docker-compose logs -f
    ```
3.  **Access Data:**
    Runtime data is persisted in the local `simulation_data/` directory.

### Dashboard
To view the real-time battle status (works with both Local and Docker if mapped):
```bash
python3 tools/visualize_threats.py
```

## 🧠 Features

### Machine Learning
-   **Double Q-Learning:** Reduces maximization bias for more stable learning.
-   **Safety Shields:** Heuristic layers that prevent agents from performing catastrophic or non-sensical actions.
-   **Context-Awareness:** Agents adapt strategies based on the current "Campaign Phase" (e.g., blocking network traffic during Exfiltration).

### Tactics Implemented
-   **Red:** `T1046` (Recon), `T1027` (Obfuscation), `T1003` (Rootkits), `T1547` (Persistence), `T1041` (Exfiltration).
-   **Blue:** Signature Scanning, Heuristic Analysis, Threat Hunting (IOC matching), Deception (Honeypots), Active Defense (Tar Pits).

## 📊 Monitoring
The system logs all critical events to `simulation_data/audit.jsonl`. You can analyze this log or view it live in the dashboard.

## 🛡️ Safety
This is a **simulation**. All malware actions (file creation, network traffic) are emulated safely within the `battlefield/` directory. No real malicious code is executed against the host system outside of this sandbox.
