
import re
import timeit
import subprocess
from unittest.mock import MagicMock, patch
from ant_swarm.tools.blue_tools import BeaconHunter

# Mocking the output of 'ss -tunap' for benchmarking
mock_output = """
tcp   ESTAB      0      0      127.0.0.1:44092                  127.0.0.1:5432       users:(("postgres",pid=1234,fd=5))
tcp   ESTAB      0      0      192.168.1.10:12345               8.8.8.8:443          users:(("chrome",pid=5678,fd=10))
""" * 1000 # Increase size for better measurement

class LegacyBeaconHunter:
    def analyze_network(self, ti_module):
        hits = []
        try:
            # Simulate subprocess overhead but use mock output
            output = mock_output
            for line in output.splitlines():
                # Extract Remote IP - Regex compilation inside loop (original behavior)
                match = re.search(r'\s+(\d+\.\d+\.\d+\.\d+):(\d+)\s+users:\(\(".*?",pid=(\d+)', line)
                if match:
                    remote_ip = match.group(1)
                    pid = int(match.group(3))
                    if ti_module.is_known_threat(remote_ip):
                        hits.append({'pid': pid, 'ip': remote_ip, 'type': 'Known IOC'})
        except Exception:
            pass
        return hits

class OptimizedBeaconHunter(BeaconHunter):
    def analyze_network(self, ti_module):
        hits = []
        try:
            # Simulate subprocess overhead but use mock output
            output = mock_output
            for line in output.splitlines():
                # Use pre-compiled regex from parent class
                match = self.CONN_RE.search(line)
                if match:
                    remote_ip = match.group(1)
                    pid = int(match.group(3))
                    if ti_module.is_known_threat(remote_ip):
                        hits.append({'pid': pid, 'ip': remote_ip, 'type': 'Known IOC'})
        except Exception:
            pass
        return hits

if __name__ == "__main__":
    ti_module = MagicMock()
    ti_module.is_known_threat.return_value = False

    legacy = LegacyBeaconHunter()
    optimized = OptimizedBeaconHunter()

    number = 100
    t1 = timeit.timeit(lambda: legacy.analyze_network(ti_module), number=number)
    t2 = timeit.timeit(lambda: optimized.analyze_network(ti_module), number=number)

    print(f"Legacy (re.search in loop) average time: {t1/number:.6f}s")
    print(f"Optimized (re.compile outside loop) average time: {t2/number:.6f}s")
    print(f"Improvement: {(t1 - t2) / t1 * 100:.2f}%")
