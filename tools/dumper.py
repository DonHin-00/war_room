#!/usr/bin/env python3
"""
Payload Dumper Tool.
Forensic utility to inspect and extract data from Stowaway containers.
"""

import sys
import os
import json
import base64
import argparse

def xor_crypt(data, key):
    return bytearray([b ^ key[i % len(key)] for i, b in enumerate(data)])

def dump_payload(filepath, output_file=None):
    if not os.path.exists(filepath):
        print(f"Error: File not found {filepath}")
        return

    try:
        with open(filepath, 'r') as f:
            container = json.load(f)

        mode = container.get("mode", "UNKNOWN")
        status = container.get("status", "DEPLOYED")
        key_b64 = container.get("key", "")
        body_b64 = container.get("body", "")

        print(f"--- Container Info ---")
        print(f"File: {filepath}")
        print(f"Mode: {mode}")
        print(f"Status: {status}")

        if key_b64 and body_b64:
            key = base64.b64decode(key_b64)
            body_enc = base64.b64decode(body_b64)

            # Decrypt
            body = xor_crypt(body_enc, key)

            print(f"Body Size: {len(body)} bytes")
            print(f"--- Payload Dump ---")

            try:
                # Try decoding as text first
                print(body.decode('utf-8', errors='ignore')[:500] + ("..." if len(body) > 500 else ""))
            except:
                print("<Binary Data>")

            if output_file:
                with open(output_file, 'wb') as out:
                    out.write(body)
                print(f"\n[+] Payload dumped to {output_file}")

    except Exception as e:
        print(f"Error dumping payload: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stowaway Payload Dumper")
    parser.add_argument("file", help="Path to stowaway .dat file")
    parser.add_argument("--output", "-o", help="Output file for dumped body")

    args = parser.parse_args()
    dump_payload(args.file, args.output)
