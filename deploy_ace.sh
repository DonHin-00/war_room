#!/bin/bash
# ACE-ES Deployment Script
# Orchestrates the Advanced Cyber Environment Emulation Suite

set -e

LOG_DIR="logs"
mkdir -p "$LOG_DIR"

echo "[*] Initializing ACE-ES Environment..."

# 1. Environment Check
echo "[*] Checking Dependencies..."
if ! command -v python3 &> /dev/null; then
    echo "[!] Python 3 not found!"
    exit 1
fi

# 2. Database Initialization
echo "[*] Initializing Database (Schema)..."
python3 db_manager.py

# 3. Threat Intelligence Ingestion
echo "[*] Fetching Threat Intelligence Feeds (This may take 15s)..."
# Force update
python3 threat_intel.py

# 4. Malware Lab Generation
echo "[*] Generating Malware Artifacts (Lab)..."
python3 lab_manager.py

# 5. Launch Agents
echo "[*] Launching Agents..."

echo "    - Starting Red APT (Attacker)..."
nohup python3 red_brain.py > "$LOG_DIR/red.log" 2>&1 &
RED_PID=$!
echo "      [PID: $RED_PID]"

echo "    - Starting Blue Hunter (Defender)..."
nohup python3 blue_brain.py > "$LOG_DIR/blue.log" 2>&1 &
BLUE_PID=$!
echo "      [PID: $BLUE_PID]"

echo "    - Starting Purple Auditor (Referee)..."
nohup python3 purple_auditor.py > "$LOG_DIR/purple.log" 2>&1 &
PURPLE_PID=$!
echo "      [PID: $PURPLE_PID]"

# 6. Save State
echo "$RED_PID" > "$LOG_DIR/red.pid"
echo "$BLUE_PID" > "$LOG_DIR/blue.pid"
echo "$PURPLE_PID" > "$LOG_DIR/purple.pid"

echo "[*] Deployment Complete."
echo "[*] Monitor logs in $LOG_DIR/"
echo "[*] To stop: kill \$(cat $LOG_DIR/*.pid)"
