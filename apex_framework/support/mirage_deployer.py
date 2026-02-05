import os
from apex_framework.core.hive import HiveMind

class MirageLayer:
    """
    Orchestrates the Deployment of Deception Tech.
    Rigging the Noob Spots.
    """
    def __init__(self, hive: HiveMind):
        self.hive = hive
        self.active_traps = []

    def deploy_labyrinth(self):
        """
        Deploys all deception assets.
        """
        print("[MIRAGE] 🎭 Deploying Labyrinth Protocol...")
        self._rig_noob_spots()
        self._deploy_decoys()

    def _rig_noob_spots(self):
        """
        Creates booby-trapped files in common locations.
        """
        traps = {
            ".env": "API_KEY=sk_live_FAKE_KEY_12345\nDB_PASS=hunter2",
            "config.json": '{"debug": true, "admin_token": "null"}',
            "admin_panel.py": "# HONEYPOT: Running this triggers a beacon\nimport time\nprint('Access Denied')\ntime.sleep(10)"
        }

        for filename, content in traps.items():
            path = os.path.join(os.getcwd(), filename)
            # Only create if doesn't exist to avoid overwriting real stuff (Safety)
            if not os.path.exists(path):
                try:
                    with open(path, 'w') as f:
                        f.write(content)
                    self.active_traps.append(filename)
                    print(f"[MIRAGE] 🪤 Rigged Trap: {filename}")
                    # In a real system, we'd add file-watchers here to trigger the signal
                    # self.hive.broadcast("TRAP_ARMED", {"file": filename}, "Mirage")
                except: pass

    def _deploy_decoys(self):
        """
        Spawns Polymorphic entities in memory.
        """
        # Simulated registration
        print("[MIRAGE] 👻 Spawning Polymorphic 'AuthManager' Decoy...")
        self.hive.memory.update_threat_matrix("active_decoys", 1)
