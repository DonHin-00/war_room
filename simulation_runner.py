
import subprocess
import time
import argparse
import sys
import os
import signal

# Process registry
processes = []

def cleanup(signum, frame):
    print("\n\033[93m[SIMULATION] Shutting down...\033[0m")
    for p in processes:
        p.terminate()
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="AI Cyber War Simulation Runner")
    parser.add_argument("--proxy", action="store_true", help="Enable Proxy War Emulation")
    parser.add_argument("--duration", type=int, default=300, help="Simulation duration in seconds")
    args = parser.parse_args()

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    print("\033[92m[SIMULATION] Starting AI Cyber War...\033[0m")

    # 1. Start Blue Brain
    blue = subprocess.Popen(["python3", "-u", "blue_brain.py"])
    processes.append(blue)

    # 2. Start Red Brain
    red = subprocess.Popen(["python3", "-u", "red_brain.py"])
    processes.append(red)

    # 3. Start Proxy War (Optional)
    if args.proxy:
        print("\033[95m[SIMULATION] Launching Proxy War Emulation...\033[0m")
        proxy = subprocess.Popen(["python3", "-u", "proxy_war.py", str(args.duration)])
        processes.append(proxy)

    try:
        # Keep running
        time.sleep(args.duration)
    except KeyboardInterrupt:
        cleanup(None, None)

    cleanup(None, None)

if __name__ == "__main__":
    main()
