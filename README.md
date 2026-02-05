# 🛡️ Sentinel: Cyber War Emulation Framework

**Sentinel** is an advanced, autonomous cyber warfare emulation environment designed to simulate realistic Red (Offense) vs. Blue (Defense) operations. It features a custom Virtual Network stack, AI-driven agents, and sophisticated security mechanisms like Zero Trust and Deep Content Inspection.

## 🌟 Key Features

### 🔴 Red Team (Adversarial Agents)
*   **Adaptive Evolution:** Agents evolve strategies using Genetic Algorithms and Reinforcement Learning (`RLBrain`).
*   **Hyper-Mutation:** Automatically rotates IP addresses and mutates obfuscation genes upon detection.
*   **Advanced Tradecraft:**
    *   **Polyglot Persistence:** Hides payloads in fake PNG files (`magic_bytes`) executed by innocent-looking loaders.
    *   **Deep Obfuscation:** Layers Zlib -> XOR -> Base64 to bypass IDS.
    *   **Timestomping:** Modifies file timestamps to blend in with system files.
    *   **Encrypted C2:** Uses XOR encryption with "Stealth Padding" (English text) to lower entropy.

### 🔵 Blue Team (Defensive Swarm)
*   **Swarm Intelligence:** Agents share Threat Intelligence (IOCs) and Reinforcement Learning models ("Brain State") via Gossip Protocol.
*   **Deep Defense:**
    *   **Zero Trust:** Enforces HMAC-signed certificate authentication for all network connections.
    *   **Deep Content Inspection:** Recursively decodes files (Base64->XOR->Zlib) to find hidden payloads.
    *   **Heuristic Hunting:** Detects Timestomping (mtime vs ctime) and Masquerading.
    *   **Entropy Detection:** Flags high-entropy network packets as potential encrypted C2.
*   **Active SOAR:**
    *   **Dynamic Firewall:** Blocks attacker IPs via the Virtual Switch.
    *   **Content Blocking:** Blacklists specific payload signatures (DPI) to counter IP rotation.

### 🌐 Virtual Network (VNet)
*   **User-Space TCP/IP Switch:** Simulates a Layer 2/3 switch on `127.0.0.1:10000`.
*   **Forensics:** Logs all traffic to binary PCAP files (`logs/capture.pcap`).
*   **Security:** Implements Port Security (Sticky MAC) and Zero Trust verification.

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

*   **Agents:** `red_mesh_node.py`, `blue_swarm_agent.py`
*   **Network:** `vnet/switch.py`, `vnet/nic.py`, `vnet/pcap.py`
*   **Services:** `services/mock_bank.py` (Vulnerable Target)
*   **Tools:** `tools/run_emulation.py`, `tools/adversary.py`, `tools/supply_chain_injector.py`

## 🔒 Security Notice
This repository contains **simulated malware** and **vulnerable services**. It is intended for educational and research purposes only. Run only in isolated environments (Docker/VM).
