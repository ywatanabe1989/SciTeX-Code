#!/usr/bin/env python3
"""
Phase 1: Open login pages for all major publishers using Windows Chrome from WSL2.
User logs into each one, then closes browser.
This saves authentication cookies for Phase 2.
"""

import time
import subprocess
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def find_windows_chrome_profile():
    """Find Chrome profile path in Windows."""
    # Get Windows username
    try:
        windows_user = subprocess.check_output(['cmd.exe', '/c', 'echo %USERNAME%'], text=True).strip()
    except:
        windows_user = subprocess.check_output(['whoami.exe'], text=True).split('\\')[1].strip()
    
    # Windows Chrome profile paths
    profile_paths = [
        f"/mnt/c/Users/{windows_user}/AppData/Local/Google/Chrome/User Data",
        f"C:\\Users\\{windows_user}\\AppData\\Local\\Google\\Chrome\\User Data"
    ]
    
    # Check if profile exists
    for profile_path in profile_paths:
        if profile_path.startswith("/mnt/c/"):
            # Check WSL path
            if Path(profile_path).exists():
                # Convert to Windows path
                return profile_path.replace("/mnt/c/", "C:\\").replace("/", "\\")
        else:
            # Already Windows path
            return profile_path
    
    return None


def get_windows_chrome_path():
    """Get the path to Chrome executable on Windows."""
    chrome_paths = [
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
    ]
    
    # Check if Chrome exists
    for chrome_path in chrome_paths:
        wsl_path = chrome_path.replace("C:\\", "/mnt/c/").replace("\\", "/")
        if Path(wsl_path).exists():
            return chrome_path
    
    # Try to find Chrome via Windows registry
    try:
        result = subprocess.check_output(
            ['cmd.exe', '/c', 'reg query "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\chrome.exe" /ve'],
            text=True
        )
        for line in result.split('\n'):
            if 'REG_SZ' in line:
                chrome_path = line.split('REG_SZ')[1].strip()
                if chrome_path:
                    return chrome_path
    except:
        pass
    
    return None


def main():
    """Open login pages for major publishers."""
    
    print("PHASE 1: PUBLISHER LOGIN SETUP (Windows Chrome)")
    print("="*60)
    print("\nThis will open login pages for major academic publishers.")
    print("Please login to each one using your UniMelb credentials.")
    print("When done, close the browser window.\n")
    
    # Major publishers and their login pages
    publishers = [
        {
            'name': 'Elsevier (ScienceDirect)',
            'url': 'https://www.sciencedirect.com/',
            'login_hint': 'Click "Sign in" → "Sign in via your institution" → Search for "University of Melbourne"'
        },
        {
            'name': 'Wiley Online Library',
            'url': 'https://onlinelibrary.wiley.com/',
            'login_hint': 'Click "Login" → "Institutional Login" → Search for "University of Melbourne"'
        },
        {
            'name': 'Springer/Nature',
            'url': 'https://link.springer.com/',
            'login_hint': 'Click "Log in" → "Access via your institution" → Search for "University of Melbourne"'
        },
        {
            'name': 'IEEE Xplore',
            'url': 'https://ieeexplore.ieee.org/',
            'login_hint': 'Click "Institutional Sign In" → Search for "University of Melbourne"'
        },
        {
            'name': 'Taylor & Francis',
            'url': 'https://www.tandfonline.com/',
            'login_hint': 'Click "Log in" → "Shibboleth" → Search for "University of Melbourne"'
        },
        {
            'name': 'SAGE Journals',
            'url': 'https://journals.sagepub.com/',
            'login_hint': 'Click "Sign in" → "Institutional access" → Search for "University of Melbourne"'
        },
        {
            'name': 'Oxford Academic',
            'url': 'https://academic.oup.com/',
            'login_hint': 'Click "Sign in" → "Sign in via your institution" → Search for "University of Melbourne"'
        },
        {
            'name': 'Cambridge Core',
            'url': 'https://www.cambridge.org/core',
            'login_hint': 'Click "Log in" → "Institutional login" → Search for "University of Melbourne"'
        }
    ]
    
    # Find Chrome executable
    chrome_exe = get_windows_chrome_path()
    if not chrome_exe:
        print("✗ Could not find Windows Chrome installation!")
        print("Please ensure Chrome is installed on Windows.")
        return
    print(f"✓ Found Chrome: {chrome_exe}")
    
    # Find Chrome profile
    profile_path = find_windows_chrome_profile()
    if profile_path:
        print(f"✓ Using Chrome profile: {profile_path}")
        print("  (Your logins will be saved here)\n")
    else:
        print("⚠ No Chrome profile found. Logins may not persist.\n")
    
    print("Publishers to login:")
    for i, pub in enumerate(publishers, 1):
        print(f"{i}. {pub['name']}")
    
    input("\nPress Enter to open all login pages...")
    
    # Setup Chrome with Windows executable
    options = Options()
    if profile_path:
        options.add_argument(f"user-data-dir={profile_path}")
    options.add_argument("--start-maximized")
    
    # Create service with Windows Chrome path
    service = Service(executable_path=chrome_exe)
    
    # Open browser
    print("\nOpening Chrome with publisher login pages...")
    driver = webdriver.Chrome(service=service, options=options)
    
    # Open first publisher in main tab
    driver.get(publishers[0]['url'])
    time.sleep(2)
    
    # Open rest in new tabs
    for pub in publishers[1:]:
        driver.execute_script(f"window.open('{pub['url']}', '_blank');")
        time.sleep(1)
    
    print("\n" + "="*60)
    print("BROWSER OPENED WITH LOGIN PAGES")
    print("="*60)
    
    print("\nPlease complete the following steps:\n")
    
    for i, pub in enumerate(publishers, 1):
        print(f"{i}. {pub['name']}:")
        print(f"   {pub['login_hint']}\n")
    
    print("="*60)
    print("IMPORTANT:")
    print("- Take your time to login to each publisher")
    print("- Some may redirect through UniMelb SSO")
    print("- Make sure you can access papers after login")
    print("- When done, close the browser window")
    print("="*60)
    
    # Wait for browser to close
    try:
        while True:
            # Check if browser is still open
            try:
                _ = driver.window_handles
                time.sleep(2)
            except:
                # Browser was closed
                break
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    
    print("\n✓ Login phase complete!")
    print("Your authentication cookies have been saved.")
    print("\nYou can now run Phase 2 to download PDFs:")
    print("  python phase2_download_pdfs_windows.py")


if __name__ == "__main__":
    main()