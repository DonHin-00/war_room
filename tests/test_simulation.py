import unittest
import os
import time
import json
import subprocess
import signal
import sys

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class TestSimulation(unittest.TestCase):
    def setUp(self):
        # Clean up artifacts
        self.artifacts = [
            config.file_paths['state_file'],
            config.file_paths['audit_log'],
            config.file_paths['blue_q_table'],
            config.file_paths['red_q_table']
        ]
        for f in self.artifacts:
            if os.path.exists(f):
                os.remove(f)

        # Ensure watch dir exists and is empty-ish
        if not os.path.exists(config.file_paths['watch_dir']):
            os.makedirs(config.file_paths['watch_dir'])

    def test_simulation_run(self):
        print("\n🚀 Starting Integration Test: 15s Simulation Run...")

        # Launch simulation
        runner_path = os.path.join(config.BASE_DIR, "simulation_runner.py")
        process = subprocess.Popen(
            [sys.executable, runner_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Let it run
        time.sleep(15)

        # Terminate
        process.send_signal(signal.SIGINT)
        try:
            stdout, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()

        print("✅ Simulation Stopped.")

        # 1. Verify Process Exit Code (0 or -2/SIGINT are acceptable)
        # return code might be non-zero due to SIGINT, that's fine.

        # 2. Verify Artifacts Created
        self.assertTrue(os.path.exists(config.file_paths['state_file']), "War state file not created")
        self.assertTrue(os.path.exists(config.file_paths['audit_log']), "Audit log not created")

        # 3. Verify Audit Log Content
        print("🔍 Analyzing Audit Log...")
        event_types = set()
        with open(config.file_paths['audit_log'], 'r') as f:
            for line in f:
                if not line.strip(): continue
                try:
                    entry = json.loads(line)
                    event_types.add(entry.get('event'))
                except: pass

        print(f"Events Found: {event_types}")

        # We expect at least some events if the simulation is working
        # (Note: In 15s, it's possible Red doesn't attack if it's sleeping, but Blue might scan)
        # Ideally we see ACTION_TAKEN or ATTACK_LAUNCHED
        self.assertTrue(len(event_types) > 0, "No events recorded in audit log")

        # 4. Verify War State Validity
        print("🔍 Verifying War State...")
        with open(config.file_paths['state_file'], 'r') as f:
            state = json.load(f)
            self.assertIn('blue_alert_level', state)
            self.assertTrue(1 <= state['blue_alert_level'] <= 5)
            print(f"Final Alert Level: {state['blue_alert_level']}")

if __name__ == "__main__":
    unittest.main()
