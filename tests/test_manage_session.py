import sys
import os
import time
import json
import threading
import multiprocessing
import unittest
from concurrent.futures import ThreadPoolExecutor

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import manage_session, DEFAULT_SESSION_TIMEOUT

SESSION_FILE = 'sessions.json'

def init_session(idx):
    """
    Helper function to run manage_session concurrently.
    Defined outside the class to be picklable for multiprocessing.
    """
    sid = f"race_user_{idx}"
    try:
        manage_session(sid)
        return True
    except Exception as e:
        print(f"Error for {sid}: {e}")
        return False

class TestManageSession(unittest.TestCase):

    def setUp(self):
        # Reset session file before each test
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)

    def tearDown(self):
        # Clean up after test
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)

    def test_create_session(self):
        """Test creating a new session."""
        sid = "user_1"
        data = manage_session(sid)
        self.assertEqual(data['status'], 'active')
        self.assertIn('created_at', data)
        self.assertIn('last_accessed', data)

        # Verify file content
        with open(SESSION_FILE, 'r') as f:
            content = json.load(f)
        self.assertIn(sid, content)

    def test_update_session(self):
        """Test updating an existing session."""
        sid = "user_2"
        data1 = manage_session(sid)
        time.sleep(1.1) # Wait > 1s to ensure time update
        data2 = manage_session(sid)

        self.assertGreater(data2['last_accessed'], data1['last_accessed'])
        self.assertEqual(data1['created_at'], data2['created_at'])

    def test_session_expiry(self):
        """Test that expired sessions are removed."""
        sid = "user_3"
        # Create session with short timeout
        # Using a very short timeout here might be flaky if GC runs too fast/slow
        # Let's use 1s timeout and sleep 1.5s
        manage_session(sid, timeout=1)

        # Manually verify it exists
        with open(SESSION_FILE, 'r') as f:
            content = json.load(f)
        self.assertIn(sid, content)

        # Wait for expiration
        time.sleep(1.5)

        # Access another session to trigger GC
        manage_session("user_4")

        # Verify old session is gone
        with open(SESSION_FILE, 'r') as f:
            content = json.load(f)
        self.assertNotIn(sid, content)
        self.assertIn("user_4", content)

    def test_concurrent_access_threads(self):
        """Test concurrent access to manage_session using threads."""
        num_threads = 10
        sids = [f"user_concurrent_{i}" for i in range(num_threads)]

        def run_manage(sid):
            return manage_session(sid)

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            list(executor.map(run_manage, sids))

        # Verify all sessions were created successfully
        with open(SESSION_FILE, 'r') as f:
            content = json.load(f)

        for sid in sids:
            self.assertIn(sid, content)
            self.assertEqual(content[sid]['status'], 'active')

    def test_initialization_race(self):
        """
        Test the initialization race condition.
        Start multiple processes simultaneously when file doesn't exist.
        """
        # Ensure file is gone
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)

        # Use multiprocessing to truly test file creation race
        num_procs = 5
        with multiprocessing.Pool(processes=num_procs) as pool:
            results = pool.map(init_session, range(num_procs))

        self.assertTrue(all(results), "Some processes failed to manage session")

        # Verify file integrity
        with open(SESSION_FILE, 'r') as f:
            content = json.load(f)

        # Note: If the race happens, some sessions might be lost (overwritten)
        # So we assert length
        self.assertEqual(len(content), num_procs, f"Expected {num_procs} sessions, found {len(content)}")


if __name__ == '__main__':
    unittest.main()
