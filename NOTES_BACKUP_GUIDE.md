# Windows Notes Backup Guide

## Overview

Your Windows Notes directory (`$WINHOME/Notes`) is now automatically backed up to the `my-org` git repository.

## Configuration

### Source
- **Location**: `$WINHOME/Notes` (Windows filesystem)
- **Default Path**: `/mnt/c/Users/ADMIN/Notes`
- **Size**: ~5.1 MB

### Contents Backed Up
Your Notes directory contains:
- `org/` - Org-mode files (has its own .git repo - excluded)
- `My-Notes/` - Personal notes collection (has its own .git repo - excluded)
- `meetings/` - Meeting notes
- Various SQL files and other notes

### Backup Target
- **Location**: `~/Projects/backup/notes/`
- **Git Repository**: `git@github.com:thebanttu/my-org.git`

## How It Works

1. **Syncs from Windows**: The script reads directly from your Windows filesystem
2. **Intelligent Exclusion**: Automatically excludes:
   - Nested `.git` directories (prevents repo conflicts)
   - Temporary Emacs files (`#file#`, `file~`)
   - Other WSL artifacts
3. **Git Versioning**: Commits and pushes to your GitHub `my-org` repository

## Usage

### Full Backup (includes Notes)
```bash
cd ~/ex-tedium
./bin/pbkp.py
```

### Dry Run (see what would be backed up)
```bash
./bin/pbkp.py --dry-run
```

### Check Configuration
```bash
./bin/pbkp.py --help
```

This will show:
- Your current WINHOME setting
- Notes source location
- Backup target location

## Setting WINHOME

If your Windows username is different from "ADMIN", set WINHOME:

### Temporary (one-time)
```bash
WINHOME=/mnt/c/Users/YourUsername ./bin/pbkp.py
```

### Permanent
Add to your `~/.bashrc` or `~/.zshrc`:
```bash
export WINHOME=/mnt/c/Users/YourUsername
```

## What Gets Excluded

The backup automatically skips:
- `.git/` directories (your org/ and My-Notes/ have their own git repos)
- Emacs auto-save files (`#file#`)
- Backup files (`file~`)
- WSL cache and build artifacts
- `.claude/` directories

## Directory Structure After Backup

```
~/Projects/backup/notes/
├── .git/                           # my-org repository
├── org/                            # Your org files
│   ├── TODO.org
│   ├── cr-erm.org
│   ├── chess.org
│   └── ... (all your org files)
├── My-Notes/                       # Personal notes
│   ├── activities.org
│   ├── ideas.txt
│   ├── brain_dump.txt
│   └── ... (all your notes)
├── meetings/                       # Meeting notes
│   └── 2024-10-15.org
├── surebet-triggers.sql
└── surebet-triggers.sql~
```

## Checking Backup Status

### View what changed
```bash
cd ~/Projects/backup/notes
git status
git log --oneline -5
```

### View backup size
```bash
du -sh ~/Projects/backup/notes/
```

### Last backup time
```bash
cd ~/Projects/backup/notes
git log -1 --format="%ai %s"
```

## Troubleshooting

### Notes not found
```bash
# Check if WINHOME is set correctly
echo $WINHOME

# Check if Notes exists
ls -la $WINHOME/Notes
```

### Git push failures
```bash
# Verify SSH key access to GitHub
ssh -T git@github.com

# Should output: "Hi yourusername! You've successfully authenticated..."
```

### Permission issues on Windows files
```bash
# WSL sometimes has permission issues with Windows files
# The script handles this gracefully and will report errors
```

## Best Practices

1. **Regular Backups**: Run the backup script regularly
   - Set up a cron job, or
   - Run manually when you make significant changes

2. **Check the Summary**: Always review the backup summary for errors

3. **Verify Pushes**: Occasionally check GitHub to ensure pushes are succeeding

4. **Multiple Git Repos**: Your org/ subdirectory has its own git repo
   - The backup script syncs the FILES but skips the .git directory
   - You still maintain your org/ repo independently
   - The my-org backup is a separate safety net

## Example Workflow

```bash
# After working on your notes in Windows
cd ~/ex-tedium

# See what would be backed up (dry run)
./bin/pbkp.py --dry-run

# If everything looks good, run the real backup
./bin/pbkp.py

# Review the summary to ensure success
```

## Notes on Nested Git Repositories

Your `org/` and `My-Notes/` directories have their own `.git` folders. The backup handles this elegantly:

- **What's backed up**: The actual content files (.org, .txt, .sql)
- **What's excluded**: The nested `.git/` directories
- **Why**: Prevents "repository within a repository" issues

This means:
- You can continue using git in `org/` independently
- The my-org backup serves as a unified backup of all Notes content
- No git conflicts or nested submodule issues

## Integration with Existing Workflows

If you're already using git in your Windows Notes directories:
- **Continue as normal**: Keep committing and pushing in those repos
- **Additional safety**: The my-org backup provides extra protection
- **Unified view**: All your notes in one backup repository
- **Cross-machine sync**: Access all notes from any machine with access to my-org

## Summary

The backup script now provides comprehensive backup of your entire Windows Notes directory to GitHub, while intelligently handling the nested git repositories you already have. This gives you both per-directory git control AND a unified backup solution.
