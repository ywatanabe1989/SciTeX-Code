#!/usr/bin/env python3
"""
Interactive tab test with visual confirmation.
Shows URL in each tab to confirm switching.
"""

import subprocess
import time

def interactive_tab_test():
    """Test tab switching with visual feedback."""
    
    print("=" * 60)
    print("INTERACTIVE TAB SWITCHING TEST")
    print("=" * 60)
    
    # Kill Chrome first
    subprocess.run(['pkill', 'chrome'], capture_output=True)
    time.sleep(2)
    
    # Open Chrome with numbered pages for visual confirmation
    print("\nOpening Chrome with 5 numbered tabs...")
    
    profile_dir = '/home/ywatanabe/.scitex/scholar/cache/chrome'
    
    # Use search queries that show tab numbers clearly
    test_urls = [
        'https://www.google.com/search?q=TAB+1+FIRST',
        'https://www.google.com/search?q=TAB+2+SECOND',
        'https://www.google.com/search?q=TAB+3+THIRD',
        'https://www.google.com/search?q=TAB+4+FOURTH',
        'https://www.google.com/search?q=TAB+5+FIFTH'
    ]
    
    args = [
        'google-chrome',
        f'--user-data-dir={profile_dir}',
        '--profile-directory=Profile 1',
    ] + test_urls
    
    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("Waiting for Chrome to load...")
    time.sleep(8)
    
    print("\n" + "=" * 60)
    print("WATCH CHROME WINDOW - TABS SHOULD CHANGE")
    print("=" * 60)
    
    # Make sure Chrome is focused
    print("\n1. Focusing Chrome window...")
    subprocess.run(['xdotool', 'search', '--name', 'Google Chrome', 'windowactivate', '--sync'],
                   capture_output=True)
    time.sleep(1)
    
    # Bring to front
    subprocess.run(['xdotool', 'search', '--name', 'Google Chrome', 'windowraise'],
                   capture_output=True)
    time.sleep(1)
    
    print("\n2. Testing Ctrl+[number] navigation:\n")
    
    # Test each tab
    for i in [1, 2, 3, 4, 5, 3, 1, 5]:  # Jump around to make it obvious
        print(f"   Switching to TAB {i} (Ctrl+{i})...", end='', flush=True)
        
        # Keep Chrome focused
        subprocess.run(['xdotool', 'search', '--name', 'Google Chrome', 'windowactivate'],
                       capture_output=True)
        
        # Send key with explicit window focus
        subprocess.run(['xdotool', 'key', '--clearmodifiers', f'ctrl+{i}'], 
                       capture_output=True)
        
        time.sleep(2)
        print(f" ✓ Should show 'TAB {i}'")
    
    print("\n3. Testing Ctrl+Tab navigation:\n")
    
    # Go to first tab
    subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+1'], 
                   capture_output=True)
    time.sleep(1)
    
    for i in range(4):
        print(f"   Ctrl+Tab (next tab)...", end='', flush=True)
        
        # Keep Chrome focused
        subprocess.run(['xdotool', 'search', '--name', 'Google Chrome', 'windowactivate'],
                       capture_output=True)
        
        subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+Tab'], 
                       capture_output=True)
        
        time.sleep(2)
        print(f" ✓ Should be on TAB {i+2}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\nDid you see:")
    print("1. Tabs switching with Ctrl+[number]?")
    print("2. Tabs advancing with Ctrl+Tab?")
    print("3. The Google search showing 'TAB 1', 'TAB 2', etc?")
    
    return input("\nDid tabs change? (y/n): ").lower() == 'y'

def test_with_papers():
    """Test with actual papers if tab switching works."""
    
    print("\n" + "=" * 60)
    print("TESTING WITH ACTUAL PAPERS")
    print("=" * 60)
    
    # Open 3 papers for testing
    subprocess.run(['pkill', 'chrome'], capture_output=True)
    time.sleep(2)
    
    profile_dir = '/home/ywatanabe/.scitex/scholar/cache/chrome'
    
    # Use different publishers to see variety
    test_dois = [
        'https://doi.org/10.1051/matecconf/201821003016',  # MATEC
        'https://doi.org/10.7717/peerj-cs.523',  # PeerJ
        'https://doi.org/10.1155/2017/1240323'  # Hindawi
    ]
    
    args = [
        'google-chrome',
        f'--user-data-dir={profile_dir}',
        '--profile-directory=Profile 1',
    ] + test_dois
    
    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("\nOpened 3 different papers")
    print("Waiting for load...")
    time.sleep(10)
    
    print("\nProcessing each tab separately:\n")
    
    # Focus Chrome
    subprocess.run(['xdotool', 'search', '--name', 'Google Chrome', 'windowactivate'],
                   capture_output=True)
    time.sleep(1)
    
    for i in range(1, 4):
        print(f"Tab {i}:")
        print(f"  Switching to tab {i}...")
        
        # Explicit tab number
        subprocess.run(['xdotool', 'key', '--clearmodifiers', f'ctrl+{i}'], 
                       capture_output=True)
        time.sleep(3)
        
        print(f"  Saving with Zotero...")
        subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+shift+s'], 
                       capture_output=True)
        
        print(f"  Waiting 6 seconds for save...")
        time.sleep(6)
        
        print(f"  ✓ Tab {i} done\n")
    
    print("✅ Complete! Check Zotero for 3 different papers")

def main():
    """Run interactive test."""
    
    # First test if tab switching works
    if interactive_tab_test():
        print("\n✅ Tab switching is working!")
        
        # If it works, test with papers
        response = input("\nTest with actual papers? (y/n): ")
        if response.lower() == 'y':
            test_with_papers()
    else:
        print("\n❌ Tab switching not working")
        print("\nPossible issues:")
        print("1. Chrome not getting keyboard focus")
        print("2. xdotool not sending keys properly")
        print("3. Chrome shortcuts disabled")

if __name__ == "__main__":
    main()