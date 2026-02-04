import socket
import threading
import logging
from .protocol import *

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SWITCH] - %(message)s')
logger = logging.getLogger(__name__)

class VirtualSwitch:
    def __init__(self, host=DEFAULT_SWITCH_HOST, port=DEFAULT_SWITCH_PORT):
        self.host = host
        self.port = port
        self.clients = {}  # IP -> conn
        self.taps = []     # List of connections monitoring traffic
        self.lock = threading.Lock()
        self.running = True

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(50)
        logger.info(f"Virtual Switch Online at {self.host}:{self.port}")

        while self.running:
            try:
                conn, addr = self.sock.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()
            except OSError:
                break

    def handle_client(self, conn, addr):
        ip_addr = None
        try:
            # First message must be HELLO
            msg = read_message(conn)
            if not msg or msg['type'] != MSG_HELLO:
                logger.warning(f"Invalid Handshake from {addr}")
                return

            ip_addr = msg['src']
            with self.lock:
                # Handle TAP registration
                if msg.get('payload', {}).get('role') == 'TAP':
                    self.taps.append(conn)
                    logger.info(f"TAP Registered: {ip_addr}")
                else:
                    self.clients[ip_addr] = conn
                    logger.info(f"Client Connected: {ip_addr}")

            # Main Loop
            while True:
                msg = read_message(conn)
                if not msg:
                    break

                self.route_packet(msg)

        except Exception as e:
            logger.error(f"Error handling client {addr}: {e}")
        finally:
            self.disconnect(ip_addr, conn)

    def route_packet(self, msg):
        dst = msg['dst']

        # 1. Send to TAPs (IDS Mirroring)
        dead_taps = []
        with self.lock:
            for tap in self.taps:
                try:
                    # Forward everything to TAP
                    packet = pack_message(msg['type'], msg['src'], msg['dst'], msg['payload'])
                    tap.sendall(packet)
                except:
                    dead_taps.append(tap)

            for dt in dead_taps:
                if dt in self.taps: self.taps.remove(dt)

        # 2. Route to Destination
        if dst == 'broadcast':
            with self.lock:
                for ip, conn in self.clients.items():
                    if ip != msg['src']: # Don't echo back to src
                        try:
                            packet = pack_message(msg['type'], msg['src'], dst, msg['payload'])
                            conn.sendall(packet)
                        except:
                            pass # Will be cleaned up by their own threads
        else:
            with self.lock:
                if dst in self.clients:
                    try:
                        packet = pack_message(msg['type'], msg['src'], dst, msg['payload'])
                        self.clients[dst].sendall(packet)
                    except:
                        pass # Target disconnected

    def disconnect(self, ip, conn):
        with self.lock:
            if ip in self.clients and self.clients[ip] == conn:
                del self.clients[ip]
                logger.info(f"Client Disconnected: {ip}")
            if conn in self.taps:
                self.taps.remove(conn)
        try:
            conn.close()
        except:
            pass

if __name__ == "__main__":
    switch = VirtualSwitch()
    switch.start()
