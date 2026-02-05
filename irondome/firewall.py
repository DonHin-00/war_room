from .siem import siem_logger

_BLOCKED_IPS = set()

def block_ip(ip):
    if ip not in _BLOCKED_IPS:
        _BLOCKED_IPS.add(ip)
        siem_logger.log_event("Firewall", "IP_BLOCKED", f"Blocking IP {ip} due to threats", "CRITICAL")

def is_blocked(ip):
    return ip in _BLOCKED_IPS
