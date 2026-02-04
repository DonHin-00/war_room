import unittest
import os
import sys
import json
import shutil

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import utils
import config

class TestCoreFeatures(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_data"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_checksum_integrity(self):
        file_path = os.path.join(self.test_dir, "data.json")
        data = {"key": "value"}

        # Write data (auto-generates checksum)
        utils.safe_json_write(file_path, data)
        self.assertTrue(os.path.exists(file_path + ".checksum"))

        # Read back (should match)
        loaded = utils.safe_json_read(file_path)
        self.assertEqual(loaded, data)

        # Tamper with file
        with open(file_path, 'w') as f:
            f.write('{"key": "TAMPERED"}')

        # Read back (should detect mismatch and return empty/error)
        # Note: safe_json_read logs error and returns {} on mismatch
        loaded_tampered = utils.safe_json_read(file_path)
        self.assertEqual(loaded_tampered, {})

    def test_calculate_checksum(self):
        file_path = os.path.join(self.test_dir, "file.txt")
        with open(file_path, 'w') as f:
            f.write("hello world")

        # sha256("hello world") = b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9
        expected = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
        self.assertEqual(utils.calculate_checksum(file_path), expected)

    def test_resource_limits(self):
        # Just ensure it doesn't crash
        try:
            utils.limit_resources()
        except Exception as e:
            self.fail(f"limit_resources raised exception: {e}")

if __name__ == '__main__':
    unittest.main()
