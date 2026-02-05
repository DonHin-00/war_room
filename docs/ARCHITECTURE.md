# System Architecture

## Overview
The AI Cyber War Simulation uses a **multi-agent swarm architecture** orchestrated by a central runner. Agents communicate via shared state files (Blackboard Pattern) and direct interaction with the file system (`battlefield/`).

## Core Components

### 1. Orchestration (`simulation_runner.py`)
-   **Role:** Process Manager.
-   **Function:** Launches all agent scripts (`agents/*.py`) as independent subprocesses.
-   **Monitoring:** Restarts crashed agents (via `tools/watchdog.py` logic, integrated here).

### 2. Configuration (`config.py`)
-   **Role:** Single Source of Truth.
-   **Content:**
    -   File paths (Centralized to avoid hardcoding).
    -   RL Hyperparameters (Alpha, Gamma, Epsilon).
    -   Reward Definitions (Blue vs Red).
    -   Simulation Constraints (Max alerts, resource limits).

### 3. Machine Learning Engine (`ml_engine.py`)
-   **Role:** Shared Intelligence.
-   **Classes:**
    -   `DoubleQLearner`: Implements Double Q-Learning to stabilize training. Handles atomic I/O for Q-Tables.
    -   `SafetyShield`: Rule-based filter to prevent agents from taking catastrophic actions (e.g., `rm -rf /`).
    -   `PrioritizedReplayBuffer`: (Stub) For future Experience Replay implementation.

### 4. Utilities (`utils/`)
-   **`core.py`:**
    -   `atomic_json_io`: Thread-safe JSON reading/writing using `fcntl` (File Locking).
    -   `AuditLogger`: centralized logging to `audit.jsonl`.
    -   `limit_resources`: Enforces RAM quotas using `resource` module.
-   **`trace_logger.py`:** Decorator for detailed error tracing.

## Agent Roles

| Agent | File | Role | Key Tactics |
| :--- | :--- | :--- | :--- |
| **Blue** | `blue_brain.py` | Defender | Signature/Heuristic Scan, Threat Hunting, Tar Pits, Decoys. |
| **Red** | `red_brain.py` | Attacker | Recon, Obfuscation, Rootkits, Persistence, Exfiltration (Kill Chain). |
| **Purple** | `purple_brain.py` | Balancer | Injects "Game Day" scenarios, detects anomalies/bursts. |
| **Green** | `green_brain.py` | Healer | Auto-patches vulnerabilities, restores backups. |
| **Yellow** | `yellow_brain.py` | Builder | Deploys vulnerable apps, simulates IT operations. |
| **Orange** | `orange_brain.py` | Facilitator | Facilitates Tabletop exercises. |
| **Sentinel** | `sentinel_brain.py` | User Ally | Cleanup, log rotation, system health monitoring. |
| **ForceMultiplier** | `force_multiplier_brain.py` | Support | Dynamic reinforcement (bonus actions). |
| **Daemon** | `daemon_brain.py` | Stress | Generates noise/flood to stress test the system. |

## Data Flow

1.  **Shared State (`war_state.json`):**
    -   Agents read/write global state (Alert Level, Campaign Phase).
    -   Locked via `fcntl` to prevent race conditions.

2.  **Battlefield (`battlefield/`):**
    -   Red writes "Malware" (files) here.
    -   Blue scans and deletes files here.
    -   **Safety:** Isolated directory to prevent damage to the host OS.

3.  **Audit Log (`audit.jsonl`):**
    -   All critical actions (Kill, Exfil, Persist) are appended here.
    -   Consumed by the Dashboard.

## Extension Guide

To add a new agent:
1.  Create `agents/new_agent_brain.py`.
2.  Import `setup_logging` and `atomic_json_io` from `utils`.
3.  Register in `simulation_runner.py` inside the `AGENTS` dict.
