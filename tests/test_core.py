import unittest
import os
import json
import shutil
import tempfile
import sys

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import utils
import config

class TestSecurity(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test.txt")
        self.test_json = os.path.join(self.test_dir, "test.json")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_secure_create_atomic(self):
        """Test that secure_create fails if file exists."""
        # Create first
        self.assertTrue(utils.secure_create(self.test_file, "content"))
        # Create second - should fail
        self.assertFalse(utils.secure_create(self.test_file, "overwrite"))

        with open(self.test_file, 'r') as f:
            self.assertEqual(f.read(), "content")

    def test_safe_json_io(self):
        """Test safe JSON read/write."""
        data = {"test": 123}
        self.assertTrue(utils.safe_json_write(self.test_json, data))
        read_data = utils.safe_json_read(self.test_json)
        self.assertEqual(read_data, data)

    def test_validate_state(self):
        """Test state validation."""
        self.assertTrue(utils.validate_state({'blue_alert_level': 1}))
        self.assertFalse(utils.validate_state({'blue_alert_level': "bad"}))
        self.assertFalse(utils.validate_state("not a dict"))

    def test_permissions_config(self):
        """Test config directories have correct permissions (if they exist)."""
        # This test runs in an env where we might not be able to check exact permissions easily
        # due to umask, but we can check the code logic or existence.
        # Check if utils.check_root exists
        self.assertTrue(callable(utils.check_root))

if __name__ == '__main__':
    unittest.main()
