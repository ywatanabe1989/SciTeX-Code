#!/usr/bin/env python3
"""
Automated save for the current Chrome tabs.
No interaction required - just runs the automation.
"""

import subprocess
import time

def automated_save_batch(num_tabs=15):
    """Save all open tabs automatically."""
    
    print("=" * 60)
    print("AUTOMATED ZOTERO SAVE - BATCH 1")
    print("=" * 60)
    print(f"Processing {num_tabs} tabs")
    print("\n⚠️  DO NOT TOUCH KEYBOARD/MOUSE!")
    print("\nStarting in 3 seconds...")
    
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    print("\n🤖 AUTOMATION RUNNING\n")
    
    # Focus Chrome
    subprocess.run(['xdotool', 'search', '--name', 'Google Chrome', 'windowactivate'],
                   capture_output=True)
    time.sleep(1)
    
    # Go to first tab
    subprocess.run(['xdotool', 'key', 'ctrl+1'], capture_output=True)
    time.sleep(2)
    
    # Process each tab
    for i in range(num_tabs):
        print(f"Tab {i+1:2}/{num_tabs}: ", end='', flush=True)
        
        # Wait for page to stabilize
        time.sleep(3)
        
        # Trigger Zotero save
        subprocess.run(['xdotool', 'key', 'ctrl+shift+s'], capture_output=True)
        print("Saving", end='', flush=True)
        
        # Wait for save to complete (longer for PDFs)
        for j in range(6):
            time.sleep(1)
            print(".", end='', flush=True)
        
        print(" ✓")
        
        # Next tab
        if i < num_tabs - 1:
            subprocess.run(['xdotool', 'key', 'ctrl+Tab'], capture_output=True)
            time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("✅ BATCH 1 COMPLETE!")
    print(f"Processed {num_tabs} papers")
    print("\nCheck Zotero library for saved items")
    print("=" * 60)

if __name__ == "__main__":
    automated_save_batch(15)