# Sentinel: Adversarial Cyber War Emulation

**Sentinel** is an autonomous, adversarial penetration testing and cyber warfare emulation framework. It utilizes a "Rainbow Team" of AI-driven agents to simulate a realistic, evolving cyber conflict environment. The system is designed to "keep it smart" by employing Reinforcement Learning (Q-Learning) and dynamic feedback loops that adapt to the adversary's tactics.

## 🚀 Architecture: The Rainbow Team

Sentinel orchestrates five specialized autonomous agents, each mimicking a specific role in a modern DevSecOps/Cyber environment:

### 🔴 Red Team (The Adversary)
*   **Role:** Advanced Persistent Threat (APT) & Pentester.
*   **Capabilities:**
    *   **C2 Beaconing:** Establishes covert communication channels.
    *   **Malware Deployment:** Polymorphic ransomware and rootkits.
    *   **Spearphishing (T1204):** Deploys realistic "bait" files to trick users.
    *   **Exfiltration (T1048):** Simulates data theft via alternative protocols (DNS Tunneling).
*   **AI:** Uses Q-Learning to optimize attack chains based on success rates and detection avoidance.

### 🔵 Blue Team (The Defender)
*   **Role:** Security Operations Center (SOC) & Incident Response.
*   **Capabilities:**
    *   **Active Defense:** Network scanning (`ss`) and Process hunting (`pgrep`).
    *   **Deep Inspection:** Entropy analysis (O(N)) and Magic Byte verification.
    *   **Heuristics:** Detection of anomaly patterns and unauthorized file modifications (FIM).
*   **AI:** Adapts defensive posture (Alert Levels) and learns signatures of successful attacks.

### 🟡 Sysadmin / SRE (The Builders)
*   **Role:** Site Reliability Engineers & End Users.
*   **Behavior:**
    *   Builds functional HTTP services (`app_*.py`).
    *   **User Simulation:** Occasionally executes "interesting" files, creating a realistic attack surface for Phishing.
    *   **Dynamic Security:** Toggles between writing "Vulnerable" vs. "Secure" code based on organizational urgency (controlled by Threat Intel).

### 🟢 SecOps (Integration)
*   **Role:** Integration & Hardening.
*   **Capabilities:**
    *   **Hot Patching:** Detects active vulnerabilities in SRE services and applies live patches.
    *   **Logging:** Injects instrumentation for better observability.
    *   **Trace Logging:** robustly captures and logs runtime errors.

### 🟠 Threat Intelligence (Governance)
*   **Role:** Threat Intelligence & Strategy.
*   **Capabilities:**
    *   **Feedback Loop:** Analyzes audit logs for successful Red Team attacks.
    *   **Policy Enforcement:** Updates `coding_standards.json` to enforce stricter development practices when threats are high, directly influencing Sysadmin behavior.

---

## 🧠 Keeping It Smart: AI & Learning

Sentinel is not just a randomizer; it learns.

*   **Reinforcement Learning (RL):** Both Red and Blue teams utilize Q-Tables to store state-action values. They learn which tactics yield the highest Rewards (Impact vs. Mitigation) and adjust their strategies over time.
*   **Adaptive Environment:**
    *   High attack success -> Orange Team increases Urgency -> Yellow Team writes Secure Code -> Red Team must pivot to advanced tactics.
    *   Blue Team learns file signatures dynamically based on Entropy and Magic Bytes.

## 🛠️ Usage

### Prerequisites
*   Python 3.x
*   Unix-like Environment (Linux/macOS) due to use of `fcntl`, `ss`, `pgrep`.

### Quick Start
To deploy the full environment, install dependencies, and run the simulation:

```bash
./deploy.sh
```

This will:
1.  Check your Python environment.
2.  Install dependencies from `requirements.txt`.
3.  Create and clean the isolated `war_zone/` directory.
4.  Launch the `simulation_runner.py` to orchestrate the agent swarm.

### Configuration
Tune the simulation parameters in `config.py`:
*   **AI_PARAMS:** Adjust `EPSILON` (Exploration), `ALPHA` (Learning Rate), and `GAMMA` (Discount Factor).
*   **REWARDS:** Modify incentives for Red/Blue actions.

## 📂 Repository Structure

*   `simulation_runner.py`: Main orchestrator.
*   `red_brain.py` / `blue_brain.py`: Core AI agents.
*   `agents/`: Support agents (Yellow, Green, Orange).
*   `utils.py`: Hardened utility primitives (Atomic I/O, Logging, Entropy).
*   `payloads/`: "Live Fire" malware templates.
*   `war_zone/`: The isolated sandbox where the cyber war takes place (Git-ignored).

---
*For educational and testing purposes only. Ensure you have permission before running adversarial simulations on any network.*
