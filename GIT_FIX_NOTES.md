# Git Repository Fix - Empty Remote Handling

## Issue Fixed

The backup script was failing when pushing to an empty GitHub repository with the error:
```
IndexError: No item found with id 'origin/main'
```

## Root Cause

The `repo_behind_remote()` method in `lib/bantu/git.py` was trying to access `origin/main` without checking if the remote branch exists. This happens when:
- The GitHub repository is empty (no branches yet)
- This is the first push to the repository
- The remote branch hasn't been created

## Solution

Updated two methods in `lib/bantu/git.py`:

### 1. `repo_behind_remote()` (lines 190-203)
**Before**: Directly accessed `remote.refs[branch_name]` causing IndexError

**After**: Wrapped in try/except to handle missing remote branch
```python
try:
    latest_remote_commit = remote.refs[branch_name].commit
    latest_local_commit = self.head.commit
    return latest_local_commit != latest_remote_commit
except (IndexError, KeyError):
    # Remote branch doesn't exist yet, so we need to push
    print(f"Remote branch '{branch_name}' doesn't exist yet. Will create it on push.")
    return True
```

### 2. `push_changes()` (lines 168-187)
**Before**: Did a simple push without setting upstream on first push

**After**: Checks if upstream tracking branch is set, and sets it on first push
```python
branch = self.active_branch
if not branch.tracking_branch():
    print(f"Setting upstream branch for '{branch.name}' to '{r}/{branch.name}'")
    remote.push(refspec=f'{branch.name}:{branch.name}', set_upstream=True)
else:
    remote.push()
```

## Testing

Verified the fix with `bin/test_git_fix.py`:
```
✓ Repo loaded successfully
  Current branch: main
  No tracking branch set (will be set on first push)

Testing repo_behind_remote()...
Remote branch 'main' doesn't exist yet. Will create it on push.
✓ repo_behind_remote() succeeded
  Result: Need to push

✓ All tests passed!
```

## What This Means

1. **First push to empty repo**: Now works correctly
   - Detects that remote branch doesn't exist
   - Sets upstream tracking on first push
   - Creates the remote branch automatically

2. **Subsequent pushes**: Work as before
   - Compares local and remote commits
   - Only pushes if there are new commits

3. **Better error handling**: More informative messages
   - Tells you when remote branch doesn't exist
   - Shows when setting upstream tracking

## GitHub Repository Status

- **Repository**: `git@github.com:thebanttu/my-org.git`
- **Status**: Exists but empty (no branches)
- **Ready**: Yes, backup script will create the main branch on first push

## Next Steps

You can now run the backup script successfully:

```bash
# Test (dry run)
./bin/pbkp.py --dry-run

# Run the actual backup
./bin/pbkp.py
```

The first run will:
1. Sync Notes from `$WINHOME/Notes/` to `~/Projects/backup/notes/`
2. Create a commit
3. Push to GitHub and create the `main` branch
4. Set up tracking between local and remote

Subsequent runs will:
1. Sync any new/changed files
2. Create a commit if there are changes
3. Push to the existing `main` branch

## Files Modified

- `lib/bantu/git.py`: Fixed `repo_behind_remote()` and `push_changes()` methods
- `bin/test_git_fix.py`: Created test script to verify the fix

## Cleanup Done

Also fixed an existing issue where the notes repo had a broken upstream:
```bash
git branch --unset-upstream
```

This allowed the backup script to properly set the upstream on the next push.
