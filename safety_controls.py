#!/usr/bin/env python3
"""
Safety Interlock
Prevents accidental live-fire by redirecting outgoing attacks/beacons
to a safe local sinkhole while maintaining simulation fidelity.
"""

import logging
import socket
import os

class SafetyInterlock:
    def __init__(self):
        self.LIVE_FIRE_ENABLED = os.environ.get("ACE_LIVE_FIRE", "FALSE") == "TRUE"
        self.SINKHOLE_IP = "127.0.0.1"
        self.SINKHOLE_PORT = 9999 # Local safe port

    def check_connection(self, target_ip, target_port):
        """
        Intercepts connection attempts.
        Returns: (safe_ip, safe_port, was_redirected)
        """
        if self.LIVE_FIRE_ENABLED:
            logging.warning(f"[SAFETY] LIVE FIRE AUTHORIZED: Connecting to {target_ip}:{target_port}")
            return (target_ip, target_port, False)

        # Check if target is already local
        if target_ip in ["127.0.0.1", "localhost", "0.0.0.0"]:
            return (target_ip, target_port, False)

        logging.info(f"[SAFETY] INTERCEPTED: {target_ip}:{target_port} -> Redirected to SINKHOLE")
        return (self.SINKHOLE_IP, self.SINKHOLE_PORT, True)

    def is_safe_mode(self):
        return not self.LIVE_FIRE_ENABLED

# Singleton instance
interlock = SafetyInterlock()
