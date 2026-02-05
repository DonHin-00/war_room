# 🛡️ Sentinel: Cyber War Emulation Framework

**Sentinel** is an advanced, autonomous cyber warfare emulation environment designed to simulate realistic Red (Offense) vs. Blue (Defense) operations. It features a custom Virtual Network stack, AI-driven agents, and sophisticated security mechanisms like Zero Trust and Deep Content Inspection.

## 🌟 Key Features

### 🔴 Red Team (Adversary)
*   **Adaptive Evolution:** Agents evolve strategies using Genetic Algorithms and Reinforcement Learning (`RLBrain`).
*   **Advanced Tradecraft:**
    *   **Lateral Movement:** Pivots from compromised frontend nodes to restricted internal backends (`192.168.1.10`) via RCE.
    *   **Polyglot Persistence:** Hides payloads in fake PNG files executed by innocent-looking loaders ("Lazarus" mechanism).
    *   **Deep Obfuscation:** Layers Zlib -> XOR -> Base64 -> Fake Headers to bypass IDS.
    *   **Structural Polymorphism:** Injects random JSON noise to defeat hash-based signatures.
    *   **Fast Flux:** Rotates IP addresses and mutation genes upon detection.

### 🔵 Blue Team (Defender)
*   **Swarm Intelligence:** Agents share Threat Intelligence (IOCs) and "Brain State" (Q-Tables) via Gossip Protocol.
*   **Deep Defense:**
    *   **UEBA:** User & Entity Behavior Analytics tracks request baselines to flag anomalies (e.g., Impossible Travel).
    *   **Deep Content Inspection:** Recursively decodes files to neutralize polyglot threats.
    *   **Heuristic Correlation:** Detects "Wolf Pack" attacks and triggers DEFCON 2 Lockdowns.
    *   **Active SOAR:** Enforces dynamic firewalling and content blocking at the Virtual Switch.

### 🟡 Yellow Team (Builder)
*   **DevOps Simulation:** Deploys simulated code updates (Features/Bugfixes) to targets.
*   **Dynamic Security:** Adjusts code quality (Secure vs Vulnerable) based on real-time feedback from Orange Team standards.

### 🟢 Green Team (DevSecOps)
*   **Pipeline Gatekeeper:** Performs SAST (Static Analysis) on deployments, blocking insecure code (`eval`, secrets).
*   **Instrumentation:** Automatically injects logging and monitoring hooks into target services.

### 🍊 Orange Team (Threat Intel)
*   **Attack Analysis:** Maps audit logs to MITRE ATT&CK and CWE identifiers.
*   **Feedback Loop:** Generates `coding_standards.json` to guide Builders based on prevalent threats.

### 🏳️ White Team (Governance)
*   **Rules of Engagement:** Monitors simulation health and enforces boundaries (e.g., resetting runaway events).

### 🌐 Virtual Network (VNet)
*   **User-Space TCP/IP Switch:** Simulates a Layer 2/3 switch on `127.0.0.1:10000`.
*   **Security:** Implements Port Security (Sticky MAC), Zero Trust (mTLS), and DPI Firewall.
*   **Forensics:** Logs all traffic to binary PCAP files (`logs/capture.pcap`).

## 🚀 Quick Start (Docker)

1.  **Deploy:**
    ```bash
    ./deploy.sh
    ```
2.  **Dashboard:**
    ```bash
    docker-compose exec -it sentinel python tools/dashboard.py
    ```
3.  **Logs:**
    ```bash
    docker-compose logs -f
    ```

## 🛠️ Architecture

*   **Agents:** Located in `agents/` (`red_brain.py`, `blue_brain.py`, etc.)
*   **Network:** `vnet/switch.py`, `vnet/nic.py`, `vnet/pcap.py`
*   **Services:** `services/mock_bank.py` (Dual-interface Target)
*   **Tools:** `tools/run_emulation.py`, `tools/supply_chain_injector.py`

## 🔒 Security Notice
This repository contains **simulated malware** and **vulnerable services**. It is intended for educational and research purposes only. Run only in isolated environments (Docker/VM).
