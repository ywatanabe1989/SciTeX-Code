#!/usr/bin/env python3
"""
Non-interactive version: Opens publisher login pages automatically.
"""

import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def find_chrome_profile():
    """Find Chrome profile path."""
    import platform
    home = Path.home()
    
    if platform.system() == "Linux":
        profiles = [
            home / ".config" / "google-chrome",
            home / ".config" / "chromium",
        ]
    
    for profile_path in profiles:
        if profile_path.exists():
            return str(profile_path)
    return None


def main():
    """Open login pages for major publishers."""
    
    print("OPENING PUBLISHER LOGIN PAGES")
    print("="*60)
    
    # Major publishers
    publishers = [
        {
            'name': 'Elsevier (ScienceDirect)',
            'url': 'https://www.sciencedirect.com/',
            'login_hint': 'Sign in → Institution → University of Melbourne'
        },
        {
            'name': 'Wiley',
            'url': 'https://onlinelibrary.wiley.com/',
            'login_hint': 'Login → Institutional → University of Melbourne'
        },
        {
            'name': 'Springer/Nature',
            'url': 'https://link.springer.com/',
            'login_hint': 'Log in → Institution → University of Melbourne'
        },
        {
            'name': 'Frontiers',
            'url': 'https://www.frontiersin.org/',
            'login_hint': 'Usually open access, no login needed'
        },
        {
            'name': 'MDPI',
            'url': 'https://www.mdpi.com/',
            'login_hint': 'Usually open access, no login needed'
        }
    ]
    
    # Find Chrome profile
    profile_path = find_chrome_profile()
    if profile_path:
        print(f"✓ Using Chrome profile: {profile_path}\n")
    
    # Setup Chrome
    options = Options()
    if profile_path:
        options.add_argument(f"user-data-dir={profile_path}")
    options.add_argument("--start-maximized")
    
    print("Opening Chrome with publisher sites...\n")
    
    try:
        driver = webdriver.Chrome(options=options)
        
        # Open first publisher
        print(f"Opening: {publishers[0]['name']}")
        driver.get(publishers[0]['url'])
        time.sleep(2)
        
        # Open rest in new tabs
        for pub in publishers[1:]:
            print(f"Opening: {pub['name']}")
            driver.execute_script(f"window.open('{pub['url']}', '_blank');")
            time.sleep(1)
        
        print("\n" + "="*60)
        print("BROWSER OPENED - LOGIN INSTRUCTIONS")
        print("="*60 + "\n")
        
        for pub in publishers:
            print(f"• {pub['name']}:")
            print(f"  {pub['login_hint']}\n")
        
        print("="*60)
        print("IMPORTANT:")
        print("1. Login to each publisher using UniMelb credentials")
        print("2. Test by clicking on a paper to verify access")
        print("3. Keep browser open for 30 seconds after all logins")
        print("4. Browser will close automatically")
        print("="*60)
        
        # Keep browser open for 30 seconds
        print("\nBrowser will remain open for 30 seconds...")
        for i in range(30, 0, -5):
            print(f"Closing in {i} seconds...")
            time.sleep(5)
        
        driver.quit()
        print("\n✓ Setup complete! Cookies saved.")
        print("\nNow run: python phase2_download_pdfs.py")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure Chrome/Chromium is installed and chromedriver is available.")


if __name__ == "__main__":
    main()