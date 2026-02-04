import os
import json
import difflib
import math
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

class FileContext:
    """
    Level 1: Short-term Memory (Local Visibility).
    Represents the active file the agent is working on.
    """
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.content = ""
        self.lines = []
        self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self.content = f.read()
                self.lines = self.content.splitlines()

    def get_context_window(self, start_line: int, end_line: int) -> str:
        """Returns a specific slice of the file to save tokens."""
        # clamp values
        start = max(0, start_line)
        end = min(len(self.lines), end_line)
        return "\n".join(self.lines[start:end])

    def update(self, new_content: str):
        self.content = new_content
        self.lines = self.content.splitlines()

class SessionDiff:
    """
    Level 2: Mid-term Memory (Session Context).
    Tracks what has changed during this 'session' or 'sprint'.
    """
    def __init__(self):
        self.changes: List[Dict[str, Any]] = []

    def record_change(self, filepath: str, diff: str, agent_id: str):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "filepath": filepath,
            "diff": diff,
            "agent": agent_id
        }
        self.changes.append(entry)

    def get_recent_changes(self, limit: int = 5) -> List[Dict[str, Any]]:
        return self.changes[-limit:]

class VectorADR:
    """
    Level 3: Long-term Memory (Architecture Decision Records).
    Simulates a Vector DB using Keyword/Jaccard similarity.
    Stores 'Why' we made decisions.
    """
    def __init__(self, db_path: str = "adrs.json"):
        self.db_path = db_path
        self.records: List[Dict[str, str]] = []
        self._load_db()

    def _load_db(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r') as f:
                    self.records = json.load(f)
            except:
                self.records = []
        else:
            # Seed with some defaults if empty
            self.records = [
                {"id": "001", "title": "No Eval", "content": "Never use eval() or exec() due to security risks.", "tags": ["security", "python"]},
                {"id": "002", "title": "50 Line Limit", "content": "Functions must not exceed 50 lines to ensure readability.", "tags": ["maintainability", "style"]},
                {"id": "003", "title": "Latency Critical", "content": "All I/O must be non-blocking where possible. 1ms delay is unacceptable.", "tags": ["performance", "latency"]}
            ]
            self._save_db()

    def _save_db(self):
        with open(self.db_path, 'w') as f:
            json.dump(self.records, f, indent=2)

    def add_record(self, title: str, content: str, tags: List[str]):
        self.records.append({
            "id": str(len(self.records) + 1).zfill(3),
            "title": title,
            "content": content,
            "tags": tags
        })
        self._save_db()

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, str]]:
        """
        Simulates vector search using Jaccard Similarity on sets of words.
        """
        query_tokens = set(re.findall(r'\w+', query.lower()))
        results = []

        for record in self.records:
            doc_text = f"{record['title']} {record['content']} {' '.join(record['tags'])}"
            doc_tokens = set(re.findall(r'\w+', doc_text.lower()))

            # Jaccard Similarity
            intersection = query_tokens.intersection(doc_tokens)
            union = query_tokens.union(doc_tokens)
            if not union:
                score = 0
            else:
                score = len(intersection) / len(union)

            results.append((score, record))

        # Sort by score desc
        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in results[:top_k] if r[0] > 0]

class SharedMemory:
    """
    The Main Source.
    A centralized bus that all agents connect to.
    """
    def __init__(self):
        self.adrs = VectorADR()
        self.session = SessionDiff()
        self.global_index = {} # To be populated by Indexer
        self.active_files: Dict[str, FileContext] = {}

    def get_file_context(self, filepath: str) -> FileContext:
        if filepath not in self.active_files:
            self.active_files[filepath] = FileContext(filepath)
        return self.active_files[filepath]

    def update_global_index(self, index_data: Dict):
        """Feeds the main source with global knowledge."""
        self.global_index.update(index_data)

    def retrieve_context(self, query: str, filepath: str = None) -> Dict[str, Any]:
        """
        Holistic retrieval:
        1. Relevant ADRs (Why)
        2. Recent Session Changes (What just happened)
        3. File Context (Where we are) - if filepath provided
        """
        context = {
            "adrs": self.adrs.search(query),
            "recent_changes": self.session.get_recent_changes(),
            "global_summary": self.global_index.get("summary", "No global index available.")
        }
        if filepath:
            context["local_file"] = self.get_file_context(filepath).content

        return context
