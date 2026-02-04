import os
from ant_swarm.memory.hierarchical import SharedMemory

class GlobalIndexer:
    """
    The 'Sky Eye'.
    Scans the repository to provide a high-level map to the swarm,
    preventing context pollution for local agents.
    """
    def __init__(self, root_dir: str, memory: SharedMemory):
        self.root_dir = root_dir
        self.memory = memory

    def scan_and_index(self):
        """
        Builds a file map and updates SharedMemory.
        """
        print("[INDEXER] Starting global repository scan...")
        file_map = {}
        total_size = 0
        file_count = 0

        for root, dirs, files in os.walk(self.root_dir):
            # Ignore hidden directories (like .git)
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                if file.startswith('.'): continue

                filepath = os.path.join(root, file)
                try:
                    stats = os.stat(filepath)
                    file_map[filepath] = {
                        "size": stats.st_size,
                        "type": os.path.splitext(file)[1]
                    }
                    total_size += stats.st_size
                    file_count += 1
                except:
                    pass

        summary = f"Repository Context: {file_count} files, Total Size: {total_size} bytes."

        # Feed the Main Source
        self.memory.update_global_index({
            "file_map": file_map,
            "summary": summary
        })
        print(f"[INDEXER] Scan complete. {summary}")
