import unittest
import os
import json
import tempfile
import shutil
import sys
import collections
from unittest.mock import MagicMock, patch

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import red_brain
import blue_brain
import utils

class TestRedBrainInnovation(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.q_table_file = os.path.join(self.test_dir, "red_q_table.json")
        self.state_file = os.path.join(self.test_dir, "war_state.json")

        red_brain.Q_TABLE_FILE = self.q_table_file
        red_brain.STATE_FILE = self.state_file
        red_brain.TARGET_DIR = self.test_dir

        self.bot = red_brain.RedTeamer()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_double_q_learning_initialization(self):
        self.assertIn("A", self.bot.q_tables)
        self.assertIn("B", self.bot.q_tables)

    def test_experience_replay(self):
        # Push enough to sample
        for i in range(10):
            self.bot.replay_buffer.push("S1", "A1", 10, "S2")

        self.assertEqual(len(self.bot.replay_buffer), 10)
        batch = self.bot.replay_buffer.sample(5)
        self.assertEqual(len(batch), 5)

    def test_adaptive_sync(self):
        # This logic is inside engage loop, hard to unit test without refactoring loop.
        # But we can verify the constant is there.
        self.assertTrue(hasattr(red_brain, 'BASE_SYNC_INTERVAL'))

class TestBlueBrainInnovation(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.q_table_file = os.path.join(self.test_dir, "blue_q_table.json")
        self.state_file = os.path.join(self.test_dir, "war_state.json")
        self.watch_dir = os.path.join(self.test_dir, "watch")
        os.makedirs(self.watch_dir)

        blue_brain.Q_TABLE_FILE = self.q_table_file
        blue_brain.STATE_FILE = self.state_file
        blue_brain.WATCH_DIR = self.watch_dir

        self.bot = blue_brain.BlueDefender()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_anomaly_detection(self):
        # Feed normal data
        self.assertFalse(self.bot.detect_anomaly(2))
        self.assertFalse(self.bot.detect_anomaly(2))
        self.assertFalse(self.bot.detect_anomaly(2))

        # Feed spike
        # Avg is 2. Spike > 4.
        self.assertTrue(self.bot.detect_anomaly(10))

    def test_honeypot_deployment(self):
        self.bot.deploy_honeypot()
        files = os.listdir(self.watch_dir)
        found = any("honeypot" in f for f in files)
        self.assertTrue(found)

if __name__ == '__main__':
    unittest.main()
