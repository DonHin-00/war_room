import unittest
import os
import json
import time
import sys

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import manage_session

class TestSessionManagement(unittest.TestCase):
    def setUp(self):
        self.session_id = "testsession123"
        self.session_dir = "sessions"
        self.session_file = os.path.join(self.session_dir, f"session_{self.session_id}.json")
        if os.path.exists(self.session_file):
            os.remove(self.session_file)
        if os.path.exists(self.session_dir):
            try:
                os.rmdir(self.session_dir)
            except OSError:
                pass # Directory might not be empty, which is fine for other tests

    def tearDown(self):
        if os.path.exists(self.session_file):
            os.remove(self.session_file)
        # We don't remove the directory as other tests might run in parallel or sequence,
        # but for this simple test suite we can try to clean up if empty
        try:
            os.rmdir(self.session_dir)
        except OSError:
            pass

    def test_create_new_session(self):
        manage_session(self.session_id)
        self.assertTrue(os.path.exists(self.session_file))

        with open(self.session_file, 'r') as f:
            data = json.load(f)
            self.assertEqual(data['session_id'], self.session_id)
            self.assertIn('created_at', data)
            self.assertIn('last_accessed', data)

    def test_update_existing_session(self):
        manage_session(self.session_id)
        with open(self.session_file, 'r') as f:
            data1 = json.load(f)
            t1 = data1['last_accessed']

        time.sleep(0.1)
        manage_session(self.session_id)

        with open(self.session_file, 'r') as f:
            data2 = json.load(f)
            t2 = data2['last_accessed']

        self.assertGreater(t2, t1)
        self.assertEqual(data1['created_at'], data2['created_at'])

    def test_invalid_session_id(self):
        with self.assertRaises(ValueError):
            manage_session("invalid_session_id!") # Contains underscore and exclamation

if __name__ == '__main__':
    unittest.main()
