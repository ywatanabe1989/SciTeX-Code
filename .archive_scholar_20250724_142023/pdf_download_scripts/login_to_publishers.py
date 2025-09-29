#!/usr/bin/env python3
"""
Open publisher sites and wait for user to login and close browser.
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
    """Open publisher sites for login."""
    
    print("PUBLISHER LOGIN HELPER")
    print("="*60)
    
    # Publishers
    publishers = [
        {
            'name': 'Elsevier (ScienceDirect)',
            'url': 'https://www.sciencedirect.com/',
            'test_url': 'https://www.sciencedirect.com/science/article/pii/S0149763420304668',  # Your paper
            'login': 'Click "Sign in" → "Sign in via your institution" → Search "University of Melbourne"'
        },
        {
            'name': 'Wiley',
            'url': 'https://onlinelibrary.wiley.com/',
            'test_url': 'https://onlinelibrary.wiley.com/doi/10.1002/hbm.26190',  # Your paper
            'login': 'Click "Login" → "Institutional Login" → Search "University of Melbourne"'
        },
        {
            'name': 'Springer/Nature',
            'url': 'https://link.springer.com/',
            'test_url': 'https://www.nature.com/articles/s41598-019-48870-2',  # Your paper
            'login': 'Click "Log in" → "Access via your institution" → Search "University of Melbourne"'
        },
        {
            'name': 'Frontiers',
            'url': 'https://www.frontiersin.org/',
            'test_url': 'https://www.frontiersin.org/articles/10.3389/fnins.2019.00573/full',  # Your paper
            'login': 'Open access - no login needed'
        },
        {
            'name': 'MDPI',
            'url': 'https://www.mdpi.com/',
            'test_url': 'https://www.mdpi.com/1099-4300/23/8/1070',  # Your paper
            'login': 'Open access - no login needed'
        }
    ]
    
    # Find Chrome profile
    profile_path = find_chrome_profile()
    if profile_path:
        print(f"✓ Using Chrome profile: {profile_path}")
        print("  (Your logins will be saved here)\n")
    
    # Setup Chrome
    options = Options()
    if profile_path:
        options.add_argument(f"user-data-dir={profile_path}")
    options.add_argument("--start-maximized")
    
    print("Opening Chrome with publisher sites...\n")
    
    try:
        driver = webdriver.Chrome(options=options)
        
        # Open publishers in tabs
        print("Opening publisher sites:")
        driver.get(publishers[0]['url'])
        print(f"  ✓ Tab 1: {publishers[0]['name']}")
        time.sleep(2)
        
        for i, pub in enumerate(publishers[1:], 2):
            driver.execute_script(f"window.open('{pub['url']}', '_blank');")
            print(f"  ✓ Tab {i}: {pub['name']}")
            time.sleep(1)
        
        print("\n" + "="*60)
        print("LOGIN INSTRUCTIONS")
        print("="*60 + "\n")
        
        for i, pub in enumerate(publishers, 1):
            print(f"{i}. {pub['name']}:")
            print(f"   {pub['login']}")
            print(f"   Test with: {pub['test_url']}\n")
        
        print("="*60)
        print("STEPS:")
        print("1. Login to each publisher (tabs 1-3)")
        print("2. Open the test URL in each tab to verify access")
        print("3. You should see 'Get Access' or 'Download PDF' button")
        print("4. When done, simply close the browser")
        print("="*60)
        
        print("\n⏳ Waiting for you to complete logins and close browser...")
        print("   (No timeout - take your time)")
        
        # Wait for browser to be closed by user
        while True:
            try:
                # Check if browser is still alive
                _ = driver.current_url
                time.sleep(2)
            except:
                # Browser was closed
                break
        
        print("\n✓ Browser closed. Cookies saved!")
        print("\nYour logins are now saved. You can run:")
        print("  python test_phase2_download.py")
        print("\nto download PDFs using your saved authentication.")
        
    except KeyboardInterrupt:
        print("\n\nInterrupted. Closing browser...")
        try:
            driver.quit()
        except:
            pass
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure Chrome/Chromium and chromedriver are installed.")


if __name__ == "__main__":
    main()