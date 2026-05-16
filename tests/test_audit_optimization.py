import pytest
from ant_swarm.tools.blue_tools import ProcessAuditor

def test_scan_proc_returns_list():
    pa = ProcessAuditor()
    result = pa.scan_proc()
    assert isinstance(result, list)

def test_scan_proc_entry_structure():
    pa = ProcessAuditor()
    result = pa.scan_proc()
    if result:
        for entry in result:
            assert 'pid' in entry
            assert 'exe' in entry
            assert 'reason' in entry
            assert isinstance(entry['pid'], int)
