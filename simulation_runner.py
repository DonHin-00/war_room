
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

    # Ensure Battlefield exists with secure permissions
    import config
    if not os.path.exists(config.TARGET_DIR):
        os.makedirs(config.TARGET_DIR, mode=0o700, exist_ok=True)
    else:
        os.chmod(config.TARGET_DIR, 0o700)

    # 1. Start Blue Brain
    # Scrub environment to prevent leaks
    clean_env = {k: v for k, v in os.environ.items()
                 if k in ['PATH', 'PYTHONPATH', 'LANG', 'HOME', 'USER']}

    blue = subprocess.Popen(["python3", "-u", "blue_brain.py"], env=clean_env)
    processes.append(blue)

    # 2. Start Red Brain
    red = subprocess.Popen(["python3", "-u", "red_brain.py"], env=clean_env)
    processes.append(red)

    # 3. Start Smart Live Target (Adaptive HTTP)
    print("\033[93m[SIMULATION] Booting Smart Live Target (Port 5000)...\033[0m")
    target = subprocess.Popen(["python3", "-u", "smart_target.py"], env=clean_env)
    processes.append(target)

    # 4. Start SOC (The "Overwatch")
    print("\033[94m[SIMULATION] Activating Security Operations Center (SOC)...\033[0m")
    soc = subprocess.Popen(["python3", "-u", "soc_core.py"], env=clean_env)
    processes.append(soc)

    # 5. Start Proxy War (Optional)
    if args.proxy:
        print("\033[95m[SIMULATION] Launching Proxy War Emulation...\033[0m")
        proxy = subprocess.Popen(["python3", "-u", "proxy_war.py", str(args.duration)], env=clean_env)
        processes.append(proxy)

    try:
        # Keep running
        time.sleep(args.duration)
    except KeyboardInterrupt:
        cleanup(None, None)

    cleanup(None, None)

if __name__ == "__main__":
    main()
