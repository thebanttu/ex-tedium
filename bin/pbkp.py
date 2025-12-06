#!/usr/bin/env python3
"""
Enhanced backup script for WSL environment
Backs up important configs, scripts, and selective project data elegantly
"""

import priv_init
import bantu.utils
import os, re, subprocess, sys, time, json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from bantu.utils import bantu_utils as bu
from bantu.git import bantu_git_repo as bgr
from os import access, R_OK, X_OK
from os.path import isfile, isdir, exists
from pprint import pprint as pp

# Configuration
home = os.environ.get('HOME')
winhome = os.environ.get('WINHOME', '/mnt/c/Users/ADMIN')  # WSL Windows home
backup_root = Path(home) / 'Projects' / 'backup'
backup_target = str(backup_root / 'env')
notes_backup_target = str(backup_root / 'notes')
python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

# Git repositories
repos = {
    "env": "git@github.com:thebanttu/bantu-env.git",
    "notes": "git@github.com:thebanttu/my-org.git",
    "extedium": "git@github.com:thebanttu/ex-tedium.git",
}

# Exclude patterns
default_excludes = [
    home + '/.excludes/junk.txt',
]

wsl_excludes = [
    '**/.git/',
    '**/.git/**',
    '**/node_modules/',
    '**/node_modules/**',
    '**/__pycache__/',
    '**/__pycache__/**',
    '**/vendor/',
    '**/vendor/**',
    '**/.venv/',
    '**/.venv/**',
    '**/venv/',
    '**/venv/**',
    '**/.terraform/',
    '**/.terraform/**',
    '**/dist/',
    '**/dist/**',
    '**/build/',
    '**/build/**',
    '**/.cache/',
    '**/.cache/**',
    '**/*.swp',
    '**/*.swo',
    '**/*.swn',
    '**/.DS_Store',
    '**/Thumbs.db',
    '**/.claude/**',
]

# Critical projects to backup (selective backup)
# These are projects with unique configs or work that's not in git
critical_projects = [
    # Add specific project names here that need backing up
    # Most git repos don't need backup as they're already versioned
]

# Backup configuration with cleaner structure
backup_config = {
    # Shell utilities and deployment scripts
    'shell_utils': {
        'source': home + '/bin/',
        'target': backup_target + '/bin/',
        'description': 'Shell utilities and deployment scripts',
        'exclude_patterns': wsl_excludes,
    },

    # Python libraries (from ex-tedium)
    'python_libs': {
        'source': home + '/ex-tedium/lib/bantu/',
        'target': backup_target + '/lib/',
        'description': 'Bantu Python libraries',
        'exclude_patterns': wsl_excludes,
    },

    # Emacs configuration
    'emacs_config': {
        'source': home + '/.emacs.d/',
        'target': backup_target + '/config/emacs/',
        'description': 'Emacs configuration',
        'exclude': [home + '/.excludes/emacs.exclude.txt'],
        'exclude_patterns': wsl_excludes,
    },

    # Essential dotfiles
    'dotfiles': {
        'files': [
            home + '/.gitconfig',
            home + '/.rgignore',
            home + '/.rtorrent.rc',
            home + '/.tmux.conf',
            home + '/.vim',
            home + '/.xbindkeysrc',
            home + '/.xinitrc',
            home + '/.zshrc',
            home + '/.Xresources',
            home + '/.bashrc',
            home + '/.profile',
        ],
        'target': backup_target + '/config/dotfiles/',
        'description': 'Essential dotfiles',
    },

    # Config directory (selective)
    'config_dirs': {
        'subdirs': [
            'claude-code',
            'git',
            'ranger',
            'cursor',
        ],
        'base_source': home + '/.config/',
        'target': backup_target + '/config/app-configs/',
        'description': 'Application configs from ~/.config',
        'exclude_patterns': wsl_excludes,
    },

    # MPV configuration
    'mpv_config': {
        'source': home + '/.config/mpv/',
        'target': backup_target + '/config/mpv/',
        'description': 'MPV media player config',
    },

    # Package list
    'package_list': {
        'files': [home + '/.pkg-list.txt'],
        'target': backup_target + '/config/pkg/',
        'description': 'System package list',
    },

    # Exclude lists
    'exclude_lists': {
        'source': home + '/.excludes/',
        'target': backup_target + '/exclude/',
        'description': 'Rsync exclude lists',
    },

    # SSH config (if exists)
    'ssh_config': {
        'source': home + '/.ssh/',
        'target': backup_target + '/config/ssh/',
        'description': 'SSH configuration and keys',
        'exclude': [],  # Be careful with private keys
    },

    # Ex-tedium bins
    'ex_tedium_bins': {
        'source': home + '/bin/',
        'target': home + '/ex-tedium/bin/',
        'description': 'Ex-tedium binary scripts',
        'exclude_patterns': wsl_excludes,
        'repo': 'extedium',
    },

    # Ex-tedium libs
    'ex_tedium_libs': {
        'source': home + '/ex-tedium/lib/bantu/',
        'target': home + '/ex-tedium/lib/bantu/',
        'description': 'Ex-tedium library files',
        'exclude_patterns': wsl_excludes,
        'repo': 'extedium',
    },

    # Ex-tedium exclude files
    'ex_tedium_excludes': {
        'source': home + '/.excludes/',
        'target': home + '/ex-tedium/files/',
        'description': 'Ex-tedium exclude files',
        'repo': 'extedium',
    },
}

class BackupStats:
    """Track backup statistics"""
    def __init__(self):
        self.files_copied = 0
        self.bytes_copied = 0
        self.errors = []
        self.skipped = []
        self.start_time = time.time()

    def add_error(self, item: str, error: str):
        self.errors.append((item, error))

    def add_skipped(self, item: str, reason: str):
        self.skipped.append((item, reason))

    def print_summary(self):
        elapsed = time.time() - self.start_time
        print("\n" + "="*60)
        print("BACKUP SUMMARY")
        print("="*60)
        print(f"Time elapsed: {elapsed:.2f} seconds")
        print(f"Files processed: {self.files_copied}")
        if self.bytes_copied > 0:
            size_mb = self.bytes_copied / (1024 * 1024)
            print(f"Data copied: {size_mb:.2f} MB")

        if self.skipped:
            print(f"\nSkipped items: {len(self.skipped)}")
            for item, reason in self.skipped[:5]:  # Show first 5
                print(f"  - {item}: {reason}")
            if len(self.skipped) > 5:
                print(f"  ... and {len(self.skipped) - 5} more")

        if self.errors:
            print(f"\n⚠ Errors encountered: {len(self.errors)}")
            for item, error in self.errors:
                print(f"  - {item}: {error}")
        else:
            print("\n✓ Backup completed successfully with no errors")
        print("="*60 + "\n")

stats = BackupStats()

def create_backup_destination_tree():
    """Create all necessary backup directories"""
    dirs_created = []
    for name, config in backup_config.items():
        target = None
        if 'target' in config:
            target = config['target']
        elif 'base_target' in config:
            target = config['base_target']

        if target and not os.path.exists(target):
            try:
                os.makedirs(target, exist_ok=True)
                dirs_created.append(target)
            except Exception as e:
                stats.add_error(target, f"Failed to create directory: {e}")

    if dirs_created:
        print(f"Created {len(dirs_created)} backup directories")
    return

def write_exclude_file(patterns: List[str]) -> Optional[str]:
    """Write exclude patterns to a temporary file for rsync"""
    if not patterns:
        return None

    import tempfile
    try:
        fd, path = tempfile.mkstemp(prefix='backup_exclude_', suffix='.txt')
        with os.fdopen(fd, 'w') as f:
            for pattern in patterns:
                f.write(pattern + '\n')
        return path
    except Exception as e:
        stats.add_error('exclude_file', f"Failed to create exclude file: {e}")
        return None

def sync_directory(source: str, target: str, description: str,
                   exclude_files: List[str] = None,
                   exclude_patterns: List[str] = None,
                   dry_run: bool = False):
    """Sync a directory with rsync"""
    if not exists(source):
        stats.add_skipped(description, f"Source doesn't exist: {source}")
        return False

    print(f"\n→ {description}")
    print(f"  {source} → {target}")

    # Prepare exclude arguments
    exclude_args = []
    temp_exclude_file = None

    # Add exclude files
    if exclude_files:
        for ex_file in exclude_files:
            if exists(ex_file):
                exclude_args.extend(['--exclude-from', ex_file])

    # Add exclude patterns via temp file
    if exclude_patterns:
        temp_exclude_file = write_exclude_file(exclude_patterns)
        if temp_exclude_file:
            exclude_args.extend(['--exclude-from', temp_exclude_file])

    try:
        # Use the bantu xrsync utility if available
        kwargs = {}
        if exclude_files or exclude_patterns:
            all_excludes = (exclude_files or []).copy()
            if temp_exclude_file:
                all_excludes.append(temp_exclude_file)
            kwargs['ex'] = all_excludes

        if dry_run:
            kwargs['dry_run'] = True

        bu.xrsync(source, target, **kwargs)
        print(f"  ✓ Completed")
        return True

    except Exception as e:
        stats.add_error(description, str(e))
        print(f"  ✗ Error: {e}")
        return False
    finally:
        # Clean up temp file
        if temp_exclude_file and exists(temp_exclude_file):
            try:
                os.unlink(temp_exclude_file)
            except:
                pass

def sync_files(files: List[str], target: str, description: str, dry_run: bool = False):
    """Copy specific files to target directory"""
    print(f"\n→ {description}")
    print(f"  → {target}")

    # Filter to only existing, readable files
    valid_files = [f for f in files
                   if isfile(f) and access(f, R_OK)]

    if not valid_files:
        stats.add_skipped(description, "No valid files found")
        return False

    try:
        os.makedirs(target, exist_ok=True)

        for f in valid_files:
            if dry_run:
                print(f"  [DRY RUN] Would copy: {f}")
            else:
                # Use rsync for consistency
                bu.xrsync(f, target)

        print(f"  ✓ Copied {len(valid_files)} file(s)")
        return True

    except Exception as e:
        stats.add_error(description, str(e))
        print(f"  ✗ Error: {e}")
        return False

def sync_config_subdirs(base_source: str, subdirs: List[str], target: str,
                       description: str, exclude_patterns: List[str] = None,
                       dry_run: bool = False):
    """Sync specific subdirectories from a base config directory"""
    print(f"\n→ {description}")

    synced = 0
    for subdir in subdirs:
        source = os.path.join(base_source, subdir)
        if not exists(source):
            continue

        subdir_target = os.path.join(target, subdir)
        os.makedirs(os.path.dirname(subdir_target), exist_ok=True)

        print(f"  {source} → {subdir_target}")

        try:
            kwargs = {}
            if exclude_patterns:
                temp_file = write_exclude_file(exclude_patterns)
                if temp_file:
                    kwargs['ex'] = [temp_file]

            if dry_run:
                kwargs['dry_run'] = True

            bu.xrsync(source, subdir_target, **kwargs)
            synced += 1

            # Cleanup
            if 'ex' in kwargs:
                for f in kwargs['ex']:
                    if exists(f):
                        try:
                            os.unlink(f)
                        except:
                            pass
        except Exception as e:
            stats.add_error(f"{description}/{subdir}", str(e))

    if synced > 0:
        print(f"  ✓ Synced {synced}/{len(subdirs)} config directories")
        return True
    else:
        stats.add_skipped(description, "No config directories found")
        return False

def sync_all_configs(dry_run: bool = False):
    """Sync all configured backups"""
    print("\n" + "="*60)
    print(f"STARTING BACKUP - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    if dry_run:
        print("\n⚠ DRY RUN MODE - No files will be copied\n")

    create_backup_destination_tree()

    for name, config in backup_config.items():
        # Skip ex-tedium items in main backup (handled separately)
        if 'repo' in config:
            continue

        try:
            if 'files' in config:
                # File list backup
                sync_files(
                    config['files'],
                    config['target'],
                    config.get('description', name),
                    dry_run=dry_run
                )
            elif 'subdirs' in config:
                # Config subdirectories
                sync_config_subdirs(
                    config['base_source'],
                    config['subdirs'],
                    config['target'],
                    config.get('description', name),
                    exclude_patterns=config.get('exclude_patterns'),
                    dry_run=dry_run
                )
            elif 'source' in config:
                # Directory sync
                sync_directory(
                    config['source'],
                    config['target'],
                    config.get('description', name),
                    exclude_files=config.get('exclude', []) + default_excludes,
                    exclude_patterns=config.get('exclude_patterns'),
                    dry_run=dry_run
                )
        except Exception as e:
            stats.add_error(name, f"Unexpected error: {e}")
            print(f"  ✗ Unexpected error in {name}: {e}")

    return

def make_commit_message():
    """Generate commit message with timestamp"""
    t = time.ctime()
    return f"Automatic backup check in done at {t}."

def sync_personal_bkp_repo(dry_run: bool = False):
    """Sync personal backup repository"""
    print("\n" + "="*60)
    print("SYNCING PERSONAL BACKUP REPO")
    print("="*60)

    try:
        repo = bgr.get_repo(backup_target, url=repos["env"])
        sync_all_configs(dry_run=dry_run)

        if not dry_run:
            repo.show_changes()
            repo.update_repo(make_commit_message())
        else:
            print("\n[DRY RUN] Skipping git operations")
    except Exception as e:
        stats.add_error('personal_backup_repo', str(e))
        print(f"✗ Error syncing personal backup repo: {e}")

    return

def sync_notes_repo(dry_run: bool = False):
    """Sync notes repository from Windows Notes directory"""
    print("\n" + "="*60)
    print("SYNCING NOTES REPO")
    print("="*60)

    try:
        # Source: Windows Notes directory
        notes_source = os.path.join(winhome, 'Notes')
        if not exists(notes_source):
            stats.add_skipped('notes_repo', f"Notes directory doesn't exist at {notes_source}")
            print(f"⚠ Notes source not found: {notes_source}")
            return

        # Ensure backup target exists
        os.makedirs(notes_backup_target, exist_ok=True)

        # Initialize or get the git repo at backup location
        repo = bgr.get_repo(notes_backup_target, url=repos["notes"])

        # Sync Notes content from Windows to backup location
        print(f"\n→ Syncing Windows Notes")
        print(f"  {notes_source} → {notes_backup_target}")

        # Create exclude file for nested git repos and other WSL artifacts
        notes_excludes = wsl_excludes.copy()

        if not dry_run:
            sync_directory(
                notes_source + '/',  # trailing slash for rsync
                notes_backup_target + '/',
                "Windows Notes content",
                exclude_patterns=notes_excludes,
                dry_run=False
            )

            # Now commit and push
            repo.show_changes()
            repo.update_repo(make_commit_message())
        else:
            sync_directory(
                notes_source + '/',
                notes_backup_target + '/',
                "Windows Notes content",
                exclude_patterns=notes_excludes,
                dry_run=True
            )
            print("[DRY RUN] Skipping git operations")

    except Exception as e:
        stats.add_error('notes_repo', str(e))
        print(f"✗ Error syncing notes repo: {e}")
        import traceback
        traceback.print_exc()

    return

def sync_ex_tedium_repo(dry_run: bool = False):
    """Sync ex-tedium repository"""
    print("\n" + "="*60)
    print("SYNCING EX-TEDIUM REPO")
    print("="*60)

    try:
        d = os.path.expanduser('~/ex-tedium')
        repo = bgr.get_repo(d, url=repos["extedium"])

        # Sync ex-tedium specific configs
        for name, config in backup_config.items():
            if config.get('repo') == 'extedium':
                if 'source' in config:
                    sync_directory(
                        config['source'],
                        config['target'],
                        config.get('description', name),
                        exclude_patterns=config.get('exclude_patterns'),
                        dry_run=dry_run
                    )

        if not dry_run:
            repo.show_changes()
            repo.update_repo(make_commit_message())
        else:
            print("[DRY RUN] Skipping git operations")
    except Exception as e:
        stats.add_error('ex_tedium_repo', str(e))
        print(f"✗ Error syncing ex-tedium repo: {e}")

    return

def main():
    """Main entry point"""
    # Parse command line arguments
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv
    help_requested = '--help' in sys.argv or '-h' in sys.argv

    if help_requested:
        print(f"""
Personal Backup Script - Enhanced for WSL

Usage: pbkp.py [OPTIONS]

Options:
  -n, --dry-run    Show what would be backed up without copying
  -h, --help       Show this help message

This script backs up:
  - Shell utilities and scripts from ~/bin/
  - Configuration files (.emacs.d, dotfiles, ~/.config)
  - Python libraries from ~/ex-tedium/lib/bantu/
  - Windows Notes from $WINHOME/Notes/
  - Application configs
  - And syncs to git repositories

Current Configuration:
  HOME: {home}
  WINHOME: {winhome}
  Backup root: {backup_root}
  Notes source: {os.path.join(winhome, 'Notes')}

The script intelligently excludes:
  - .git directories
  - node_modules, vendor directories
  - Python virtual environments (__pycache__, venv, .venv)
  - Build artifacts (dist, build, .terraform)
  - Temporary files (.swp, .swo, vim swap files)
  - .claude directories

Repositories:
  - Personal env: {repos['env']}
  - Notes: {repos['notes']}
  - Ex-tedium: {repos['extedium']}
""")
        return 0

    try:
        # Run all backups
        sync_personal_bkp_repo(dry_run=dry_run)
        sync_notes_repo(dry_run=dry_run)
        sync_ex_tedium_repo(dry_run=dry_run)

        # Print summary
        stats.print_summary()

        return 0 if not stats.errors else 1

    except KeyboardInterrupt:
        print("\n\n⚠ Backup interrupted by user")
        stats.print_summary()
        return 130
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
