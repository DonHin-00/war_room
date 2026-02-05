#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}[DEPLOY] Starting Cyber War Simulation Deployment...${NC}"

# 1. Environment Check
echo -e "${BLUE}[DEPLOY] Checking Python environment...${NC}"
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed."
    exit 1
fi

# 2. Dependencies
if [ -f "requirements.txt" ]; then
    echo -e "${BLUE}[DEPLOY] Installing dependencies...${NC}"
    pip install -r requirements.txt
else
    echo "Warning: requirements.txt not found."
fi

# 3. Setup Directories
echo -e "${BLUE}[DEPLOY] Cleaning and preparing War Zone...${NC}"
export WAR_ZONE_DIR="./war_zone"
if [ -d "$WAR_ZONE_DIR" ]; then
    rm -rf "$WAR_ZONE_DIR"
fi
mkdir -p "$WAR_ZONE_DIR"

# 4. Launch Simulation
echo -e "${GREEN}[DEPLOY] Launching Simulation Runner...${NC}"
echo "---------------------------------------------------"
python3 simulation_runner.py
echo "---------------------------------------------------"
echo -e "${GREEN}[DEPLOY] Simulation Completed.${NC}"
