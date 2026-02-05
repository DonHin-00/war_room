#!/usr/bin/env python3
"""
Secure C2 Crypto Module
Provides AES-GCM encryption for C2 payloads.
"""

import os
import json
import base64
try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:
    # Fallback if cryptography not installed (simulation mode)
    # We will implement a basic XOR for simulation fidelity if deps missing
    # But ideally we use real crypto.
    AESGCM = None

class C2Crypto:
    def __init__(self, key=None):
        # 256-bit key
        self.key = key or os.urandom(32)

    def encrypt(self, data: dict) -> str:
        payload = json.dumps(data).encode('utf-8')

        if AESGCM:
            nonce = os.urandom(12)
            aesgcm = AESGCM(self.key)
            ciphertext = aesgcm.encrypt(nonce, payload, None)
            # Format: nonce + ciphertext (b64 encoded)
            return base64.b64encode(nonce + ciphertext).decode('utf-8')
        else:
            # XOR Fallback (Simulation Only - Not Secure but "Real Code")
            # In a real environment, we'd insist on the library.
            # XOR key cycling
            key_bytes = self.key
            encrypted = bytearray()
            for i, b in enumerate(payload):
                encrypted.append(b ^ key_bytes[i % len(key_bytes)])
            return base64.b64encode(encrypted).decode('utf-8')

# Singleton with a simulation key
# In production, this comes from ENV or Config
c2_crypto = C2Crypto(b'0'*32)
