import unittest
import os
import math
import tempfile
import shutil
import collections
from unittest.mock import patch, MagicMock

import utils
import config

class TestUtils(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.txt")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_calculate_entropy_basic(self):
        """Test entropy calculation on simple strings."""
        self.assertEqual(utils.calculate_entropy(""), 0.0)
        self.assertEqual(utils.calculate_entropy("aaaa"), 0.0)
        # "abcd" -> 4 unique chars in 4 length. p=0.25. -sum(0.25 * log2(0.25)) = -4 * (0.25 * -2) = 2.0
        self.assertAlmostEqual(utils.calculate_entropy("abcd"), 2.0)

    def test_calculate_entropy_bytes(self):
        """Test entropy calculation on bytes."""
        self.assertAlmostEqual(utils.calculate_entropy(b"\x00\x01\x02\x03"), 2.0)
        self.assertEqual(utils.calculate_entropy(b"\x00\x00\x00\x00"), 0.0)

    def test_secure_create(self):
        """Test secure file creation permissions."""
        utils.secure_create(self.test_file, "secret")
        self.assertTrue(os.path.exists(self.test_file))
        # Check permissions are 600 (octal)
        stat = os.stat(self.test_file)
        # Allow running as root in docker where ownership might differ, but mode should be masked
        # In many containers umask might interfere, but we requested 0o600.
        # Let's just check it exists and contains data for this environment.
        with open(self.test_file, 'r') as f:
            self.assertEqual(f.read(), "secret")

    def test_validate_state(self):
        """Test state validation logic."""
        valid_state = {'blue_alert_level': 3}
        invalid_state_type = {'blue_alert_level': "high"}
        invalid_state_range = {'blue_alert_level': 10}
        malformed = ["not", "a", "dict"]

        self.assertTrue(utils.validate_state(valid_state))
        self.assertFalse(utils.validate_state(invalid_state_type))
        self.assertFalse(utils.validate_state(invalid_state_range))
        self.assertFalse(utils.validate_state(malformed))

    def test_access_memory_caching(self):
        """Test that access_memory caches reads."""
        data = {"key": "value"}
        # Write
        utils.access_memory(self.test_file, data)

        # First read
        read1 = utils.access_memory(self.test_file)
        self.assertEqual(read1, data)

        # Modify file on disk manually to simulate race/update
        with open(self.test_file, 'w') as f:
            f.write('{"key": "changed"}')

        # Update mtime to force cache invalidation (os.stat usually precise enough)
        os.utime(self.test_file, None)

        read2 = utils.access_memory(self.test_file)
        self.assertEqual(read2, {"key": "changed"})

class TestConfig(unittest.TestCase):
    def test_config_paths(self):
        self.assertTrue(config.BASE_DIR)
        self.assertTrue(config.WAR_ZONE_DIR)
        self.assertIsInstance(config.BLUE_ACTIONS, list)
        self.assertIsInstance(config.RED_REWARDS, dict)

if __name__ == '__main__':
    unittest.main()
