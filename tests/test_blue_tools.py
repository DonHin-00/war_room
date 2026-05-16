
import unittest
from unittest.mock import MagicMock, patch
from ant_swarm.tools.blue_tools import BeaconHunter

class TestBeaconHunter(unittest.TestCase):
    def setUp(self):
        self.hunter = BeaconHunter()
        self.ti_module = MagicMock()

    @patch('subprocess.check_output')
    def test_analyze_network_hit(self, mock_ss):
        # Mock ss output
        mock_ss.return_value = 'tcp ESTAB 0 0 192.168.1.10:12345 8.8.8.8:443 users:(("chrome",pid=5678,fd=10))\n'

        # Mock Threat Intel to return True for the IP
        self.ti_module.is_known_threat.return_value = True

        hits = self.hunter.analyze_network(self.ti_module)

        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]['pid'], 5678)
        self.assertEqual(hits[0]['ip'], '8.8.8.8')
        self.assertEqual(hits[0]['type'], 'Known IOC')
        self.ti_module.is_known_threat.assert_called_with('8.8.8.8')

    @patch('subprocess.check_output')
    def test_analyze_network_no_hit(self, mock_ss):
        # Mock ss output
        mock_ss.return_value = 'tcp ESTAB 0 0 192.168.1.10:12345 8.8.8.8:443 users:(("chrome",pid=5678,fd=10))\n'

        # Mock Threat Intel to return False for the IP
        self.ti_module.is_known_threat.return_value = False

        hits = self.hunter.analyze_network(self.ti_module)

        self.assertEqual(len(hits), 0)
        self.ti_module.is_known_threat.assert_called_with('8.8.8.8')

    @patch('subprocess.check_output')
    def test_analyze_network_malformed_line(self, mock_ss):
        # Mock ss output with a line that doesn't match the regex
        mock_ss.return_value = 'tcp LISTEN 0 128 0.0.0.0:22 0.0.0.0:*\n'

        hits = self.hunter.analyze_network(self.ti_module)

        self.assertEqual(len(hits), 0)
        self.ti_module.is_known_threat.assert_not_called()

if __name__ == '__main__':
    unittest.main()
