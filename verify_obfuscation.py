import time
import sys
# Ensure we can import from current directory
sys.path.append('.')

from payloads.obfuscation import Obfuscator
import payloads.live_ammo as ammo

def test_rotation():
    print("Testing Rolling Key Obfuscation...")

    # 1. Generate Payload
    payload = "SECRET_MISSION_DATA_XYZ"
    print(f"Original: {payload}")

    # 2. Obfuscate (uses current time)
    now = time.time()
    obfuscated = Obfuscator.obfuscate(payload, fmt='png')
    print(f"Obfuscated (bytes): {len(obfuscated)}")

    # 3. Decrypt immediately (Success)
    # We must pass the exact same timestamp (or rely on time.time() if within the same second/window)
    # To be precise for the test, we pass 'now'.
    decoded = Obfuscator.deobfuscate(obfuscated, fmt='png', timestamp=now)
    print(f"Immediate Decrypt: {decoded}")

    if decoded == payload:
        print("[PASS] Immediate decryption successful.")
    else:
        print(f"[FAIL] Immediate decryption failed. Got: {decoded}")
        sys.exit(1)

    # 4. Decrypt with old/future time (Fail)
    # The window is 30 seconds. Let's shift by 35 seconds to ensure we are in a different window.
    future_time = now + 35
    decoded_fail = Obfuscator.deobfuscate(obfuscated, fmt='png', timestamp=future_time)
    print(f"Future Decrypt (+35s): {decoded_fail}")

    # It mimics garbage or fails decoding because Base85/Zlib might fail on garbage data
    # The deobfuscator catches exceptions and returns the error string usually,
    # OR if it succeeds in decompression (unlikely but possible), the text is garbage.

    if decoded_fail != payload:
        print("[PASS] Info is obsolete/unreadable with wrong time key.")
    else:
        print("[FAIL] Info was decrypted with wrong key!")
        sys.exit(1)

if __name__ == "__main__":
    test_rotation()
