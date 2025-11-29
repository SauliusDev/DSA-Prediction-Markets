#!/usr/bin/env python3
"""
Clean up user JSON files with empty trader_types and their associated log folders.

This script:
1. Scans all user JSON files in data/users/
2. Identifies users with empty trader_types (trader_types = [])
3. Deletes the JSON file
4. Deletes the associated folder in logs/user_data/
"""
import json
import os
import shutil
import argparse
from pathlib import Path

def load_user_json(filepath):
    """Load and parse a user JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def has_empty_trader_types(user_data):
    """Check if user has empty trader_types."""
    if user_data is None:
        return False
    
    trader_types = user_data.get('trader_types')
    
    # Check if trader_types exists and is an empty list
    if trader_types is not None and isinstance(trader_types, list) and len(trader_types) == 0:
        return True
    
    return False

def get_user_address_from_filename(filename):
    """Extract user address from filename (e.g., '0xabc123.json' -> '0xabc123')."""
    return filename.replace('.json', '')

def cleanup_empty_users(users_dir='data/users', logs_dir='logs/user_data', dry_run=False):
    """
    Clean up users with empty trader_types.
    
    Args:
        users_dir: Directory containing user JSON files
        logs_dir: Directory containing user log folders
        dry_run: If True, only show what would be deleted without actually deleting
    """
    if not os.path.exists(users_dir):
        print(f"Error: Users directory '{users_dir}' does not exist")
        return
    
    print(f"Scanning user files in: {users_dir}")
    print(f"Log directory: {logs_dir}")
    print(f"Mode: {'DRY RUN (no files will be deleted)' if dry_run else 'LIVE (files will be deleted)'}")
    print("=" * 70)
    
    # Get all JSON files
    json_files = [f for f in os.listdir(users_dir) if f.endswith('.json')]
    print(f"\nFound {len(json_files)} user JSON files")
    
    empty_users = []
    error_count = 0
    
    # Scan all users
    print("\nScanning for empty trader_types...")
    for filename in json_files:
        filepath = os.path.join(users_dir, filename)
        user_data = load_user_json(filepath)
        
        if user_data is None:
            error_count += 1
            continue
        
        if has_empty_trader_types(user_data):
            user_address = get_user_address_from_filename(filename)
            empty_users.append({
                'address': user_address,
                'json_file': filepath,
                'log_folder': os.path.join(logs_dir, user_address)
            })
    
    print(f"\nResults:")
    print(f"  - Total users scanned: {len(json_files)}")
    print(f"  - Users with empty trader_types: {len(empty_users)}")
    print(f"  - Errors reading files: {error_count}")
    
    if len(empty_users) == 0:
        print("\n✓ No users with empty trader_types found. Nothing to clean up.")
        return
    
    # Show what will be deleted
    print(f"\n{'='*70}")
    print(f"Users to be deleted ({len(empty_users)}):")
    print(f"{'='*70}")
    
    for i, user in enumerate(empty_users, 1):
        print(f"\n{i}. {user['address']}")
        print(f"   JSON: {user['json_file']}")
        
        log_folder = user['log_folder']
        if os.path.exists(log_folder):
            num_files = len(os.listdir(log_folder))
            print(f"   Logs: {log_folder} ({num_files} files)")
        else:
            print(f"   Logs: {log_folder} (does not exist)")
    
    # Confirm deletion
    if not dry_run:
        print(f"\n{'='*70}")
        response = input(f"\nDelete {len(empty_users)} users and their logs? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Cancelled. No files deleted.")
            return
    
    # Perform deletion
    print(f"\n{'='*70}")
    print("Processing deletions...")
    print(f"{'='*70}")
    
    deleted_json = 0
    deleted_logs = 0
    failed_json = 0
    failed_logs = 0
    
    for user in empty_users:
        user_address = user['address']
        json_file = user['json_file']
        log_folder = user['log_folder']
        
        # Delete JSON file
        try:
            if dry_run:
                print(f"[DRY RUN] Would delete JSON: {json_file}")
            else:
                os.remove(json_file)
                print(f"✓ Deleted JSON: {user_address}")
            deleted_json += 1
        except Exception as e:
            print(f"✗ Failed to delete JSON {user_address}: {e}")
            failed_json += 1
        
        # Delete log folder
        if os.path.exists(log_folder):
            try:
                if dry_run:
                    num_files = len(os.listdir(log_folder))
                    print(f"[DRY RUN] Would delete log folder: {log_folder} ({num_files} files)")
                else:
                    shutil.rmtree(log_folder)
                    print(f"✓ Deleted logs: {user_address}")
                deleted_logs += 1
            except Exception as e:
                print(f"✗ Failed to delete logs {user_address}: {e}")
                failed_logs += 1
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    
    if dry_run:
        print(f"DRY RUN - No files were actually deleted")
        print(f"Would delete:")
    else:
        print(f"Deleted:")
    
    print(f"  - JSON files: {deleted_json} (failed: {failed_json})")
    print(f"  - Log folders: {deleted_logs} (failed: {failed_logs})")
    
    if not dry_run:
        print(f"\n✓ Cleanup complete!")

def list_empty_users(users_dir='data/users'):
    """List users with empty trader_types without deleting."""
    if not os.path.exists(users_dir):
        print(f"Error: Users directory '{users_dir}' does not exist")
        return
    
    print(f"Scanning user files in: {users_dir}")
    print("=" * 70)
    
    json_files = [f for f in os.listdir(users_dir) if f.endswith('.json')]
    empty_users = []
    
    for filename in json_files:
        filepath = os.path.join(users_dir, filename)
        user_data = load_user_json(filepath)
        
        if user_data and has_empty_trader_types(user_data):
            user_address = get_user_address_from_filename(filename)
            empty_users.append(user_address)
    
    print(f"\nFound {len(empty_users)} users with empty trader_types:")
    print("=" * 70)
    
    if empty_users:
        for i, address in enumerate(empty_users, 1):
            print(f"{i:4d}. {address}")
    else:
        print("None found.")

def main():
    parser = argparse.ArgumentParser(
        description='Clean up user JSON files with empty trader_types',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List users with empty trader_types (no deletion)
  python cleanup_empty_users.py --list
  
  # Dry run - see what would be deleted
  python cleanup_empty_users.py --dry-run
  
  # Actually delete (will prompt for confirmation)
  python cleanup_empty_users.py
  
  # Delete without confirmation prompt
  python cleanup_empty_users.py --force
  
  # Custom directories
  python cleanup_empty_users.py --users-dir data/users --logs-dir logs/user_data
        """
    )
    
    parser.add_argument('--users-dir', type=str, default='data/users',
                        help='Directory containing user JSON files (default: data/users)')
    parser.add_argument('--logs-dir', type=str, default='logs/user_data',
                        help='Directory containing user log folders (default: logs/user_data)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be deleted without actually deleting')
    parser.add_argument('--list', action='store_true',
                        help='Only list users with empty trader_types, do not delete')
    parser.add_argument('--force', action='store_true',
                        help='Delete without confirmation prompt (use with caution!)')
    
    args = parser.parse_args()
    
    if args.list:
        list_empty_users(args.users_dir)
    else:
        # Override dry_run behavior if force is used
        if args.force and not args.dry_run:
            # Temporarily set dry_run to False and skip confirmation
            import sys
            # Monkey patch input to auto-confirm
            original_input = __builtins__.input
            __builtins__.input = lambda _: "yes"
            cleanup_empty_users(args.users_dir, args.logs_dir, dry_run=False)
            __builtins__.input = original_input
        else:
            cleanup_empty_users(args.users_dir, args.logs_dir, dry_run=args.dry_run)

if __name__ == "__main__":
    main()

