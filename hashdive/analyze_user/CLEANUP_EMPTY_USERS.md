# Cleanup Empty Users Script

## Purpose

This script identifies and deletes user JSON files that have empty `trader_types` arrays, along with their associated log folders. These are users for which the hashdive.com server returned no meaningful data (likely due to authentication issues, rate limiting, or users with no trading activity).

## Why Clean These Up?

Users with `trader_types = []` have no useful data for analysis:
- No trader classification
- Likely missing other important fields
- Take up disk space unnecessarily
- Will skew your data analysis (294 users with no data out of ~600 fetched)

## Usage

### 1. List Empty Users (No Deletion)

See which users have empty trader_types:

```bash
python3 hashdive/analyze_user/cleanup_empty_users.py --list
```

**Output:**
```
Found 294 users with empty trader_types:
======================================================================
   1. 0x9bcab737696b730f21a886cb2bb9a06b7979fdb2
   2. 0x4258dacda33c81c6ca212bb861dffd9cfa3ec11b
   ...
```

### 2. Dry Run (See What Would Be Deleted)

Preview what will be deleted without actually deleting:

```bash
python3 hashdive/analyze_user/cleanup_empty_users.py --dry-run
```

**Output:**
```
Scanning user files in: data/users
Mode: DRY RUN (no files will be deleted)
======================================================================

Found 600 user JSON files

Results:
  - Total users scanned: 600
  - Users with empty trader_types: 294
  - Errors reading files: 0

======================================================================
Users to be deleted (294):
======================================================================

1. 0x9bcab737696b730f21a886cb2bb9a06b7979fdb2
   JSON: data/users/0x9bcab737696b730f21a886cb2bb9a06b7979fdb2.json
   Logs: logs/user_data/0x9bcab737696b730f21a886cb2bb9a06b7979fdb2 (139 files)

[DRY RUN] Would delete JSON: data/users/0x9bcab737696b730f21a886cb2bb9a06b7979fdb2.json
[DRY RUN] Would delete log folder: logs/user_data/0x9bcab737696b730f21a886cb2bb9a06b7979fdb2 (139 files)
...
```

### 3. Delete with Confirmation (Recommended)

Delete empty users with a confirmation prompt:

```bash
python3 hashdive/analyze_user/cleanup_empty_users.py
```

**You will be prompted:**
```
Delete 294 users and their logs? (yes/no):
```

Type `yes` to proceed, anything else to cancel.

### 4. Delete Without Confirmation (Use with Caution!)

Delete immediately without prompting:

```bash
python3 hashdive/analyze_user/cleanup_empty_users.py --force
```

⚠️ **Warning:** This will delete files immediately without asking!

### 5. Custom Directories

If your files are in different locations:

```bash
python3 hashdive/analyze_user/cleanup_empty_users.py \
  --users-dir path/to/users \
  --logs-dir path/to/logs
```

## What Gets Deleted

For each user with `trader_types = []`:

1. **JSON file**: `data/users/0x<address>.json`
2. **Log folder**: `logs/user_data/0x<address>/` (contains all message JSON files)

## Example Output (Actual Deletion)

```bash
$ python3 hashdive/analyze_user/cleanup_empty_users.py

Scanning user files in: data/users
Mode: LIVE (files will be deleted)
======================================================================

Found 600 user JSON files

Results:
  - Total users scanned: 600
  - Users with empty trader_types: 294
  - Errors reading files: 0

======================================================================
Users to be deleted (294):
======================================================================
[... list of users ...]

======================================================================

Delete 294 users and their logs? (yes/no): yes

======================================================================
Processing deletions...
======================================================================
✓ Deleted JSON: 0x9bcab737696b730f21a886cb2bb9a06b7979fdb2
✓ Deleted logs: 0x9bcab737696b730f21a886cb2bb9a06b7979fdb2
✓ Deleted JSON: 0x4258dacda33c81c6ca212bb861dffd9cfa3ec11b
✓ Deleted logs: 0x4258dacda33c81c6ca212bb861dffd9cfa3ec11b
...

======================================================================
SUMMARY
======================================================================
Deleted:
  - JSON files: 294 (failed: 0)
  - Log folders: 294 (failed: 0)

✓ Cleanup complete!
```

## Current Status

Based on your data:
- **Total users fetched**: ~600
- **Users with empty trader_types**: 294 (49%)
- **Valid users for analysis**: ~306 (51%)

## Why So Many Empty Users?

Looking at your logs, all users fetched after 12:29pm on Nov 28 received 0 messages due to expired cookies/authentication. This is why you have so many empty users.

**Recommendation:**
1. Delete these 294 empty users
2. Refresh your cookies (see `CONNECTION_ISSUE.md`)
3. Re-fetch these users with valid authentication
4. You'll then have complete data for all 1000 users

## Impact on Your Analysis

**Before cleanup:**
- 600 users total
- 294 with no data (will cause issues in analysis)
- Mean/median calculations will be skewed
- Correlation analysis will fail for empty users

**After cleanup:**
- 306 valid users
- All have complete data
- Clean dataset for EDA and hypothesis testing
- Can re-fetch the missing 694 users later

## Safety Features

✅ **Dry run mode** - Preview before deleting
✅ **Confirmation prompt** - Requires explicit "yes"
✅ **Detailed logging** - Shows what's being deleted
✅ **Error handling** - Continues even if some deletions fail
✅ **List mode** - View empty users without any risk

## Recommendations

1. **Always run `--list` first** to see what will be deleted
2. **Use `--dry-run`** to preview the operation
3. **Backup important data** before running (optional)
4. **Fix authentication** before re-fetching (see `CONNECTION_ISSUE.md`)

## After Cleanup

Once you've deleted empty users:

1. **Verify cleanup**:
   ```bash
   python3 hashdive/analyze_user/cleanup_empty_users.py --list
   # Should show: "Found 0 users with empty trader_types"
   ```

2. **Check remaining users**:
   ```bash
   ls data/users/*.json | wc -l
   # Should show: ~306 files
   ```

3. **Refresh cookies and re-fetch**:
   ```bash
   # Test connection
   python3 hashdive/analyze_user/test_connection.py
   
   # If test passes, resume fetching
   python3 hashdive/analyze_user/fetch_multiple_users.py --offset 306 --limit 694
   ```

## Help

For more options:

```bash
python3 hashdive/analyze_user/cleanup_empty_users.py --help
```

