# 🛡️ Sentinel Deployment Guide

This repository contains the **Sentinel Cyber War Emulation** environment, a sophisticated multi-agent simulation of Red (Attack) and Blue (Defense) teams interacting over a Virtual Network.

## Prerequisites

*   Docker
*   Docker Compose

## Quick Start

1.  **Run the Deployment Script:**
    ```bash
    ./deploy.sh
    ```
    This will build the container and start the simulation in the background.

2.  **View the Dashboard:**
    To see the live Cyber War Dashboard (TUI):
    ```bash
    docker-compose exec -it sentinel python tools/dashboard.py
    ```

3.  **View Logs:**
    ```bash
    docker-compose logs -f
    ```

4.  **Stop the Simulation:**
    ```bash
    docker-compose down
    ```

## Architecture

*   **Virtual Network (`vnet`):** A custom user-space TCP/IP switch emulation.
*   **Red Team:** Autonomous agents performing scanning, exploitation (SQLi, XSS), and persistence.
*   **Blue Team:** Autonomous defenders with EDR, IDS, and SOAR capabilities.
*   **Targets:** Vulnerable services (e.g., Mock Bank) hosted on the VNet.

## Security Note

This environment intentionally contains vulnerable code (`services/mock_bank.py`) and simulated malware (`red_mesh_node.py`). It is designed to run in an isolated container. **Do not expose the container ports to untrusted networks.**
