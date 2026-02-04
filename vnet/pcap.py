import struct
import time
import os

class PcapWriter:
    """Simple PCAP Writer for capturing VNet traffic."""

    def __init__(self, filename):
        self.filename = filename
        self.f = open(filename, 'wb')
        self._write_header()

    def _write_header(self):
        # Global Header
        # magic_number (0xa1b2c3d4), version_major (2), version_minor (4),
        # thiszone (0), sigfigs (0), snaplen (65535), network (101 - Raw IP? Or 1 for Ethernet)
        # Using LinkType 1 (Ethernet) is standard, but we are sending raw JSON...
        # Let's use LinkType 147 (User0) or just fake Ethernet headers.
        # Let's fake Ethernet for Wireshark compatibility: LinkType 1
        header = struct.pack('IHHIIII', 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1)
        self.f.write(header)
        self.f.flush()

    def write_packet(self, data):
        ts = time.time()
        sec = int(ts)
        usec = int((ts - sec) * 1000000)

        # Fake Ethernet Header (14 bytes)
        # Dst MAC (6), Src MAC (6), EtherType (2)
        # We don't have MACs, so use dummy
        eth_header = b'\x00\x00\x00\x00\x00\x02' + \
                     b'\x00\x00\x00\x00\x00\x01' + \
                     b'\x08\x00' # IPv4

        # Fake IP Header (20 bytes) to make it look like a packet
        # Just wrapping the JSON payload in minimal headers so packet analyzers don't choke
        full_payload = eth_header + data
        length = len(full_payload)

        # Packet Header
        # ts_sec, ts_usec, incl_len, orig_len
        pkt_header = struct.pack('IIII', sec, usec, length, length)

        self.f.write(pkt_header)
        self.f.write(full_payload)
        self.f.flush()

    def close(self):
        self.f.close()
