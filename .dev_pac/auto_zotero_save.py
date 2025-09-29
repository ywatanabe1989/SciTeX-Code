#!/usr/bin/env python3
"""
Automate Zotero Connector saves using keyboard shortcuts.
Workflow: Switch tabs → Press Ctrl+Shift+S → Wait → Repeat
"""

import subprocess
import time
import json
from pathlib import Path

def count_chrome_tabs():
    """Count open Chrome tabs to know how many to iterate through."""
    # This is approximate - we'll use the number of papers we tried to open
    return 15  # We opened 15 papers earlier

def get_papers_without_pdfs():
    """Get count of papers without PDFs for reference."""
    pac_dir = Path.home() / '.scitex/scholar/library/pac'
    count = 0
    
    for item in pac_dir.iterdir():
        if item.is_symlink():
            target_dir = item.resolve()
            if target_dir.exists():
                pdf_files = list(target_dir.glob('*.pdf'))
                metadata_file = target_dir / 'metadata.json'
                
                if not pdf_files and metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    journal = metadata.get('journal', '')
                    if 'IEEE' not in journal:
                        count += 1
    return count

def activate_chrome():
    """Activate Chrome window."""
    subprocess.run(['xdotool', 'search', '--name', 'Chrome', 'windowactivate'], 
                   capture_output=True)
    time.sleep(0.5)

def press_zotero_save():
    """Press Ctrl+Shift+S to trigger Zotero Connector."""
    subprocess.run(['xdotool', 'key', 'ctrl+shift+s'], capture_output=True)

def next_tab():
    """Switch to next Chrome tab using Ctrl+Tab."""
    subprocess.run(['xdotool', 'key', 'ctrl+Tab'], capture_output=True)

def previous_tab():
    """Switch to previous Chrome tab using Ctrl+Shift+Tab."""
    subprocess.run(['xdotool', 'key', 'ctrl+shift+Tab'], capture_output=True)

def grab_input():
    """Grab keyboard and mouse input to prevent interference."""
    # Note: This requires X11 and may need sudo for some systems
    try:
        # Grab keyboard
        subprocess.Popen(['xdotool', 'key', '--clearmodifiers', 'XF86LogGrabInfo'], 
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def ungrab_input():
    """Release keyboard and mouse input."""
    try:
        subprocess.Popen(['xdotool', 'key', 'Escape'], 
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

def auto_save_all_tabs():
    """Automatically save all open tabs using Zotero Connector."""
    
    print("=" * 80)
    print("AUTOMATED ZOTERO CONNECTOR SAVES")
    print("=" * 80)
    print("\n⚠️  AUTOMATION STARTING - DO NOT TOUCH KEYBOARD/MOUSE!")
    print("Starting in 5 seconds...")
    time.sleep(5)
    
    # Alternative: Show a warning overlay
    warning_process = subprocess.Popen([
        'zenity', '--info', 
        '--text=AUTOMATION IN PROGRESS\n\nDO NOT USE KEYBOARD OR MOUSE\n\nThis window will close when complete',
        '--title=Zotero Automation',
        '--no-wrap'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Activate Chrome
    print("\nActivating Chrome window...")
    activate_chrome()
    
    # Get to first tab (go back several times to ensure we're at the start)
    print("Going to first tab...")
    for _ in range(20):
        previous_tab()
        time.sleep(0.2)
    
    # Number of tabs to process
    num_tabs = count_chrome_tabs()
    papers_count = get_papers_without_pdfs()
    
    print(f"\nProcessing approximately {num_tabs} tabs")
    print(f"(There are {papers_count} papers without PDFs total)")
    print("-" * 40)
    
    successful_saves = 0
    
    for i in range(num_tabs):
        print(f"\nTab {i+1}/{num_tabs}:")
        
        # Give page time to load if needed
        time.sleep(2)
        
        # Press Ctrl+Shift+S to save
        print("  Pressing Ctrl+Shift+S...")
        press_zotero_save()
        
        # Wait for Zotero to process (longer for PDFs)
        print("  Waiting for Zotero to save...")
        time.sleep(5)  # Adjust based on download speed
        
        # Move to next tab
        if i < num_tabs - 1:
            print("  Moving to next tab...")
            next_tab()
            time.sleep(1)
        
        successful_saves += 1
    
    # Close warning dialog if using zenity
    try:
        warning_process.terminate()
    except:
        pass
    
    print("\n" + "=" * 80)
    print(f"COMPLETED: Attempted to save {successful_saves} papers")
    print("Please check Zotero library for saved items and PDFs")
    print("=" * 80)

def main():
    # Check if xdotool is installed
    try:
        subprocess.run(['which', 'xdotool'], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("ERROR: xdotool not installed!")
        print("Please install it with: sudo apt-get install xdotool")
        return
    
    print("Zotero Automated Save Script")
    print("=" * 40)
    print("\nThis script will:")
    print("1. Switch Chrome to focus")
    print("2. Navigate through open tabs")
    print("3. Press Ctrl+Shift+S on each tab to save with Zotero")
    print("\nMake sure:")
    print("- Chrome is open with papers loaded")
    print("- Zotero desktop is running")
    print("- Zotero WSL Proxy is active")
    print("- You're logged into institutional access")
    
    response = input("\nReady to start? (y/n): ")
    if response.lower() == 'y':
        auto_save_all_tabs()
    else:
        print("Cancelled.")

if __name__ == "__main__":
    main()