import random
import string
import json

def generate_noise():
    """Generate random string noise."""
    length = random.randint(4, 12)
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def polymorph_payload(payload):
    """
    Inject random noise keys into a dictionary payload to alter its hash.
    Preserves original keys.
    """
    if not isinstance(payload, dict):
        return payload

    new_payload = payload.copy()

    # Inject 1-3 random noise keys
    for _ in range(random.randint(1, 3)):
        key = f"_{generate_noise()}" # Prefix with _ to denote ignore-able
        val = generate_noise()
        new_payload[key] = val

    # Recursively polymorph nested dicts
    for k, v in new_payload.items():
        if isinstance(v, dict):
            new_payload[k] = polymorph_payload(v)

    return new_payload
