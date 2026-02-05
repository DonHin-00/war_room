import socket
import threading
import queue
import time
import logging
import sys
import os

# Ensure root is in path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils
import config

from .protocol import *

logger = logging.getLogger(__name__)

class VNic:
    """Virtual Network Interface Card."""
    def __init__(self, ip, switch_host=DEFAULT_SWITCH_HOST, switch_port=DEFAULT_SWITCH_PORT, is_tap=False):
        self.ip = ip
        self.switch_addr = (switch_host, switch_port)
        self.is_tap = is_tap
        self.sock = None

        # Identity
        self.id_mgr = utils.IdentityManager(config.SESSION_DB)
        # Register/Login to get token
        self.token = self.id_mgr.login(self.ip)
        self.rx_queue = queue.Queue()
        self.running = False
        self.connected = False

    def connect(self):
        """Connect to the Virtual Switch."""
        while not self.connected:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect(self.switch_addr)

                # Handshake with Zero Trust Token
                role = 'TAP' if self.is_tap else 'CLIENT'
                packet = pack_message(MSG_HELLO, self.ip, 'switch', {
                    'role': role,
                    'token': self.token
                })
                self.sock.sendall(packet)

                self.connected = True
                self.running = True
                threading.Thread(target=self._listen_loop, daemon=True).start()
                logger.info(f"VNIC {self.ip} connected to Switch.")
                return True
            except ConnectionRefusedError:
                logger.warning(f"Switch unavailable, retrying in 2s...")
                time.sleep(2)
            except Exception as e:
                logger.error(f"VNIC Connection Error: {e}")
                time.sleep(2)
        return False

    def send(self, dst, payload, msg_type=MSG_DATA):
        """Send a packet."""
        if not self.connected:
            return False
        try:
            packet = pack_message(msg_type, self.ip, dst, payload)
            self.sock.sendall(packet)
            return True
        except Exception as e:
            logger.error(f"Send Error: {e}")
            self.close()
            return False

    def recv(self, timeout=None):
        """Blocking receive."""
        try:
            return self.rx_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def _listen_loop(self):
        while self.running:
            try:
                msg = read_message(self.sock)
                if not msg:
                    break # Connection closed
                self.rx_queue.put(msg)
            except Exception:
                break

        self.connected = False
        logger.info(f"VNIC {self.ip} disconnected.")

    def close(self):
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
