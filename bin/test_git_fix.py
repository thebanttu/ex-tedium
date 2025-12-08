#!/usr/bin/env python3
"""
Test the git.py fixes for handling empty remote repositories
"""
import sys
import os

# Add script directory to path so priv_init can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../lib')

import priv_init
from bantu.git import bantu_git_repo as bgr

print("Testing git.py fixes...")
print("="*60)

# Test with the notes repo
notes_repo_path = os.path.expanduser("~/Projects/backup/notes")

if os.path.exists(notes_repo_path):
    print(f"Testing with: {notes_repo_path}")

    try:
        repo = bgr.get_repo(notes_repo_path)
        print(f"✓ Repo loaded successfully")
        print(f"  Current branch: {repo.active_branch.name}")

        # Check if tracking branch exists
        tracking = repo.active_branch.tracking_branch()
        if tracking:
            print(f"  Tracking branch: {tracking}")
        else:
            print(f"  No tracking branch set (will be set on first push)")

        # Test repo_behind_remote
        print("\nTesting repo_behind_remote()...")
        try:
            behind = repo.repo_behind_remote()
            print(f"✓ repo_behind_remote() succeeded")
            print(f"  Result: {'Need to push' if behind else 'Up to date'}")
        except Exception as e:
            print(f"✗ Error: {e}")

        print("\n✓ All tests passed!")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"✗ Repo not found at {notes_repo_path}")
