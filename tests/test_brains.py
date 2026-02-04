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
import config

class TestRedBrain(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.q_table_file = os.path.join(self.test_dir, "red_q_table.json")
        self.state_file = os.path.join(self.test_dir, "war_state.json")

        # Patch config paths
        self.orig_paths = config.PATHS.copy()
        config.PATHS["Q_TABLE_RED"] = self.q_table_file
        config.PATHS["WAR_STATE"] = self.state_file
        config.PATHS["WAR_ZONE"] = self.test_dir

        # Initialize Bot
        self.bot = red_brain.RedTeamer()

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        config.PATHS = self.orig_paths

    def test_initialization(self):
        self.assertTrue(self.bot.running)
        self.assertEqual(len(self.bot.q_tables["A"]), 0)

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

        self.orig_paths = config.PATHS.copy()
        config.PATHS["Q_TABLE_BLUE"] = self.q_table_file
        config.PATHS["WAR_STATE"] = self.state_file
        config.PATHS["WAR_ZONE"] = self.test_dir

        self.bot = blue_brain.BlueDefender()

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        config.PATHS = self.orig_paths

    def test_entropy_calc(self):
        fpath = os.path.join(self.test_dir, "zero_entropy.txt")
        with open(fpath, 'wb') as f: f.write(b'A' * 100)

        with open(fpath, 'rb') as f:
            data = f.read()
            self.assertEqual(utils.calculate_entropy(data), 0.0)

        fpath2 = os.path.join(self.test_dir, "high_entropy.bin")
        data_random = os.urandom(100)
        with open(fpath2, 'wb') as f: f.write(data_random)
        self.assertGreater(utils.calculate_entropy(data_random), 3.0)

if __name__ == '__main__':
    unittest.main()
