import unittest
import os
import json
import tempfile
import shutil
import sys
import collections
import time
from unittest.mock import MagicMock, patch

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import red_brain
import blue_brain
import utils

class TestDefenseMechanisms(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.q_table_file = os.path.join(self.test_dir, "blue_q_table.json")
        self.state_file = os.path.join(self.test_dir, "war_state.json")
        self.watch_dir = os.path.join(self.test_dir, "watch")
        os.makedirs(self.watch_dir)

        blue_brain.Q_TABLE_FILE = self.q_table_file
        blue_brain.STATE_FILE = self.state_file
        blue_brain.WATCH_DIR = self.watch_dir

        red_brain.TARGET_DIR = self.watch_dir

        self.blue_bot = blue_brain.BlueDefender()
        self.red_bot = red_brain.RedTeamer()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_tar_pit_creation(self):
        pit_path = os.path.join(self.watch_dir, "tarpit.pipe")
        utils.create_tar_pit(pit_path)
        self.assertTrue(utils.is_tar_pit(pit_path))

    def test_safe_read_timeout(self):
        # Create a FIFO
        pit_path = os.path.join(self.watch_dir, "read_timeout.pipe")
        os.mkfifo(pit_path)

        start = time.time()
        # Should return empty string immediately or after small timeout, NOT hang
        data = utils.safe_file_read(pit_path, timeout=0.1)
        end = time.time()

        self.assertLess(end - start, 1.0)
        self.assertEqual(data, "")

    def test_red_recon_avoids_traps(self):
        pit_path = os.path.join(self.watch_dir, "trap.pipe")
        utils.create_tar_pit(pit_path)

        # Red bot recon should see it but not crash/hang
        traps_found = self.red_bot.perform_recon()
        self.assertGreaterEqual(traps_found, 1)

if __name__ == '__main__':
    unittest.main()
