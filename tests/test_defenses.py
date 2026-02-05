import unittest
import os
import json
import tempfile
import shutil
import sys
import collections
import time
from unittest.mock import MagicMock, patch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import red_brain
import blue_brain
import utils
import config

class TestDefenseMechanisms(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.q_table_file = os.path.join(self.test_dir, "blue_q_table.json")
        self.state_file = os.path.join(self.test_dir, "war_state.json")
        self.watch_dir = os.path.join(self.test_dir, "watch")
        os.makedirs(self.watch_dir)

        self.orig_paths = config.PATHS.copy()
        config.PATHS["BASE_DIR"] = self.test_dir # FIX: Allow access to temp dir
        config.PATHS["Q_TABLE_BLUE"] = self.q_table_file
        config.PATHS["WAR_STATE"] = self.state_file
        config.PATHS["WAR_ZONE"] = self.watch_dir
        # Fix missing paths causing validation errors
        config.PATHS["AUDIT_LOG"] = os.path.join(self.test_dir, "audit.jsonl")
        config.PATHS["SIGNATURES"] = os.path.join(self.test_dir, "sigs.json")
        config.PATHS["Q_TABLE_RED"] = os.path.join(self.test_dir, "red.json")

        self.blue_bot = blue_brain.BlueDefender()
        self.red_bot = red_brain.RedTeamer()

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        config.PATHS = self.orig_paths

    def test_tar_pit_creation(self):
        pit_path = os.path.join(self.watch_dir, "tarpit.pipe")
        utils.create_tar_pit(pit_path)
        self.assertTrue(utils.is_tar_pit(pit_path))

    def test_safe_read_timeout(self):
        pit_path = os.path.join(self.watch_dir, "read_timeout.pipe")
        os.mkfifo(pit_path)

        start = time.time()
        data = utils.safe_file_read(pit_path, timeout=0.1)
        end = time.time()

        self.assertLess(end - start, 1.0)
        self.assertEqual(data, "")

    def test_red_recon_avoids_traps(self):
        pit_path = os.path.join(self.watch_dir, "trap.pipe")
        utils.create_tar_pit(pit_path)

        # Red recon returns dict
        # Force Red to target the watch dir (usually targets ZONES[access_level])
        # We patch _get_target_dir
        self.red_bot._get_target_dir = lambda: self.watch_dir

        result = self.red_bot.t1046_recon()
        self.assertGreaterEqual(result.get("traps_found", 0), 1)

if __name__ == '__main__':
    unittest.main()
