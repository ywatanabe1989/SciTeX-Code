#!/usr/bin/env python3
"""
Simple automated Zotero Connector saves using keyboard shortcuts.
Uses xdotool to automate: Tab switch → Ctrl+Shift+S → Wait → Repeat
"""

import subprocess
import time
import sys

def run_automation(num_tabs=15, wait_time=4):
    """
    Automate Zotero saves across Chrome tabs.
    
    Args:
        num_tabs: Number of tabs to process
        wait_time: Seconds to wait after each save
    """
    
    print("=" * 80)
    print("ZOTERO AUTOMATED SAVE")
    print("=" * 80)
    print(f"\nWill process {num_tabs} tabs")
    print(f"Wait time per save: {wait_time} seconds")
    print("\n⚠️  DO NOT TOUCH KEYBOARD/MOUSE DURING AUTOMATION!")
    print("\nStarting in 5 seconds...")
    print("Position Chrome window now!")
    
    for i in range(5, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    print("\n🤖 AUTOMATION RUNNING - HANDS OFF!\n")
    
    # Focus Chrome window
    subprocess.run(['xdotool', 'search', '--name', 'Google Chrome', 'windowactivate'], 
                   capture_output=True)
    time.sleep(1)
    
    # Go to first tab (Ctrl+1)
    print("Going to first tab...")
    subprocess.run(['xdotool', 'key', 'ctrl+1'], capture_output=True)
    time.sleep(2)
    
    # Process each tab
    for i in range(num_tabs):
        print(f"\nTab {i+1}/{num_tabs}:")
        
        # Wait for page to be ready
        print("  Waiting for page...")
        time.sleep(2)
        
        # Trigger Zotero Connector (Ctrl+Shift+S)
        print("  Saving with Zotero (Ctrl+Shift+S)...")
        subprocess.run(['xdotool', 'key', 'ctrl+shift+s'], capture_output=True)
        
        # Wait for save to complete
        print(f"  Waiting {wait_time}s for save to complete...")
        time.sleep(wait_time)
        
        # Move to next tab (Ctrl+Tab)
        if i < num_tabs - 1:
            print("  Next tab (Ctrl+Tab)...")
            subprocess.run(['xdotool', 'key', 'ctrl+Tab'], capture_output=True)
            time.sleep(0.5)
    
    print("\n" + "=" * 80)
    print("✅ AUTOMATION COMPLETE!")
    print(f"Processed {num_tabs} tabs")
    print("\nCheck your Zotero library for saved items.")
    print("PDFs should be downloading with institutional access.")
    print("=" * 80)

def main():
    """Main entry point."""
    
    # Check for xdotool
    try:
        subprocess.run(['which', 'xdotool'], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("ERROR: xdotool not installed!")
        print("Install with: sudo apt-get install xdotool")
        sys.exit(1)
    
    print("Zotero Batch Save Automation")
    print("-" * 40)
    print("\nPre-flight checklist:")
    print("✓ Chrome is open with paper tabs")
    print("✓ Zotero Desktop is running") 
    print("✓ Zotero WSL Proxy is active")
    print("✓ You're logged into institutional access")
    print("✓ Zotero Connector extension is installed")
    
    # Get number of tabs
    try:
        num_tabs = input("\nHow many tabs to process? (default: 15): ").strip()
        num_tabs = int(num_tabs) if num_tabs else 15
    except ValueError:
        num_tabs = 15
    
    # Get wait time
    try:
        wait_time = input("Seconds to wait per save? (default: 4): ").strip()
        wait_time = int(wait_time) if wait_time else 4
    except ValueError:
        wait_time = 4
    
    print(f"\nWill process {num_tabs} tabs with {wait_time}s wait per save")
    print(f"Total time: ~{num_tabs * (wait_time + 3)} seconds")
    
    response = input("\nReady to start? (y/n): ").strip().lower()
    if response == 'y':
        run_automation(num_tabs, wait_time)
    else:
        print("Cancelled.")

if __name__ == "__main__":
    main()