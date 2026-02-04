import unittest
import os
import time
import subprocess
import sys
import threading

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

NUM_INSTANCES = 3
DURATION = 30

def run_instance(instance_id):
    print(f"🚀 Starting Simulation Instance {instance_id}...")
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    runner_path = os.path.join(config.BASE_DIR, "simulation_runner.py")

    # We deliberately use the SAME config/files to stress test locking
    try:
        process = subprocess.Popen(
            [sys.executable, runner_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )

        # Capture output
        try:
            stdout, stderr = process.communicate(timeout=DURATION)
        except subprocess.TimeoutExpired:
            process.terminate()
            stdout, stderr = process.communicate()

        if stderr:
            print(f"⚠️  Instance {instance_id} STDERR:\n{stderr}")

    except Exception as e:
        print(f"❌ Instance {instance_id} Failed: {e}")

if __name__ == "__main__":
    print(f"⚡ Starting Parallel Stress Test: {NUM_INSTANCES} concurrent simulations...")
    print(f"🎯 Goal: Stress test fcntl locking on {config.file_paths['state_file']}")

    threads = []
    start_time = time.time()

    for i in range(NUM_INSTANCES):
        t = threading.Thread(target=run_instance, args=(i,))
        threads.append(t)
        t.start()
        time.sleep(1) # Stagger slightly

    for t in threads:
        t.join()

    print(f"\n✅ Stress Test Complete in {time.time() - start_time:.2f}s")
