import threading
import os
import json
import time
import sys
import shutil

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils

TARGET_FILE = "concurrency_test.json"
THREADS = 10
ITERATIONS = 50

def writer(tid):
    for i in range(ITERATIONS):
        # Read-Modify-Write Loop using Transaction
        with utils.atomic_json_update(TARGET_FILE, {"count": 0, "logs": []}) as data:
            data["count"] += 1
            data["logs"].append(f"Thread-{tid}-{i}")
        time.sleep(0.001)

def test_concurrency():
    print("🧪 Starting Concurrency Test...")

    # Init
    with utils.atomic_json_update(TARGET_FILE, {"count": 0, "logs": []}) as data:
        pass

    threads = []
    for i in range(THREADS):
        t = threading.Thread(target=writer, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Verify
    with utils.atomic_json_update(TARGET_FILE) as final_data:
        pass # Just read

    expected = THREADS * ITERATIONS
    actual = final_data["count"]

    print(f"Expected Count: {expected}")
    print(f"Actual Count:   {actual}")

    if expected == actual:
        print("✅ Concurrency Integrity Check PASSED")
    else:
        print("❌ Concurrency Integrity Check FAILED (Lost Updates)")
        sys.exit(1)

    # Cleanup
    if os.path.exists(TARGET_FILE): os.remove(TARGET_FILE)
    if os.path.exists(TARGET_FILE + ".sha256"): os.remove(TARGET_FILE + ".sha256")

if __name__ == "__main__":
    test_concurrency()
