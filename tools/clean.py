#!/usr/bin/env python3
import os
import shutil
import glob

def secure_delete(path):
    """Securely delete a file or directory."""
    if not os.path.exists(path):
        return

    # Anti-Symlink Defense
    if os.path.islink(path):
        print(f"⚠️  Skipping symlink: {path}")
        return

    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
            print(f"🗑️  Deleted directory: {path}")
        else:
            os.remove(path)
            print(f"🗑️  Deleted file: {path}")
    except Exception as e:
        print(f"❌ Failed to delete {path}: {e}")

def main():
    print("🧹 Cleaning simulation artifacts...")

    # Define targets
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    targets = [
        os.path.join(base_dir, "simulation_data"),
        os.path.join(base_dir, "logs"),
        os.path.join(base_dir, "models"),
        os.path.join(base_dir, "network_bus"),
        os.path.join(base_dir, "backups"),
        os.path.join(base_dir, "war_state.json"),
        os.path.join(base_dir, "signatures.json"),
        os.path.join(base_dir, "topology.json"),
        os.path.join(base_dir, "sessions.json"),
        os.path.join(base_dir, "ALERTS.txt"),
        os.path.join(base_dir, ".range_secret"),
    ]

    # Also clean orphan checksums
    checksums = glob.glob(os.path.join(base_dir, "*.sha256"))
    targets.extend(checksums)

    # Ask for confirmation
    confirm = input("Are you sure you want to delete all simulation data? [y/N] ")
    if confirm.lower() != 'y':
        print("Aborted.")
        return

    for target in targets:
        secure_delete(target)

    # Recreate dirs safely
    print("🔄 Recreating directories...")
    import sys
    sys.path.append(base_dir)
    try:
        import config
    except ImportError:
        print("Could not import config to recreate directories.")

if __name__ == "__main__":
    main()
