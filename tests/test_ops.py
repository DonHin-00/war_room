import unittest
import os
import json
import tempfile
import shutil
import sys
import time
import hashlib

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import red_brain
import blue_brain
import utils
import config

class TestOpsIntegration(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.war_zone = os.path.join(self.test_dir, "battlefield")
        self.data_dir = os.path.join(self.test_dir, "data")
        self.incidents_dir = os.path.join(self.data_dir, "incidents")
        os.makedirs(self.war_zone)
        os.makedirs(self.incidents_dir)

        # Patch config paths for isolation
        self.orig_paths = config.PATHS.copy()
        config.PATHS["WAR_ZONE"] = self.war_zone
        config.PATHS["AUDIT_LOG"] = os.path.join(self.data_dir, "audit.jsonl")
        config.PATHS["INCIDENTS"] = self.incidents_dir
        config.PATHS["WAR_STATE"] = os.path.join(self.data_dir, "war_state.json")
        config.PATHS["Q_TABLE_RED"] = os.path.join(self.data_dir, "red.json")
        config.PATHS["Q_TABLE_BLUE"] = os.path.join(self.data_dir, "blue.json")
        config.PATHS["SIGNATURES"] = os.path.join(self.data_dir, "sigs.json")

        # Initialize Utils state (since it might be module level)
        # Re-init logger
        utils.setup_logging(os.path.join(self.test_dir, "test.log"))

        self.red = red_brain.RedTeamer()
        self.blue = blue_brain.BlueDefender()

    def tearDown(self):
        config.PATHS = self.orig_paths
        shutil.rmtree(self.test_dir)

    def test_audit_logger_chaining(self):
        logger = utils.AuditLogger(config.PATHS["AUDIT_LOG"])
        logger.log_event("TEST", "EVENT_1", {"data": 1})
        logger.log_event("TEST", "EVENT_2", {"data": 2})

        with open(config.PATHS["AUDIT_LOG"], 'r') as f:
            lines = f.readlines()

        self.assertEqual(len(lines), 2)
        e1 = json.loads(lines[0])
        e2 = json.loads(lines[1])

        # Check chain
        self.assertEqual(e1["previous_hash"], "0"*64)
        self.assertEqual(e2["previous_hash"], e1["hash"])

        # Verify Integrity
        # Re-calc hash for e1
        e1_copy = e1.copy()
        del e1_copy["hash"]
        expected_hash = hashlib.sha256(json.dumps(e1_copy, sort_keys=True).encode('utf-8')).hexdigest()
        self.assertEqual(e1["hash"], expected_hash)

    def test_ransomware_restore_cycle(self):
        # 1. Create a critical file
        critical_file = os.path.join(self.war_zone, "secrets.txt")
        content = b"My Secret Data"
        with open(critical_file, 'wb') as f: f.write(content)

        # 2. Blue backs it up
        self.blue.perform_backup()
        self.assertIn("secrets.txt", self.blue.backups)
        # safe_file_read uses 'r' mode, so it reads as string
        self.assertEqual(self.blue.backups["secrets.txt"], content.decode('utf-8'))

        # 3. Red encrypts it
        success = self.red.encrypt_target()
        self.assertEqual(success, 1)
        self.assertFalse(os.path.exists(critical_file))
        self.assertTrue(os.path.exists(critical_file + ".enc"))

        # 4. Blue restores it
        restored = self.blue.restore_data()
        self.assertEqual(restored, 1)
        self.assertTrue(os.path.exists(critical_file))
        self.assertFalse(os.path.exists(critical_file + ".enc"))

        # Verify content
        with open(critical_file, 'r') as f:
            self.assertEqual(f.read(), "My Secret Data")

    def test_incident_reporting(self):
        self.blue.generate_incident_report("TEST_THREAT", "/tmp/malware")

        files = os.listdir(self.incidents_dir)
        self.assertEqual(len(files), 1)

        with open(os.path.join(self.incidents_dir, files[0]), 'r') as f:
            report = json.load(f)
            self.assertEqual(report["type"], "TEST_THREAT")
            self.assertEqual(report["action"], "MITIGATED")

if __name__ == '__main__':
    unittest.main()
