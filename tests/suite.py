import unittest
import threading
import time
import sys
import os
import json
import shutil

# Setup Path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import utils
import config
from vnet.protocol import pack_message, MSG_HELLO
from vnet.switch import VirtualSwitch
from vnet.nic import VNic
from agents.blue_brain import BlueSwarmAgent
from payloads.obfuscation import deep_encode, deep_decode
from payloads.polymorph import polymorph_payload

class TestSentinel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Setup Environment
        cls.test_dir = "tests/test_data"
        if os.path.exists(cls.test_dir): shutil.rmtree(cls.test_dir)
        os.makedirs(cls.test_dir)

        # Patch Config
        config.SIMULATION_DATA_DIR = cls.test_dir
        config.SESSION_DB = os.path.join(cls.test_dir, "sessions.json")

        # Start Switch
        cls.switch_port = 10005
        cls.switch = VirtualSwitch(port=cls.switch_port)
        cls.t = threading.Thread(target=cls.switch.start, daemon=True)
        cls.t.start()
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.switch.running = False
        try:
            cls.switch.sock.close()
        except: pass
        shutil.rmtree(cls.test_dir)

    def test_01_crypto_utils(self):
        """Verify obfuscation stack."""
        payload = {"secret": "weapon_x"}
        encoded = deep_encode(payload, "PNG")
        self.assertTrue(encoded.startswith(b"\x89PNG"))

        decoded = deep_decode(encoded)
        self.assertEqual(decoded['secret'], "weapon_x")

    def test_02_polymorphism(self):
        """Verify structural polymorphism."""
        payload = {"cmd": "exec"}
        poly1 = polymorph_payload(payload)
        poly2 = polymorph_payload(payload)

        self.assertNotEqual(str(poly1), str(poly2))
        self.assertEqual(poly1['cmd'], "exec")
        # Check for noise keys
        self.assertTrue(any(k.startswith("_") for k in poly1.keys()))

    def test_03_vnet_auth(self):
        """Verify Zero Trust Handshake."""
        nic = VNic("10.50.0.1", switch_port=self.switch_port)
        # Should succeed (auto-registers token)
        self.assertTrue(nic.connect())
        nic.close()

    def test_04_blue_ids(self):
        """Verify Blue Team Entropy Detection logic."""
        agent = BlueSwarmAgent()

        # Low Entropy
        low = agent.calculate_entropy(b"AAAAAAA")
        self.assertLess(low, 1.0)

        # High Entropy (Random)
        high = agent.calculate_entropy(os.urandom(100))
        self.assertGreater(high, 4.0)

if __name__ == '__main__':
    unittest.main()
