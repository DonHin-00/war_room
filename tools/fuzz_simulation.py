
import sys
import os
import random
import time
import string

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils

def fuzz_files():
    print("Fuzzing Battlefield...")
    # Inject garbage files
    for _ in range(5):
        name = ''.join(random.choices(string.ascii_letters, k=8)) + ".tmp"
        path = os.path.join(config.TARGET_DIR, name)
        with open(path, "wb") as f:
            f.write(os.urandom(1024))

    # Corrupt a random file (if any)
    try:
        files = [f.path for f in os.scandir(config.TARGET_DIR) if f.is_file()]
        if files:
            target = random.choice(files)
            with open(target, "wb") as f:
                f.write(b"CORRUPTED")
            print(f"Corrupted {os.path.basename(target)}")
    except: pass

def fuzz_state():
    print("Fuzzing State DB...")
    # Randomly flip alert level
    try:
        level = random.randint(1, 5)
        utils.DB.set_state("blue_alert_level", level)
        print(f"Forced Alert Level to {level}")
    except: pass

def main():
    print("Chaos Monkey Active. Press Ctrl+C to stop.")
    try:
        while True:
            action = random.choice([fuzz_files, fuzz_state, fuzz_files])
            action()
            time.sleep(random.uniform(2, 5))
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
