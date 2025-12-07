#!/usr/bin/env python3
"""
Restore script for personal backup system
Restores backups created by pbkp.py to a Linux environment
Supports: Fedora 43, Void Linux
"""

import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class RestoreStats:
    """Track restoration statistics"""
    def __init__(self):
        self.files_restored = 0
        self.errors = []
        self.skipped = []
        self.packages_installed = 0

    def add_error(self, item: str, error: str):
        self.errors.append((item, error))

    def add_skipped(self, item: str, reason: str):
        self.skipped.append((item, reason))

    def print_summary(self):
        print("\n" + "="*60)
        print("RESTORATION SUMMARY")
        print("="*60)
        print(f"Files/directories restored: {self.files_restored}")
        print(f"Packages installed: {self.packages_installed}")

        if self.skipped:
            print(f"\nSkipped items: {len(self.skipped)}")
            for item, reason in self.skipped[:5]:
                print(f"  - {item}: {reason}")
            if len(self.skipped) > 5:
                print(f"  ... and {len(self.skipped) - 5} more")

        if self.errors:
            print(f"\n⚠ Errors encountered: {len(self.errors)}")
            for item, error in self.errors:
                print(f"  - {item}: {error}")
        else:
            print("\n✓ Restoration completed successfully with no errors")
        print("="*60 + "\n")

stats = RestoreStats()

def detect_distro() -> Tuple[str, str]:
    """
    Detect Linux distribution
    Returns: (distro_name, package_manager)
    """
    # Try os-release first (standard)
    os_release_path = '/etc/os-release'
    if os.path.exists(os_release_path):
        with open(os_release_path, 'r') as f:
            content = f.read().lower()

            if 'fedora' in content:
                return ('fedora', 'dnf')
            elif 'void' in content:
                return ('void', 'xbps')

    # Fallback: check for package managers
    if shutil.which('dnf'):
        return ('fedora', 'dnf')
    elif shutil.which('xbps-install'):
        return ('void', 'xbps')

    return ('unknown', 'unknown')

def run_command(cmd: List[str], description: str, check=True, shell=False) -> Tuple[bool, str]:
    """
    Run a shell command and return success status
    """
    try:
        if shell and isinstance(cmd, str):
            result = subprocess.run(cmd, shell=True, check=check,
                                  capture_output=True, text=True)
        else:
            result = subprocess.run(cmd, check=check,
                                  capture_output=True, text=True)
        return (True, result.stdout)
    except subprocess.CalledProcessError as e:
        error_msg = f"Command failed: {e.stderr if e.stderr else e.stdout}"
        stats.add_error(description, error_msg)
        return (False, error_msg)
    except Exception as e:
        stats.add_error(description, str(e))
        return (False, str(e))

def restore_directory(source: str, target: str, description: str,
                     create_symlink: bool = False, backup_existing: bool = True) -> bool:
    """
    Restore a directory from backup
    """
    if not os.path.exists(source):
        stats.add_skipped(description, f"Source doesn't exist: {source}")
        return False

    print(f"\n→ Restoring {description}")
    print(f"  {source} → {target}")

    target_path = Path(target)

    # Backup existing if requested
    if backup_existing and target_path.exists():
        backup_path = str(target_path) + '.bak'
        try:
            if target_path.is_symlink():
                os.unlink(target_path)
            else:
                shutil.move(str(target_path), backup_path)
            print(f"  (Backed up existing to {backup_path})")
        except Exception as e:
            stats.add_error(description, f"Failed to backup existing: {e}")
            return False

    try:
        # Create parent directory if it doesn't exist
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if create_symlink:
            # Create symbolic link
            os.symlink(source, target)
            print(f"  ✓ Created symlink")
        else:
            # Copy directory
            if os.path.isdir(source):
                shutil.copytree(source, target, dirs_exist_ok=True,
                              symlinks=True)
            else:
                shutil.copy2(source, target)
            print(f"  ✓ Copied")

        stats.files_restored += 1
        return True

    except Exception as e:
        stats.add_error(description, str(e))
        print(f"  ✗ Error: {e}")
        return False

def restore_files(source_dir: str, target_dir: str, files: List[str],
                 description: str, backup_existing: bool = True) -> bool:
    """
    Restore specific files from backup
    """
    print(f"\n→ Restoring {description}")

    restored = 0
    for filename in files:
        source_file = os.path.join(source_dir, filename)
        target_file = os.path.join(target_dir, filename)

        if not os.path.exists(source_file):
            continue

        # Backup existing
        if backup_existing and os.path.exists(target_file):
            try:
                shutil.move(target_file, target_file + '.bak')
            except Exception as e:
                stats.add_error(f"{description}/{filename}",
                              f"Failed to backup: {e}")
                continue

        try:
            # Create parent dir if needed
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            shutil.copy2(source_file, target_file)
            print(f"  ✓ {filename}")
            restored += 1
        except Exception as e:
            stats.add_error(f"{description}/{filename}", str(e))
            print(f"  ✗ {filename}: {e}")

    if restored > 0:
        print(f"  Restored {restored}/{len(files)} files")
        stats.files_restored += restored
        return True
    else:
        stats.add_skipped(description, "No files found to restore")
        return False

def install_packages(pkg_list_file: str, distro: str, pkg_mgr: str,
                    dry_run: bool = False) -> bool:
    """
    Install packages from package list file
    """
    if not os.path.exists(pkg_list_file):
        stats.add_skipped('package_installation',
                         f"Package list not found: {pkg_list_file}")
        return False

    print(f"\n→ Installing packages from {pkg_list_file}")

    # Read package list
    with open(pkg_list_file, 'r') as f:
        packages = [line.strip() for line in f
                   if line.strip() and not line.startswith('#')]

    if not packages:
        stats.add_skipped('package_installation', "No packages in list")
        return False

    print(f"  Found {len(packages)} packages")

    if dry_run:
        print("  [DRY RUN] Would install:")
        for pkg in packages[:10]:
            print(f"    - {pkg}")
        if len(packages) > 10:
            print(f"    ... and {len(packages) - 10} more")
        return True

    # Construct install command based on distro
    if pkg_mgr == 'dnf':
        # Fedora
        cmd = ['sudo', 'dnf', 'install', '-y'] + packages
    elif pkg_mgr == 'xbps':
        # Void Linux
        cmd = ['sudo', 'xbps-install', '-Sy'] + packages
    else:
        stats.add_error('package_installation',
                       f"Unsupported package manager: {pkg_mgr}")
        return False

    print(f"  Running: {' '.join(cmd[:4])} ... ({len(packages)} packages)")

    success, output = run_command(cmd, 'package_installation', check=False)

    if success:
        print(f"  ✓ Package installation completed")
        stats.packages_installed = len(packages)
        return True
    else:
        print(f"  ✗ Package installation failed")
        print(f"     You may need to manually install packages")
        print(f"     Package list: {pkg_list_file}")
        return False

def restore_from_backup(backup_dir: str, dry_run: bool = False,
                       skip_packages: bool = False, use_symlinks: bool = False):
    """
    Main restoration function
    """
    backup_path = Path(backup_dir)
    home = os.path.expanduser('~')

    # Validate backup directory
    if not backup_path.exists():
        print(f"✗ Backup directory not found: {backup_dir}")
        return False

    print("\n" + "="*60)
    print("PERSONAL BACKUP RESTORATION")
    print("="*60)

    # Detect distro
    distro, pkg_mgr = detect_distro()
    print(f"\nDetected distribution: {distro}")
    print(f"Package manager: {pkg_mgr}")
    print(f"Backup source: {backup_dir}")
    print(f"Target home: {home}")

    if dry_run:
        print("\n⚠ DRY RUN MODE - No files will be modified\n")

    # Define restoration mappings
    restorations = []

    # 1. Dotfiles
    dotfiles_source = backup_path / 'config' / 'dotfiles'
    if dotfiles_source.exists():
        dotfiles = [
            '.gitconfig', '.rgignore', '.rtorrent.rc', '.tmux.conf',
            '.vim', '.xbindkeysrc', '.xinitrc', '.zshrc', '.Xresources',
            '.bashrc', '.profile'
        ]
        restorations.append({
            'type': 'files',
            'source_dir': str(dotfiles_source),
            'target_dir': home,
            'files': dotfiles,
            'description': 'Dotfiles'
        })

    # 2. Emacs configuration
    emacs_source = backup_path / 'config' / 'emacs'
    if emacs_source.exists():
        restorations.append({
            'type': 'directory',
            'source': str(emacs_source),
            'target': os.path.join(home, '.emacs.d'),
            'description': 'Emacs configuration',
            'symlink': use_symlinks
        })

    # 3. App configs (claude-code, git, ranger, cursor)
    app_configs_source = backup_path / 'config' / 'app-configs'
    if app_configs_source.exists():
        for app_dir in app_configs_source.iterdir():
            if app_dir.is_dir():
                restorations.append({
                    'type': 'directory',
                    'source': str(app_dir),
                    'target': os.path.join(home, '.config', app_dir.name),
                    'description': f'Config: {app_dir.name}',
                    'symlink': use_symlinks
                })

    # 4. MPV configuration
    mpv_source = backup_path / 'config' / 'mpv'
    if mpv_source.exists():
        restorations.append({
            'type': 'directory',
            'source': str(mpv_source),
            'target': os.path.join(home, '.config', 'mpv'),
            'description': 'MPV configuration',
            'symlink': use_symlinks
        })

    # 5. SSH configuration
    ssh_source = backup_path / 'config' / 'ssh'
    if ssh_source.exists():
        restorations.append({
            'type': 'directory',
            'source': str(ssh_source),
            'target': os.path.join(home, '.ssh'),
            'description': 'SSH configuration',
            'symlink': use_symlinks
        })

    # 6. Shell utilities (bin)
    bin_source = backup_path / 'bin'
    if bin_source.exists():
        restorations.append({
            'type': 'directory',
            'source': str(bin_source),
            'target': os.path.join(home, 'bin'),
            'description': 'Shell utilities',
            'symlink': use_symlinks
        })

    # 7. Python libraries
    lib_source = backup_path / 'lib'
    if lib_source.exists():
        # Determine where to put Python libraries
        # Option 1: Put in ex-tedium if it exists
        ex_tedium = os.path.join(home, 'ex-tedium')
        if os.path.exists(ex_tedium):
            lib_target = os.path.join(ex_tedium, 'lib', 'bantu')
        else:
            # Option 2: Put in a generic location
            lib_target = os.path.join(home, '.local', 'lib', 'python', 'bantu')

        restorations.append({
            'type': 'directory',
            'source': str(lib_source),
            'target': lib_target,
            'description': 'Python libraries',
            'symlink': use_symlinks
        })

    # 8. Exclude lists
    exclude_source = backup_path / 'exclude'
    if exclude_source.exists():
        restorations.append({
            'type': 'directory',
            'source': str(exclude_source),
            'target': os.path.join(home, '.excludes'),
            'description': 'Exclude lists',
            'symlink': use_symlinks
        })

    # Execute restorations
    if not dry_run:
        for item in restorations:
            if item['type'] == 'directory':
                restore_directory(
                    item['source'],
                    item['target'],
                    item['description'],
                    create_symlink=item.get('symlink', False)
                )
            elif item['type'] == 'files':
                restore_files(
                    item['source_dir'],
                    item['target_dir'],
                    item['files'],
                    item['description']
                )
    else:
        print("\n[DRY RUN] Would restore:")
        for item in restorations:
            print(f"  - {item['description']}: {item.get('source', item.get('source_dir'))}")

    # Fix SSH permissions
    ssh_dir = os.path.join(home, '.ssh')
    if not dry_run and os.path.exists(ssh_dir):
        print("\n→ Fixing SSH permissions")
        try:
            os.chmod(ssh_dir, 0o700)
            for file in os.listdir(ssh_dir):
                filepath = os.path.join(ssh_dir, file)
                if os.path.isfile(filepath):
                    # Private keys should be 600, public keys 644
                    if file.endswith('.pub') or file == 'known_hosts' or file == 'config':
                        os.chmod(filepath, 0o644)
                    else:
                        os.chmod(filepath, 0o600)
            print("  ✓ SSH permissions fixed")
        except Exception as e:
            stats.add_error('ssh_permissions', str(e))

    # Install packages
    if not skip_packages and pkg_mgr != 'unknown':
        pkg_list = backup_path / 'config' / 'pkg' / '.pkg-list.txt'
        if pkg_list.exists():
            install_packages(str(pkg_list), distro, pkg_mgr, dry_run=dry_run)
        else:
            stats.add_skipped('package_installation',
                            'Package list not found in backup')

    return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Restore personal backup to Linux environment',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Restore from default backup location
  %(prog)s

  # Restore from custom backup directory
  %(prog)s -b /path/to/backup/env

  # Dry run to see what would be restored
  %(prog)s --dry-run

  # Restore but skip package installation
  %(prog)s --skip-packages

  # Use symlinks instead of copying files
  %(prog)s --symlinks

Supported distributions:
  - Fedora 43 (dnf)
  - Void Linux (xbps)
        """
    )

    parser.add_argument('-b', '--backup-dir',
                       default=os.path.expanduser('~/Projects/backup/env'),
                       help='Backup directory to restore from (default: ~/Projects/backup/env)')
    parser.add_argument('-n', '--dry-run', action='store_true',
                       help='Show what would be restored without making changes')
    parser.add_argument('--skip-packages', action='store_true',
                       help='Skip package installation')
    parser.add_argument('--symlinks', action='store_true',
                       help='Create symlinks instead of copying files')

    args = parser.parse_args()

    try:
        # Expand user path
        backup_dir = os.path.expanduser(args.backup_dir)

        # Run restoration
        restore_from_backup(
            backup_dir,
            dry_run=args.dry_run,
            skip_packages=args.skip_packages,
            use_symlinks=args.symlinks
        )

        # Print summary
        stats.print_summary()

        return 0 if not stats.errors else 1

    except KeyboardInterrupt:
        print("\n\n⚠ Restoration interrupted by user")
        stats.print_summary()
        return 130
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
