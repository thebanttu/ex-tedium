#!/usr/bin/env python3
"""
Quick test script for Notes backup functionality
"""
import sys
import os

# Ensure WINHOME is set
if not os.environ.get('WINHOME'):
    os.environ['WINHOME'] = '/mnt/c/Users/ADMIN'

# Add parent directory to path to import pbkp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test the Notes sync
print("Testing Notes backup (dry run)...")
print("="*60)

# Import after setting WINHOME
import priv_init
from pbkp import sync_notes_repo, winhome, notes_backup_target

print(f"WINHOME: {winhome}")
print(f"Notes backup target: {notes_backup_target}")
print()

# Run in dry-run mode
sync_notes_repo(dry_run=True)
