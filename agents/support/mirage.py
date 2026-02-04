import random
import uuid
import time

class Mirage:
    """Deception Engine: Generates high-fidelity fake data."""

    def __init__(self):
        self.first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda"]
        self.last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
        self.domains = ["example.com", "test.org", "fake-corp.net", "internal.io"]

    def generate_user_db(self, count=10):
        lines = ["user_id,first_name,last_name,email,role,last_login"]
        for i in range(count):
            fn = random.choice(self.first_names)
            ln = random.choice(self.last_names)
            email = f"{fn.lower()}.{ln.lower()}@{random.choice(self.domains)}"
            role = "admin" if random.random() < 0.1 else "user"
            lines.append(f"{1000+i},{fn},{ln},{email},{role},{int(time.time()) - random.randint(0, 100000)}")
        return "\n".join(lines)

    def generate_aws_config(self):
        return f"""[default]
aws_access_key_id = AKIA{uuid.uuid4().hex[:16].upper()}
aws_secret_access_key = {uuid.uuid4().hex + uuid.uuid4().hex}
region = us-east-1
output = json"""

    def generate_junk_data(self, size_kb=1):
        """Generates convincing-looking binary junk (e.g. random entropy but valid header?)"""
        # For now, just high entropy noise
        return "".join([chr(random.randint(32, 126)) for _ in range(size_kb * 1024)])
