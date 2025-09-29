#!/usr/bin/env python3
"""
Phase 1: Login to University of Melbourne Library SSO.
This single login gives you access to all academic publishers.
"""

import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def find_chrome_profile():
    """Find Chrome profile path."""
    import platform
    home = Path.home()
    
    if platform.system() == "Windows":
        profiles = [
            home / "AppData" / "Local" / "Google" / "Chrome" / "User Data",
        ]
    elif platform.system() == "Darwin":  # macOS
        profiles = [
            home / "Library" / "Application Support" / "Google" / "Chrome",
        ]
    else:  # Linux
        profiles = [
            home / ".config" / "google-chrome",
            home / ".config" / "chromium",
        ]
    
    for profile_path in profiles:
        if profile_path.exists():
            return str(profile_path)
    return None


def main():
    """Open University of Melbourne library login page."""
    
    print("PHASE 1: UNIVERSITY SSO LOGIN")
    print("="*60)
    print("\nThis will open the University of Melbourne library portal.")
    print("Login once to get access to all publishers.\n")
    
    # University of Melbourne Library URLs
    unimelb_urls = [
        {
            'name': 'UniMelb Library Portal',
            'url': 'https://library.unimelb.edu.au/',
            'description': 'Main library portal - login here for general access'
        },
        {
            'name': 'UniMelb EZProxy Login',
            'url': 'https://login.ezproxy.lib.unimelb.edu.au/login',
            'description': 'Direct EZProxy login - provides access to all subscribed content'
        },
        {
            'name': 'LibrarySearch (Primo)',
            'url': 'https://primo.lib.unimelb.edu.au/',
            'description': 'Search interface - login provides full-text access'
        }
    ]
    
    # Find Chrome profile
    profile_path = find_chrome_profile()
    if profile_path:
        print(f"✓ Using Chrome profile: {profile_path}")
        print("  (Your login will be saved here)\n")
    else:
        print("⚠ No Chrome profile found. Login may not persist.\n")
    
    print("Available login options:")
    for i, site in enumerate(unimelb_urls, 1):
        print(f"{i}. {site['name']}")
        print(f"   {site['description']}")
    
    # Ask which one to use
    print("\nWhich login page would you like to use?")
    choice = input("Enter 1-3 (default=2 for EZProxy): ").strip() or "2"
    
    try:
        idx = int(choice) - 1
        selected_url = unimelb_urls[idx]
    except:
        print("Using EZProxy login...")
        selected_url = unimelb_urls[1]
    
    print(f"\nOpening: {selected_url['name']}")
    input("Press Enter to continue...")
    
    # Setup Chrome
    options = Options()
    if profile_path:
        options.add_argument(f"user-data-dir={profile_path}")
    options.add_argument("--start-maximized")
    
    # Open browser
    print("\nOpening Chrome...")
    driver = webdriver.Chrome(options=options)
    
    # Navigate to login page
    driver.get(selected_url['url'])
    
    print("\n" + "="*60)
    print("BROWSER OPENED - PLEASE LOGIN")
    print("="*60)
    
    print("\nInstructions:")
    print("1. Login with your UniMelb credentials")
    print("2. Complete any two-factor authentication if required")
    print("3. Once logged in, you can close the browser")
    print("\nAfter login, you'll have access to:")
    print("- Elsevier (ScienceDirect)")
    print("- Wiley Online Library")
    print("- Springer/Nature")
    print("- IEEE Xplore")
    print("- Taylor & Francis")
    print("- SAGE Journals")
    print("- Oxford Academic")
    print("- Cambridge Core")
    print("- And many more...")
    
    print("\n" + "="*60)
    print("TIP: You can test your access by searching for a paper")
    print("in the library search and checking if you can download PDFs")
    print("="*60)
    
    # Wait for browser to close
    try:
        while True:
            try:
                _ = driver.window_handles
                time.sleep(2)
            except:
                break
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    
    print("\n✓ Login phase complete!")
    print("Your authentication has been saved.")
    print("\nYou can now run Phase 2 to download PDFs:")
    print("  python phase2_download_pdfs.py")
    print("\nNote: When downloading PDFs, they will automatically")
    print("redirect through the EZProxy to provide access.")


if __name__ == "__main__":
    main()