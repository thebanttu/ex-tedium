# Personal Backup System

Enhanced backup script for WSL environment with intelligent exclusions and git integration.

## Overview

The `bin/pbkp.py` script backs up critical configurations, scripts, and data to git repositories for version control and disaster recovery.

## Features

- **Intelligent Exclusions**: Automatically excludes common development artifacts
  - `.git` directories
  - `node_modules`, `vendor` directories
  - Python virtual environments (`venv`, `.venv`, `__pycache__`)
  - Build artifacts (`dist/`, `build/`, `.terraform/`)
  - Temporary files (`.swp`, `.swo`, vim swap files)
  - `.claude` directories

- **Multi-Repository Support**: Syncs to three git repositories
  - Personal environment backup (configs, scripts, libs)
  - Notes repository
  - Ex-tedium repository (this repo)

- **Error Handling**: Graceful error handling with detailed summary
- **Dry Run Mode**: Test backups without copying files
- **Statistics**: Shows what was backed up, skipped, and any errors

## Usage

### Basic backup
```bash
./bin/pbkp.py
```

### Dry run (test without copying)
```bash
./bin/pbkp.py --dry-run
# or
./bin/pbkp.py -n
```

### Help
```bash
./bin/pbkp.py --help
```

## What Gets Backed Up

### Personal Environment Backup (`~/Projects/backup/env/`)

1. **Shell Utilities** (`~/bin/`)
   - Deployment scripts
   - Custom shell utilities
   - Development helpers

2. **Python Libraries** (`~/Projects/code/python/private/bantu/`)
   - Personal Python libraries
   - Utility modules

3. **Configuration Files**
   - **Emacs**: `~/.emacs.d/`
   - **Dotfiles**: `.gitconfig`, `.zshrc`, `.bashrc`, `.tmux.conf`, etc.
   - **App Configs**: Selected configs from `~/.config/`
     - `claude-code`
     - `git`
     - `ranger`
     - `cursor`
   - **MPV**: `~/.config/mpv/`
   - **SSH**: `~/.ssh/` (if exists)
   - **Exclude lists**: `~/.excludes/`

4. **Package List**: `~/.pkg-list.txt`

### Notes Repository (`~/Projects/backup/notes/`)
- **Source**: `$WINHOME/Notes/` (Windows Notes directory)
  - Typically `/mnt/c/Users/ADMIN/Notes/`
  - Includes all subdirectories: `org/`, `My-Notes/`, `meetings/`, etc.
- **Target**: `~/Projects/backup/notes/`
- **Git Repo**: `git@github.com:thebanttu/my-org.git`
- Personal notes, org files, meeting notes, and documentation
- **Important**: Automatically excludes nested `.git` directories to avoid conflicts
  - Your `org/` subdirectory may have its own `.git` folder
  - The backup script will sync the content but skip the nested git repo
  - This prevents repository-within-repository issues

### Ex-tedium Repository (this repo)
- Commits any local changes to the ex-tedium repository
- **Deploys** tools FROM ex-tedium TO home directories:
  - `ex-tedium/bin/` → `~/bin/` (installs/updates scripts)
  - `ex-tedium/files/` → `~/.excludes/` (installs exclude files)
- Uses `rsync --update` to only copy if source is newer
- This prevents ex-tedium from being clobbered by older versions in ~/bin/

## Directory Structure

After backup, the structure looks like:
```
~/Projects/backup/env/
├── bin/                    # Shell utilities
├── lib/                    # Python libraries
├── config/
│   ├── emacs/             # Emacs config
│   ├── dotfiles/          # Essential dotfiles
│   ├── app-configs/       # Application configs
│   │   ├── claude-code/
│   │   ├── git/
│   │   ├── ranger/
│   │   └── cursor/
│   ├── mpv/               # MPV config
│   ├── ssh/               # SSH config
│   └── pkg/               # Package list
└── exclude/               # Rsync exclude lists
```

## Configuration

### Environment Variables

The script uses these environment variables:
- `HOME`: Your Linux home directory (automatically set)
- `WINHOME`: Your Windows home directory in WSL (default: `/mnt/c/Users/ADMIN`)
  - Set this if your Windows username differs
  - Example: `export WINHOME=/mnt/c/Users/YourUsername`

### Customization

Edit `bin/pbkp.py` to customize:

### Git Repositories
```python
repos = {
    "env": "git@github.com:thebanttu/bantu-env.git",
    "notes": "git@gitlab.com:thebanttu/my-org.git",
    "extedium": "git@github.com:thebanttu/ex-tedium.git",
}
```

### Backup Items
The `backup_config` dictionary in the script controls what gets backed up. Each entry has:
- `source`: Source directory or file
- `target`: Destination directory
- `description`: Human-readable description
- `exclude`: Optional list of exclude files
- `exclude_patterns`: Optional list of patterns to exclude
- `files`: Optional list of specific files (instead of `source`)

### Adding New Backups

To add a new backup item:

```python
backup_config = {
    # ... existing items ...

    'my_new_backup': {
        'source': home + '/my/source/dir/',
        'target': backup_target + '/my/target/',
        'description': 'My important files',
        'exclude_patterns': wsl_excludes,  # Use common WSL excludes
    },
}
```

## Exclude Patterns

### WSL-Specific Excludes
The script automatically excludes:
- Development dependencies (`node_modules`, `vendor`)
- Virtual environments
- Build artifacts
- Cache directories
- Git repositories (nested `.git` dirs)
- Temporary editor files
- `.claude` directories

### Custom Excludes
Custom exclude files in `~/.excludes/`:
- `junk.txt`: General junk patterns
- `emacs.exclude.txt`: Emacs-specific excludes
- `media.exclude.txt`: Media file patterns

## Best Practices

1. **Run Regularly**: Set up a cron job or run manually
   ```bash
   # Example cron: daily at 2 AM
   0 2 * * * /home/bantu/ex-tedium/bin/pbkp.py
   ```

2. **Test First**: Use `--dry-run` when changing config

3. **Check Summary**: Review the backup summary for errors

4. **Selective Backup**: Most git repos don't need backing up
   - They're already version-controlled
   - Only backup non-git work or unique configs

5. **SSH Keys**: Be careful backing up private keys
   - Consider using encrypted storage
   - Or rely on key regeneration

## Troubleshooting

### Git Authentication Errors
Ensure SSH keys are set up for GitHub/GitLab:
```bash
ssh -T git@github.com
ssh -T git@gitlab.com
```

### Permission Errors
Check file permissions on source directories:
```bash
ls -la ~/bin/
ls -la ~/.ssh/
```

### Internet Connection
The script checks for internet before git operations. Ensure you have connectivity for:
- Cloning repos (first run)
- Pushing changes
- Fetching updates

### Missing Directories
The script gracefully skips missing directories and reports them in the summary.

## Dependencies

- Python 3.6+
- `GitPython` (auto-installed)
- `rsync` (system command)
- SSH keys for git repos
- Custom `bantu.utils` library

## Exit Codes

- `0`: Success
- `1`: Errors occurred (check summary)
- `130`: Interrupted by user (Ctrl+C)

## Future Enhancements

Consider adding:
- Selective project backup from `~/Projects`
- Database dumps
- Encrypted backup support
- Remote backup targets (not just git)
- Incremental backup tracking
- Compression options
