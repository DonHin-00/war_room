# Instructions for AI Agents

Welcome, Agent. This repository contains a complex, multi-agent Cyber War Simulation.

## 🗺️ Orientation
-   **Architecture:** Read `docs/ARCHITECTURE.md` first. It explains the "Swarm" design, data flow, and agent roles.
-   **Entry Point:** `simulation_runner.py` is the orchestrator. Do not run individual agent scripts directly; they rely on the environment setup by the runner.
-   **Configuration:** `config.py` contains all file paths and hyperparameters. Edit this instead of hardcoding values.

## ⚠️ Core Directives
1.  **Safety First:** All file destruction/creation must happen inside the `battlefield/` directory (or `simulation_data/`). Never touch system files.
2.  **No "Sim-Only" Shortcuts:** Do not simulate actions by just writing to a log file. If Red Team "Exfiltrates," it must actually read a file, encrypt it, and move it to a staging area.
3.  **Atomic I/O:** When reading/writing shared JSON files (like `war_state.json`), you **MUST** use `utils.atomic_json_io` or `utils.atomic_json_update`. These use `fcntl` locking to prevent race conditions.
4.  **Performance:**
    -   Cache Q-Tables in memory. Do not read them from disk on every loop iteration.
    -   Use `utils.limit_resources` to keep memory usage low.

## 🧪 Verification
Before submitting changes:
1.  Run the full simulation: `python3 simulation_runner.py`.
2.  Check the dashboard: `python3 tools/visualize_threats.py`.
3.  Run stress tests: `python3 tests/stress_parallel.py`.

## 📂 File Structure
-   `agents/`: Brains of the swarm.
-   `ml_engine.py`: Shared RL logic (Double Q-Learning).
-   `utils/`: Hardened I/O and logging.
-   `simulation_data/`: Runtime state (Ignored by git).

Good luck.
