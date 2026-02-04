import unittest
import os
import sys
import threading
import time
import json
import signal
import subprocess
import shutil
import tempfile

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils
import config

class TestAdversarialStress(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.test_dir, "war_state.json")

        # Patch config
        self.orig_paths = config.PATHS.copy()
        config.PATHS["WAR_STATE"] = self.state_file
        config.PATHS["BASE_DIR"] = self.test_dir

        # Init state
        utils.safe_json_write(self.state_file, {"count": 0})

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        config.PATHS = self.orig_paths

    def test_race_condition_writes(self):
        def increment_state():
            for _ in range(10):
                try:
                    for retry in range(5):
                        data = utils.safe_json_read(self.state_file)
                        if data:
                            data["count"] = data.get("count", 0) + 1
                            utils.safe_json_write(self.state_file, data)
                            break
                        time.sleep(0.01)
                except Exception as e:
                    print(f"Thread Error: {e}")

        threads = []
        for _ in range(20):
            t = threading.Thread(target=increment_state)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        final_data = utils.safe_json_read(self.state_file)
        self.assertIn("count", final_data)
        self.assertGreater(final_data["count"], 0)
        print(f"Race Condition Result: {final_data['count']}/200")

    def test_signal_storm(self):
        state_path = os.path.join(self.test_dir, "agent_state.json")
        agent_script = os.path.join(self.test_dir, "dummy_agent.py")

        # FIX: Patch config inside the subprocess
        script_content = r"""
import sys
import time
import signal
import os

sys.path.append('{}')
import utils
import config

# Patch config so validate_path allows writing to test_dir
config.PATHS["BASE_DIR"] = '{}'

running = True
def handler(s, f):
    global running
    running = False

signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGTERM, handler)

path = '{}'

while running:
    utils.safe_json_write(path, {{"status": "alive"}})
    time.sleep(0.1)
""".format(os.getcwd(), self.test_dir, state_path)

        with open(agent_script, 'w') as f:
            f.write(script_content)

        proc = subprocess.Popen([sys.executable, agent_script], cwd=self.test_dir)
        time.sleep(1)

        for _ in range(5):
            proc.send_signal(signal.SIGINT)
            time.sleep(0.1)

        try:
            proc.wait(timeout=2)
        except:
            proc.kill()

        data = utils.safe_json_read(state_path)
        self.assertEqual(data.get("status"), "alive")

if __name__ == '__main__':
    unittest.main()
