import subprocess
import time
import os
import signal
import sys
import shutil

def main():
    print("Starting Adversarial Simulation...")

    # Setup isolated environment
    war_zone_dir = os.path.abspath("war_zone")
    if os.path.exists(war_zone_dir):
        shutil.rmtree(war_zone_dir)
    os.makedirs(war_zone_dir)
    print(f"Created isolated war zone at: {war_zone_dir}")

    env = os.environ.copy()
    env["WAR_ZONE_DIR"] = war_zone_dir

    # Start Blue Team
    print("Launching Blue Team...")
    blue_process = subprocess.Popen(
        [sys.executable, "-u", "blue_brain.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )

    # Start Red Team
    print("Launching Red Team...")
    red_process = subprocess.Popen(
        [sys.executable, "-u", "red_brain.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )

    duration = 20
    print(f"Running simulation for {duration} seconds...")

    start_time = time.time()
    try:
        while time.time() - start_time < duration:
            # Check if processes are still alive
            if blue_process.poll() is not None:
                print("Blue Team process exited unexpectedly.")
                break
            if red_process.poll() is not None:
                print("Red Team process exited unexpectedly.")
                break

            time.sleep(5)
            sys.stdout.write(".")
            sys.stdout.flush()

    except KeyboardInterrupt:
        print("\nSimulation interrupted.")
    finally:
        print("\nStopping bots...")
        blue_process.terminate()
        red_process.terminate()

        try:
            blue_stdout, blue_stderr = blue_process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            blue_process.kill()
            blue_stdout, blue_stderr = blue_process.communicate()

        try:
            red_stdout, red_stderr = red_process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            red_process.kill()
            red_stdout, red_stderr = red_process.communicate()

        print("\n--- Blue Team Output (Last 20 lines) ---")
        print('\n'.join(blue_stdout.splitlines()[-20:]) if blue_stdout else "No output")
        if blue_stderr:
            print("\n--- Blue Team Errors ---")
            print(blue_stderr)

        print("\n--- Red Team Output (Last 20 lines) ---")
        print('\n'.join(red_stdout.splitlines()[-20:]) if red_stdout else "No output")
        if red_stderr:
            print("\n--- Red Team Errors ---")
            print(red_stderr)

        # Cleanup
        print(f"\nCleaning up {war_zone_dir}...")
        try:
            shutil.rmtree(war_zone_dir)
            pass
        except Exception as e:
            print(f"Error cleaning up: {e}")

        print("\nSimulation complete.")

if __name__ == "__main__":
    main()
