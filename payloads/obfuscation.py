import zlib
import base64
import os
import random
import json

# Magic Headers to fake file types
HEADERS = {
    "PNG": b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A",
    "PDF": b"\x25\x50\x44\x46\x2D\x31\x2E\x35",
    "JPG": b"\xFF\xD8\xFF\xE0"
}

XOR_KEY = b"SENTINEL_DEEP_LAYER"

def xor_data(data, key):
    if isinstance(data, str): data = data.encode()
    if isinstance(key, str): key = key.encode()

    output = bytearray()
    for i in range(len(data)):
        output.append(data[i] ^ key[i % len(key)])
    return bytes(output)

def deep_encode(payload, file_type="PNG"):
    """
    Layers:
    1. JSON Dump (if dict)
    2. Zlib Compress
    3. XOR Encrypt
    4. Base64 Encode
    5. Prepend Fake Header
    """
    if isinstance(payload, dict):
        payload = json.dumps(payload)

    if isinstance(payload, str):
        payload = payload.encode()

    # Layer 1: Compress
    compressed = zlib.compress(payload)

    # Layer 2: XOR
    encrypted = xor_data(compressed, XOR_KEY)

    # Layer 3: Base64
    b64 = base64.b64encode(encrypted)

    # Layer 4: Fake Header
    header = HEADERS.get(file_type, HEADERS["PNG"])

    # Return as bytes
    return header + b64

def deep_decode(data):
    """
    Reverse the layers. Returns payload or None.
    This is computationally annoying if you don't know it's there.
    """
    # Try stripping known headers
    payload_b64 = None

    for magic in HEADERS.values():
        if data.startswith(magic):
            payload_b64 = data[len(magic):]
            break

    if not payload_b64:
        # Maybe no header?
        payload_b64 = data

    try:
        # Layer 3: Base64
        encrypted = base64.b64decode(payload_b64)

        # Layer 2: XOR
        compressed = xor_data(encrypted, XOR_KEY)

        # Layer 1: Decompress
        payload = zlib.decompress(compressed)

        # Try JSON
        try:
            return json.loads(payload)
        except:
            return payload.decode('utf-8')

    except Exception:
        return None
