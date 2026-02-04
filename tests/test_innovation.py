import unittest
import os
import json
import tempfile
import shutil
import sys
import collections
from unittest.mock import MagicMock, patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import red_brain
import blue_brain
import utils
import config

class TestRedBrainInnovation(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.q_table_file = os.path.join(self.test_dir, "red_q_table.json")
        self.state_file = os.path.join(self.test_dir, "war_state.json")

        self.orig_paths = config.PATHS.copy()
        config.PATHS["Q_TABLE_RED"] = self.q_table_file
        config.PATHS["WAR_STATE"] = self.state_file
        config.PATHS["WAR_ZONE"] = self.test_dir

        self.bot = red_brain.RedTeamer()

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        config.PATHS = self.orig_paths

    def test_double_q_learning_initialization(self):
        self.assertIn("A", self.bot.q_tables)
        self.assertIn("B", self.bot.q_tables)

    def test_experience_replay(self):
        for i in range(10):
            self.bot.replay_buffer.push("S1", "A1", 10, "S2")

        self.assertEqual(len(self.bot.replay_buffer), 10)
        batch = self.bot.replay_buffer.sample(5)
        self.assertEqual(len(batch), 5)

    def test_adaptive_sync(self):
        self.assertTrue("SYNC_INTERVAL" in config.RL)

class TestBlueBrainInnovation(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.q_table_file = os.path.join(self.test_dir, "blue_q_table.json")
        self.state_file = os.path.join(self.test_dir, "war_state.json")
        self.watch_dir = os.path.join(self.test_dir, "watch")
        os.makedirs(self.watch_dir)

        self.orig_paths = config.PATHS.copy()
        config.PATHS["Q_TABLE_BLUE"] = self.q_table_file
        config.PATHS["WAR_STATE"] = self.state_file
        config.PATHS["WAR_ZONE"] = self.watch_dir

        self.bot = blue_brain.BlueDefender()

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        config.PATHS = self.orig_paths

    def test_anomaly_detection(self):
        self.assertFalse(self.bot.detect_anomaly(2))
        self.assertFalse(self.bot.detect_anomaly(2))
        self.assertFalse(self.bot.detect_anomaly(2))
        self.assertTrue(self.bot.detect_anomaly(10))

    def test_honeypot_deployment(self):
        self.bot.deploy_nasty_defenses()
        files = os.listdir(self.watch_dir)
        # Check for specific traps deployed
        found = any("access.log" in f or "shadow_backup" in f for f in files)
        self.assertTrue(found)

if __name__ == '__main__':
    unittest.main()
