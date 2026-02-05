import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import app, parse_nmcli, ACTIVE_PROCESSES

class TestRealApiCapabilities(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        ACTIVE_PROCESSES.clear()

    def test_nmcli_parsing(self):
        # Sample output from: nmcli -t -f SSID,BSSID,SIGNAL,SECURITY dev wifi
        # Note: nmcli escapes colons with backslash in values?
        # Actually usually it just delimits.
        sample_output = (
            "HomeWiFi:AA:BB:CC:DD:EE:FF:80:WPA2\n"
            "FreeWiFi:11:22:33:44:55:66:45:Open\n"
            "Weird:SSID:00:11:22:33:44:00:99:WPA1"
        )
        data = parse_nmcli(sample_output)

        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['ssid'], 'HomeWiFi')
        self.assertEqual(data[0]['bssid'], 'AA:BB:CC:DD:EE:FF')
        self.assertEqual(data[0]['signal'], 80)
        self.assertEqual(data[0]['security'], 'WPA2')

        # Check tricky case
        self.assertEqual(data[2]['ssid'], 'Weird:SSID')
        self.assertEqual(data[2]['bssid'], '00:11:22:33:44:00')

    @patch('api.run_command')
    def test_wifi_scan_endpoint(self, mock_run):
        mock_run.return_value = {
            "success": True,
            "output": "TestNet:AA:BB:CC:11:22:33:90:WPA2",
            "error": ""
        }

        resp = self.app.post('/api/wifi/scan')
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)

        self.assertTrue(data['success'])
        self.assertTrue('data' in data)
        self.assertEqual(data['data'][0]['ssid'], 'TestNet')

    @patch('api.subprocess.Popen')
    @patch('api.run_command')
    def test_wifi_capture_flow(self, mock_run, mock_popen):
        # Mock 'which airodump-ng' success
        mock_run.return_value = {"success": True}

        # Mock Popen process
        mock_proc = MagicMock()
        mock_proc.pid = 12345
        mock_popen.return_value = mock_proc

        payload = {
            "bssid": "AA:BB:CC:DD:EE:FF",
            "channel": 6
        }

        resp = self.app.post('/api/wifi/capture', json=payload)
        self.assertEqual(resp.status_code, 200)

        resp_data = json.loads(resp.data)
        self.assertTrue(resp_data['success'])
        self.assertIn('capture_id', resp_data)

        capture_id = resp_data['capture_id']
        self.assertIn(capture_id, ACTIVE_PROCESSES)
        self.assertEqual(ACTIVE_PROCESSES[capture_id]['pid'], 12345)

    @patch('os.getpgid')
    @patch('os.killpg')
    @patch('os.path.exists')
    def test_stop_capture(self, mock_exists, mock_kill, mock_getpgid):
        # Setup active process
        capture_id = "test_id"
        ACTIVE_PROCESSES[capture_id] = {
            "pid": 12345,
            "file_base": "/tmp/test",
            "cmd": []
        }

        mock_exists.return_value = True # File saved

        resp = self.app.post('/api/wifi/stop_capture', json={"capture_id": capture_id})
        self.assertEqual(resp.status_code, 200)

        self.assertNotIn(capture_id, ACTIVE_PROCESSES)
        mock_kill.assert_called()

if __name__ == '__main__':
    unittest.main()
