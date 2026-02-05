#!/bin/bash

# Deployment Automation Script for Cyber War Emulation
# Usage: ./deploy.sh [mode]
# Modes:
#   local   - Run locally using python3
#   docker  - Build and run using docker-compose (Default)

MODE=${1:-docker}

echo "========================================="
echo "   CYBER WAR EMULATION DEPLOYMENT TOOL"
echo "========================================="
echo "Mode: $MODE"

if [ "$MODE" == "docker" ]; then
    if ! command -v docker &> /dev/null; then
        echo "Error: Docker not found. Please install Docker or use 'local' mode."
        exit 1
    fi

    echo "[*] Building Docker Image..."
    docker-compose build

    echo "[*] Starting Stack (Detached)..."
    docker-compose up -d

    echo "[*] Deployment Complete."
    echo "    - Dashboard: http://localhost:8080"
    echo "    - Smart Target: http://localhost:5000"
    echo "    - View Logs: docker-compose logs -f"

elif [ "$MODE" == "local" ]; then
    echo "[*] Setting up Python Environment..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate

    echo "[*] Installing Dependencies..."
    pip install -r requirements.txt

    echo "[*] Launching Simulation Runner..."
    echo "    (Press Ctrl+C to stop)"
    python3 simulation_runner.py --dashboard
else
    echo "Unknown mode: $MODE"
    echo "Usage: ./deploy.sh [local|docker]"
    exit 1
fi
