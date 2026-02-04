import unittest
import os
import json
import tempfile
import shutil
import sys
from unittest.mock import MagicMock, patch

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import red_brain
import blue_brain
import utils

class TestRedBrain(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.q_table_file = os.path.join(self.test_dir, "red_q_table.json")
        self.state_file = os.path.join(self.test_dir, "war_state.json")

        # Patch paths
        self.original_q_file = red_brain.Q_TABLE_FILE
        self.original_state_file = red_brain.STATE_FILE
        self.original_target_dir = red_brain.TARGET_DIR

        red_brain.Q_TABLE_FILE = self.q_table_file
        red_brain.STATE_FILE = self.state_file
        red_brain.TARGET_DIR = self.test_dir

        # Initialize Bot
        self.bot = red_brain.RedTeamer()

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        red_brain.Q_TABLE_FILE = self.original_q_file
        red_brain.STATE_FILE = self.original_state_file
        red_brain.TARGET_DIR = self.original_target_dir

    def test_initialization(self):
        self.assertTrue(self.bot.running)
        self.assertEqual(len(self.bot.q_table), 0)

    def test_state_manager_load_save(self):
        data = {"key": "value"}
        self.bot.state_manager.save_json(self.q_table_file, data)
        loaded = self.bot.state_manager.load_json(self.q_table_file)
        self.assertEqual(data, loaded)

    def test_war_state_mtime_caching(self):
        initial_state = {'blue_alert_level': 1}
        self.bot.state_manager.save_json(self.state_file, initial_state)

        # First read
        state1 = self.bot.state_manager.get_war_state()
        self.assertEqual(state1['blue_alert_level'], 1)

        # Modify file manually
        new_state = {'blue_alert_level': 5}
        # Force mtime update
        time_future = os.stat(self.state_file).st_mtime + 10
        with open(self.state_file, 'w') as f:
            json.dump(new_state, f)
        os.utime(self.state_file, (time_future, time_future))

        # Second read should catch update
        state2 = self.bot.state_manager.get_war_state()
        self.assertEqual(state2['blue_alert_level'], 5)

    def test_engage_shutdown(self):
        with self.assertRaises(SystemExit):
            self.bot.shutdown(None, None)

class TestBlueBrain(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.q_table_file = os.path.join(self.test_dir, "blue_q_table.json")
        self.state_file = os.path.join(self.test_dir, "war_state.json")

        # Patch paths
        self.original_q_file = blue_brain.Q_TABLE_FILE
        self.original_state_file = blue_brain.STATE_FILE
        self.original_watch_dir = blue_brain.WATCH_DIR

        blue_brain.Q_TABLE_FILE = self.q_table_file
        blue_brain.STATE_FILE = self.state_file
        blue_brain.WATCH_DIR = self.test_dir

        self.bot = blue_brain.BlueDefender()

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        blue_brain.Q_TABLE_FILE = self.original_q_file
        blue_brain.STATE_FILE = self.original_state_file
        blue_brain.WATCH_DIR = self.original_watch_dir

    def test_entropy_calc(self):
        # Create a file with zero entropy (all A's)
        fpath = os.path.join(self.test_dir, "zero_entropy.txt")
        with open(fpath, 'wb') as f: f.write(b'A' * 100)
        # Use utils.calculate_entropy since blue_brain uses it directly
        with open(fpath, 'rb') as f:
            data = f.read()
            self.assertEqual(utils.calculate_entropy(data), 0.0)

        # High entropy (random)
        fpath2 = os.path.join(self.test_dir, "high_entropy.bin")
        data_random = os.urandom(100)
        with open(fpath2, 'wb') as f: f.write(data_random)
        self.assertGreater(utils.calculate_entropy(data_random), 3.0)

if __name__ == '__main__':
    unittest.main()
