#!/bin/bash

# Kill existing processes
echo "[*] Cleaning up old processes..."
pkill -f "python blue_brain.py"
pkill -f "python red_brain.py"
pkill -f "python api.py"
kill $(lsof -t -i :5173) 2>/dev/null
kill $(lsof -t -i :3000) 2>/dev/null
kill $(lsof -t -i :5000) 2>/dev/null

# Start Sentinel (Blue Brain)
echo "[*] Starting Sentinel (Blue Brain)..."
nohup python blue_brain.py > logs/blue_brain.log 2>&1 &
echo "    PID: $!"

# Start Red Team
echo "[*] Starting Red Team AI..."
nohup python red_brain.py > logs/red_brain.log 2>&1 &
echo "    PID: $!"

# Start Backend API
echo "[*] Starting Cyber Muzzle API..."
nohup python api.py > logs/api.log 2>&1 &
echo "    PID: $!"

# Start Frontend
echo "[*] Starting Cyber Muzzle Interface (Live Preview)..."
cd frontend
export __VITE_ADDITIONAL_SERVER_ALLOWED_HOSTS=.com
nohup npm run dev > ../logs/frontend.log 2>&1 &
echo "    PID: $!"
cd ..

echo ""
echo "============================================"
echo "   CYBER MUZZLE SYSTEM DEPLOYED"
echo "============================================"
echo "   Frontend:  http://0.0.0.0:3000 (Proxy Safe)"
echo "   API:       http://localhost:5000"
echo "   Sentinel:  ACTIVE (Logging to logs/blue_brain.log)"
echo "   Red Team:  ACTIVE (Logging to logs/red_brain.log)"
echo "============================================"
