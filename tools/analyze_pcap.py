#!/usr/bin/env python3
import sys
import struct
import json
import os

def analyze_pcap(filename):
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return

    print(f"🔍 Analyzing Forensics Capture: {filename}")
    print("========================================")

    with open(filename, 'rb') as f:
        # Read Global Header (24 bytes)
        global_header = f.read(24)
        if len(global_header) < 24:
            print("Invalid PCAP file.")
            return

        pkt_count = 0
        while True:
            # Read Packet Header (16 bytes)
            pkt_header = f.read(16)
            if not pkt_header: break

            ts_sec, ts_usec, incl_len, orig_len = struct.unpack('IIII', pkt_header)

            # Read Packet Data
            pkt_data = f.read(incl_len)

            # Skip Ethernet (14)
            # Skip IPv4 (20) - but we faked it in vnet/pcap.py
            # 14 + 0 (we just did fake eth + data)
            # Actually looking at pcap.py: eth_header = 14 bytes. Then data.

            try:
                # Payload is at offset 14
                payload = pkt_data[14:]

                # Try to decode length-prefixed JSON
                if len(payload) > 4:
                    msg_len = struct.unpack('!I', payload[:4])[0]
                    json_data = payload[4:4+msg_len]

                    obj = json.loads(json_data.decode('utf-8'))
                    print(f"[{ts_sec}] {obj['type']} {obj['src']} -> {obj['dst']}")

                    if obj['type'] == 'DATA':
                        payload_content = obj.get('payload', {})
                        # Check for Encrypted C2
                        if isinstance(payload_content, dict) and payload_content.get('proto') == 'C2v2':
                             print(f"    🔒 ENCRYPTED C2 DETECTED: {len(payload_content.get('blob', ''))} bytes")
                        elif isinstance(payload_content, dict):
                             # Show interesting keys
                             keys = list(payload_content.keys())
                             print(f"    Payload: {keys}")

            except Exception as e:
                # print(f"Packet Parse Error: {e}")
                pass

            pkt_count += 1

    print(f"\nTotal Packets Analyzed: {pkt_count}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_pcap.py <pcap_file>")
    else:
        analyze_pcap(sys.argv[1])
