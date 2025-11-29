#!/usr/bin/env python3
"""
Utility script to clean up old or oversized log files.
This can be run manually if you need to free up space.
"""
import os
import argparse
from datetime import datetime, timedelta

def get_file_size_mb(filepath):
    """Get file size in megabytes."""
    return os.path.getsize(filepath) / (1024 * 1024)

def cleanup_logs(log_dir="logs", max_age_days=None, max_size_mb=None, dry_run=False):
    """
    Clean up log files based on age or size criteria.
    
    Args:
        log_dir: Directory containing log files
        max_age_days: Delete files older than this many days
        max_size_mb: Delete files larger than this size in MB
        dry_run: If True, only print what would be deleted
    """
    if not os.path.exists(log_dir):
        print(f"Log directory '{log_dir}' does not exist.")
        return
    
    deleted_count = 0
    freed_space_mb = 0
    
    for filename in os.listdir(log_dir):
        if not filename.endswith('.log'):
            continue
        
        filepath = os.path.join(log_dir, filename)
        
        if not os.path.isfile(filepath):
            continue
        
        should_delete = False
        reason = ""
        
        # Check age
        if max_age_days:
            file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            age_days = (datetime.now() - file_mtime).days
            if age_days > max_age_days:
                should_delete = True
                reason = f"older than {max_age_days} days (age: {age_days} days)"
        
        # Check size
        if max_size_mb:
            file_size_mb = get_file_size_mb(filepath)
            if file_size_mb > max_size_mb:
                should_delete = True
                reason = f"larger than {max_size_mb} MB (size: {file_size_mb:.2f} MB)"
        
        if should_delete:
            file_size_mb = get_file_size_mb(filepath)
            if dry_run:
                print(f"[DRY RUN] Would delete: {filename} ({file_size_mb:.2f} MB) - {reason}")
            else:
                try:
                    os.remove(filepath)
                    print(f"Deleted: {filename} ({file_size_mb:.2f} MB) - {reason}")
                    deleted_count += 1
                    freed_space_mb += file_size_mb
                except Exception as e:
                    print(f"Error deleting {filename}: {e}")
    
    if not dry_run and deleted_count > 0:
        print(f"\nTotal: Deleted {deleted_count} files, freed {freed_space_mb:.2f} MB")
    elif dry_run:
        print(f"\n[DRY RUN] Would delete {deleted_count} files")
    else:
        print("\nNo files to delete based on criteria.")

def list_logs(log_dir="logs"):
    """List all log files with their sizes."""
    if not os.path.exists(log_dir):
        print(f"Log directory '{log_dir}' does not exist.")
        return
    
    log_files = []
    total_size_mb = 0
    
    for filename in os.listdir(log_dir):
        if not filename.endswith('.log'):
            continue
        
        filepath = os.path.join(log_dir, filename)
        
        if not os.path.isfile(filepath):
            continue
        
        size_mb = get_file_size_mb(filepath)
        mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
        age_days = (datetime.now() - mtime).days
        
        log_files.append({
            'name': filename,
            'size_mb': size_mb,
            'age_days': age_days,
            'modified': mtime
        })
        total_size_mb += size_mb
    
    # Sort by size (largest first)
    log_files.sort(key=lambda x: x['size_mb'], reverse=True)
    
    print(f"\nLog files in '{log_dir}':")
    print(f"{'Filename':<50} {'Size (MB)':<12} {'Age (days)':<12} {'Modified':<20}")
    print("-" * 94)
    
    for log in log_files:
        print(f"{log['name']:<50} {log['size_mb']:>10.2f}   {log['age_days']:>10}   {log['modified'].strftime('%Y-%m-%d %H:%M')}")
    
    print("-" * 94)
    print(f"Total: {len(log_files)} files, {total_size_mb:.2f} MB")

def main():
    parser = argparse.ArgumentParser(
        description='Manage log files - list, clean up by age or size',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all log files
  python cleanup_logs.py --list
  
  # Delete logs older than 7 days (dry run)
  python cleanup_logs.py --max-age 7 --dry-run
  
  # Delete logs larger than 500 MB
  python cleanup_logs.py --max-size 500
  
  # Delete logs older than 3 days OR larger than 1000 MB
  python cleanup_logs.py --max-age 3 --max-size 1000
        """
    )
    
    parser.add_argument('--log-dir', type=str, default='logs',
                        help='Directory containing log files (default: logs)')
    parser.add_argument('--list', action='store_true',
                        help='List all log files with sizes')
    parser.add_argument('--max-age', type=int, metavar='DAYS',
                        help='Delete files older than this many days')
    parser.add_argument('--max-size', type=float, metavar='MB',
                        help='Delete files larger than this size in MB')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be deleted without actually deleting')
    
    args = parser.parse_args()
    
    if args.list:
        list_logs(args.log_dir)
    elif args.max_age or args.max_size:
        cleanup_logs(
            log_dir=args.log_dir,
            max_age_days=args.max_age,
            max_size_mb=args.max_size,
            dry_run=args.dry_run
        )
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

