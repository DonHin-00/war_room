import re
from .siem import siem_logger

class DLPScanner:
    def __init__(self):
        # Regex for Credit Cards (Simplified)
        self.cc_regex = re.compile(r'\b(?:\d[ -]*?){13,16}\b')
        # Regex for SSN (Simplified)
        self.ssn_regex = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')

    def inspect_traffic(self, path, response_data):
        if not isinstance(response_data, str):
            return

        if self.cc_regex.search(response_data):
            siem_logger.log_event("DLP", "DATA_LEAK", f"Potential Credit Card leak in {path}", "CRITICAL")

        if self.ssn_regex.search(response_data):
            siem_logger.log_event("DLP", "DATA_LEAK", f"Potential SSN leak in {path}", "CRITICAL")
