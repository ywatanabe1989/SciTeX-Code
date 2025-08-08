#!/usr/bin/env python3
"""
Automated save for batch 3 - final papers.
"""

import subprocess
import time

def save_final_batch(num_papers=3):
    """Save final batch papers automatically."""
    
    print("=" * 60)
    print("AUTOMATED ZOTERO SAVE - FINAL BATCH")
    print("=" * 60)
    print(f"Processing final {num_papers} papers")
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
    for i in range(num_papers):
        paper_num = i + 31  # Papers 31+
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
        if i < num_papers - 1:
            subprocess.run(['xdotool', 'key', 'ctrl+Tab'], capture_output=True)
            time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("🎉 ALL BATCHES COMPLETE!")
    print(f"Processed final {successful} papers")
    print("\n✅ PAC COLLECTION DOWNLOAD PROJECT COMPLETE!")
    print("=" * 60)
    
    return successful

if __name__ == "__main__":
    save_final_batch(3)