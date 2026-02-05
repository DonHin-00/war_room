from .siem import siem_logger
from .firewall import block_ip
import random

class FraudDetector:
    def check_transaction(self, sender_id, amount, avg_amount=1000):
        if amount > 10000:
            siem_logger.log_event("FraudDetector", "HIGH_VALUE_TX", f"User {sender_id} transferring ${amount}", "WARNING")
            return False

        if amount > avg_amount * 5:
            siem_logger.log_event("FraudDetector", "ANOMALY_TX", f"User {sender_id} unusual amount ${amount}", "CRITICAL")
            return False

        return True

class IdentityDefense:
    def check_login(self, username, ip_address):
        # Simulated Geo-IP check
        suspicious_ips = ["192.168.1.100", "10.0.0.55"] # Mock bad IPs
        if ip_address in suspicious_ips:
            siem_logger.log_event("IdentityDefense", "SUSPICIOUS_IP", f"Login attempt for {username} from {ip_address}", "HIGH")
            block_ip(ip_address)
            return False

        # Check for obvious attack patterns in username
        attack_signatures = ["<script>", "' OR", "UNION SELECT"]
        for sig in attack_signatures:
            if sig in username:
                siem_logger.log_event("IdentityDefense", "ATTACK_SIGNATURE", f"Attack payload in username: {username}", "CRITICAL")
                block_ip(ip_address)
                return False

        return True
