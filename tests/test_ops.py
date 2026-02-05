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
        config.PATHS["BASE_DIR"] = self.test_dir # FIX: Allow access to temp dir
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
        self.blue.backup_critical()
        self.assertIn("secrets.txt", self.blue.backups)
        # safe_file_read uses binary mode now, so it reads as bytes
        self.assertEqual(self.blue.backups["secrets.txt"], content)

        # 3. Red encrypts it
        # We need to ensure Red has access to the zone (Red defaults to DMZ, test dir is generic)
        # But t1486_encrypt searches in self._get_target_dir().
        # We need to force Red's target dir or move file to DMZ.
        # Simpler: Mock Red's _get_target_dir or access_level?
        # Let's ensure access_level covers the file.
        # But config.ZONES keys are absolute paths.
        # The test sets config.PATHS["WAR_ZONE"].
        # But Red uses config.ZONES.
        # We need to patch config.ZONES too!

        # FIX: The test didn't patch ZONES, so Red is looking at real paths probably or defaulting to something broken.
        # Let's assume for this unit test we just want to call the method.
        # But Red.t1486_encrypt calls _get_target_dir() which uses ZONES[access_level].
        # So we MUST patch ZONES.

        # Update: patching ZONES in setUp would be better, but let's just make Red look at WAR_ZONE.
        self.red._get_target_dir = lambda: self.war_zone

        result = self.red.t1486_encrypt()
        self.assertEqual(result.get("impact", 0), 8) # 8 is impact for encrypt
        self.assertFalse(os.path.exists(critical_file))
        self.assertTrue(os.path.exists(critical_file + ".enc"))

        # 4. Blue restores it
        result = self.blue.restore_data()
        self.assertEqual(result.get("restored", 0), 1)
        self.assertTrue(os.path.exists(critical_file))
        self.assertFalse(os.path.exists(critical_file + ".enc"))

        # Verify content (binary read)
        with open(critical_file, 'rb') as f:
            self.assertEqual(f.read(), content)

    # def test_incident_reporting(self):
    #     # Deprecated: Incident reporting is now handled by AuditLogger
    #     pass

if __name__ == '__main__':
    unittest.main()
