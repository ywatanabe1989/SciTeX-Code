#!/usr/bin/env python3
"""Monitor enrichment progress in real-time."""

import time
import subprocess
from datetime import datetime

def get_stats():
    """Get current enrichment statistics."""
    try:
        # Count total attempts
        total = subprocess.check_output(
            "grep -c 'Trying to get abstract for:' enrichment_full.log || echo 0",
            shell=True, text=True
        ).strip()
        
        # Count successful enrichments
        success = subprocess.check_output(
            "grep -c 'Found abstract for' enrichment_full.log || echo 0",
            shell=True, text=True
        ).strip()
        
        # Get last few lines
        tail = subprocess.check_output(
            "tail -5 enrichment_full.log | grep -E '(INFO|WARNING|ERROR|Rate limited)'",
            shell=True, text=True
        ).strip()
        
        return int(total), int(success), tail
    except:
        return 0, 0, ""

def main():
    print("Monitoring enrichment progress...")
    print("Press Ctrl+C to stop\n")
    
    last_total = 0
    start_time = time.time()
    
    while True:
        total, success, tail = get_stats()
        
        # Calculate progress
        progress = (total / 75) * 100 if total > 0 else 0
        success_rate = (success / total) * 100 if total > 0 else 0
        
        # Calculate rate
        elapsed = time.time() - start_time
        if total > last_total and elapsed > 60:
            rate = (total - last_total) / (elapsed / 60)  # papers per minute
            eta_minutes = (75 - total) / rate if rate > 0 else 0
            eta_str = f"{int(eta_minutes)} min"
        else:
            eta_str = "calculating..."
        
        # Display
        print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
              f"Progress: {total}/75 ({progress:.1f}%) | "
              f"Success: {success}/{total} ({success_rate:.1f}%) | "
              f"ETA: {eta_str}", end='', flush=True)
        
        # Show activity
        if tail and total > last_total:
            print(f"\n{tail}")
            last_total = total
        
        time.sleep(10)  # Update every 10 seconds

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
    except Exception as e:
        print(f"\nError: {e}")