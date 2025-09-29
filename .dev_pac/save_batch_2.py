#!/usr/bin/env python3
"""
Automated save for batch 2 (15 papers).
"""

import subprocess
import time

def save_batch_2():
    """Save batch 2 papers automatically."""
    
    print("=" * 60)
    print("AUTOMATED ZOTERO SAVE - BATCH 2")
    print("=" * 60)
    print("Processing 15 papers (16-30)")
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
    successful = 0
    for i in range(15):
        paper_num = i + 16  # Papers 16-30
        print(f"Paper {paper_num:2}: ", end='', flush=True)
        
        # Wait for page
        time.sleep(3)
        
        # Trigger Zotero save
        subprocess.run(['xdotool', 'key', 'ctrl+shift+s'], capture_output=True)
        print("Saving", end='', flush=True)
        
        # Wait for save (longer for PDFs)
        for j in range(6):
            time.sleep(1)
            print(".", end='', flush=True)
        
        print(" ✓")
        successful += 1
        
        # Next tab
        if i < 14:
            subprocess.run(['xdotool', 'key', 'ctrl+Tab'], capture_output=True)
            time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print(f"✅ BATCH 2 COMPLETE!")
    print(f"Processed {successful} papers (16-30)")
    print("\nCheck Zotero library for saved items")
    print("=" * 60)
    
    return successful

if __name__ == "__main__":
    save_batch_2()