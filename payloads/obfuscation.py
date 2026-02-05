import time
import zlib
import base64
import os
import random
import struct

class Obfuscator:
    """
    Advanced multi-layer obfuscation engine with time-based rolling keys.
    Layers:
    1. Time-based XOR Encryption (Rolling Key)
    2. Zlib Compression
    3. Base85 Encoding
    4. Junk Injection (Polymorphism)
    5. Fake File Headers (Masquerade)
    """

    # Fake Headers
    HEADERS = {
        'png': b'\x89PNG\r\n\x1a\n',
        'pdf': b'%PDF-1.5',
        'jpg': b'\xff\xd8\xff\xe0',
        'elf': b'\x7fELF'
    }

    ROTATION_WINDOW = 30  # Seconds

    @staticmethod
    def _get_rolling_key(timestamp=None):
        """Derive a key from the current time window."""
        if timestamp is None:
            timestamp = time.time()

        # Quantize time to windows
        time_seed = int(timestamp / Obfuscator.ROTATION_WINDOW)
        random.seed(time_seed)
        key = random.randbytes(32) # 256-bit key
        return key

    @staticmethod
    def _xor_encrypt(data: bytes, key: bytes) -> bytes:
        """Simple XOR encryption with a rolling key."""
        encrypted = bytearray()
        for i, byte in enumerate(data):
            encrypted.append(byte ^ key[i % len(key)])
        return bytes(encrypted)

    @staticmethod
    def _compress(data: bytes) -> bytes:
        """Layer 2: Compression."""
        return zlib.compress(data, level=9)

    @staticmethod
    def _decompress(data: bytes) -> bytes:
        return zlib.decompress(data)

    @staticmethod
    def _encode(data: bytes) -> bytes:
        """Layer 3: Base85 Encoding."""
        return base64.b85encode(data)

    @staticmethod
    def _decode(data: bytes) -> bytes:
        return base64.b85decode(data)

    @staticmethod
    def _inject_junk(data: bytes) -> bytes:
        """Layer 4: Inject random junk bytes at the end."""
        junk_size = random.randint(10, 50)
        junk = os.urandom(junk_size)
        # We append a delimiter and the junk length so we can strip it later?
        # Actually, if we just append junk after the Base85 string,
        # legitimate decoders might fail or we need a specific format.
        # Strategy: Prepend 4 bytes length of real data, then data, then junk.
        length_header = struct.pack('>I', len(data))
        return length_header + data + junk

    @staticmethod
    def _remove_junk(data: bytes) -> bytes:
        try:
            length = struct.unpack('>I', data[:4])[0]
            return data[4:4+length]
        except:
            raise ValueError("Junk removal failed: invalid structure")

    @staticmethod
    def _add_header(data: bytes, format='png') -> bytes:
        """Layer 5: Prepend fake magic bytes."""
        header = Obfuscator.HEADERS.get(format, b'')
        return header + data

    @staticmethod
    def _strip_header(data: bytes, format='png') -> bytes:
        header = Obfuscator.HEADERS.get(format, b'')
        if data.startswith(header):
            return data[len(header):]
        return data

    @classmethod
    def obfuscate(cls, payload: str, fmt='png') -> bytes:
        """
        Full 5-layer obfuscation stack.
        Payload input is a string (e.g., Python code).
        Returns binary blob ready for disk.
        """
        # 0. Convert to bytes
        data = payload.encode('utf-8')

        # 1. Encrypt (Rolling Key)
        key = cls._get_rolling_key()
        encrypted = cls._xor_encrypt(data, key)

        # 2. Compress
        compressed = cls._compress(encrypted)

        # 3. Encode (Base85)
        encoded = cls._encode(compressed)

        # 4. Inject Junk
        junked = cls._inject_junk(encoded)

        # 5. Masquerade
        final = cls._add_header(junked, fmt)

        return final

    @classmethod
    def deobfuscate(cls, data: bytes, fmt='png', timestamp=None) -> str:
        """
        Reverse the stack.
        Requires the correct timestamp (or current time) to derive the key.
        """
        try:
            # 5. Strip Header
            no_header = cls._strip_header(data, fmt)

            # 4. Remove Junk
            clean_encoded = cls._remove_junk(no_header)

            # 3. Decode
            compressed = cls._decode(clean_encoded)

            # 2. Decompress
            encrypted = cls._decompress(compressed)

            # 1. Decrypt
            key = cls._get_rolling_key(timestamp)
            decrypted = cls._xor_encrypt(encrypted, key)

            return decrypted.decode('utf-8')
        except Exception as e:
            return f"DECRYPTION FAILED: {str(e)}"
