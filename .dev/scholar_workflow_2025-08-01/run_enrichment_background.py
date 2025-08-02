#!/usr/bin/env python3
"""Run enrichment in background."""

import subprocess
import sys
import time
from pathlib import Path

def main():
    # Run enrichment in background
    log_file = "enrichment_full.log"
    
    print(f"Starting enrichment process in background...")
    print(f"Output will be logged to: {log_file}")
    print(f"This may take several minutes due to rate limiting...")
    
    # Run the enrichment script
    with open(log_file, 'w') as log:
        process = subprocess.Popen(
            [sys.executable, '.dev/enrich_with_monitoring.py'],
            stdout=log,
            stderr=subprocess.STDOUT
        )
    
    print(f"Process started with PID: {process.pid}")
    print(f"You can monitor progress with: tail -f {log_file}")
    
    # Wait a bit to see initial output
    time.sleep(5)
    
    # Show first few lines of log
    with open(log_file, 'r') as log:
        lines = log.readlines()[:20]
        if lines:
            print("\nInitial output:")
            print(''.join(lines))
    
    print(f"\nEnrichment running in background (PID: {process.pid})")
    print("Continuing with other tasks...")

if __name__ == "__main__":
    main()