import socket
import threading
import logging
import os
from .protocol import *
from .pcap import PcapWriter

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SWITCH] - %(message)s')
logger = logging.getLogger(__name__)

MAX_CONNECTIONS = 50

class VirtualSwitch:
    def __init__(self, host=DEFAULT_SWITCH_HOST, port=DEFAULT_SWITCH_PORT):
        self.host = host
        self.port = port
        self.clients = {}  # IP -> conn
        self.taps = []     # List of connections monitoring traffic
        self.lock = threading.Lock()
        self.running = True

        # PCAP logging
        self.pcap = PcapWriter("logs/capture.pcap")

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(MAX_CONNECTIONS)
        logger.info(f"Virtual Switch Online at {self.host}:{self.port}")

        while self.running:
            try:
                conn, addr = self.sock.accept()

                # Connection Limit
                with self.lock:
                    if len(self.clients) + len(self.taps) >= MAX_CONNECTIONS:
                        logger.warning(f"Refused connection from {addr} (Limit Reached)")
                        conn.close()
                        continue

                threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()
            except OSError:
                break

    def handle_client(self, conn, addr):
        ip_addr = None
        try:
            # First message must be HELLO
            conn.settimeout(5.0) # Handshake timeout
            msg = read_message(conn)
            conn.settimeout(None)

            if not msg or msg['type'] != MSG_HELLO:
                logger.debug(f"Invalid Handshake from {addr}")
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
        packet = pack_message(msg['type'], msg['src'], dst, msg['payload'])

        # Log to PCAP
        try:
            self.pcap.write_packet(packet)
        except Exception as e:
            logger.error(f"PCAP Write Error: {e}")

        if dst == 'broadcast':
            with self.lock:
                for ip, conn in self.clients.items():
                    if ip != msg['src']: # Don't echo back to src
                        try:
                            conn.sendall(packet)
                        except:
                            pass # Will be cleaned up by their own threads
        else:
            with self.lock:
                if dst in self.clients:
                    try:
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
