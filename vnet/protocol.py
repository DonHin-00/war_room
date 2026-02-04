import struct
import json

# Network Constants
DEFAULT_SWITCH_PORT = 10000
DEFAULT_SWITCH_HOST = '127.0.0.1'

# Message Types
MSG_HELLO = 'HELLO'      # Handshake: {ip: "10.0.0.1"}
MSG_DATA = 'DATA'        # Standard Packet: {payload: ...}
MSG_BROADCAST = 'BCAST'  # Broadcast
MSG_TAP = 'TAP'          # Register as TAP (Promiscuous mode)

def pack_message(msg_type: str, src: str, dst: str, payload: dict) -> bytes:
    """Pack a message into length-prefixed JSON."""
    data = {
        'type': msg_type,
        'src': src,
        'dst': dst,
        'payload': payload
    }
    json_bytes = json.dumps(data).encode('utf-8')
    # 4 bytes length + body
    return struct.pack('!I', len(json_bytes)) + json_bytes

def read_message(sock) -> dict:
    """Read a length-prefixed message from a socket."""
    # Read length (4 bytes)
    header = b''
    while len(header) < 4:
        chunk = sock.recv(4 - len(header))
        if not chunk:
            return None
        header += chunk

    length = struct.unpack('!I', header)[0]

    # Read body
    body = b''
    while len(body) < length:
        chunk = sock.recv(min(4096, length - len(body)))
        if not chunk:
            return None
        body += chunk

    return json.loads(body.decode('utf-8'))
