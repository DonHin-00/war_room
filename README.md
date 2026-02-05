# ⚔️ AI Cyber War Emulation Platform

A modular, self-learning cyber warfare simulation environment. It pits an **Autonomous Red Team** (Attacker) against an **AI-Powered Blue Team** (Defender) in a live-fire exercise against a **Smart Adaptive Target**.

## 🚀 Key Features

*   **Smart Adaptive Target:** A real HTTP server (Port 5000) that dynamically learns from attacks (Hot-Patching) and self-heals artifacts.
*   **AI-Powered WAF:** Hybrid defense engine combining Regex Signatures with a **Naïve Bayes Classifier** to detect obfuscated payloads (SQLi, XSS, RCE).
*   **Autonomous Red Team:** Uses Q-Learning to optimize attack strategies, rotating User-Agents and using "Low and Slow" evasion tactics.
*   **Web Dashboard:** Real-time visualization of the War State (DEFCON Level), Attack Logs, and Agent Performance on Port 8080.
*   **Dockerized:** Full stack deployment via Docker Compose.

## 🛠️ Installation & Usage

### Option 1: Docker (Recommended)

1.  **Deploy the Stack:**
    ```bash
    ./deploy.sh docker
    ```
2.  **Access Interfaces:**
    *   **Dashboard:** [http://localhost:8080](http://localhost:8080)
    *   **Vulnerable Target:** [http://localhost:5000](http://localhost:5000)

### Option 2: Local Python

1.  **Run Locally:**
    ```bash
    ./deploy.sh local
    ```
    (This creates a virtual environment, installs dependencies, and runs the simulation).

## 🧠 Architecture

*   **`simulation_runner.py`**: The orchestrator. Launches Red/Blue brains, Target, and Dashboard.
*   **`red_brain.py`**: The Attacker. Uses Reinforcement Learning to choose techniques from MITRE ATT&CK.
*   **`blue_brain.py`**: The Defender. Runs the Hybrid WAF and manages Incident Response.
*   **`smart_target.py`**: The Battleground. A web server that evolves based on incoming threats.
*   **`ai_defense.py`**: The ML Engine. Provides probability-based threat detection.
*   **`web_dashboard.py`**: The UI. Flask-based monitoring center.

## 🛡️ Safety Note

This tool is for **educational and research purposes only**. All attacks are performed against `localhost` within the isolated environment. The "malware" generated is simulated and safe.
