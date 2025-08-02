#!/usr/bin/env python3
"""
Manual Chrome Extension Installer for SciTeX Scholar
Run this script to open Chrome with the persistent profile and install extensions.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pathlib import Path
import time

# Extension IDs
EXTENSIONS = {
    "Lean Library": "hghakoefmnkhamdhenpbogkeopjlkpoa",
    "Zotero Connector": "ekhagklcjbdpajgpjgmbionohlpdbjgc",
    "Accept all cookies": "ofpnikijgfhlmmjlpkfaifhhdonchhoi",
    "Captcha Solver": "ifibfemgeogfhoebkmokieepdoobkbpo"
}

def install_extensions():
    profile_dir = Path.home() / ".scitex" / "scholar" / "chrome_profile_v2"
    
    options = Options()
    options.add_argument(f"--user-data-dir={profile_dir}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("detach", True)  # Keep browser open
    
    print(f"Opening Chrome with profile: {profile_dir}")
    driver = webdriver.Chrome(options=options)
    
    print("\nPlease install the following extensions manually:")
    for name, ext_id in EXTENSIONS.items():
        url = f"https://chrome.google.com/webstore/detail/{ext_id}"
        print(f"\n{name}:")
        print(f"  URL: {url}")
        driver.execute_script(f"window.open('{url}', '_blank');")
        time.sleep(1)
    
    print("\n" + "="*60)
    print("INSTRUCTIONS:")
    print("1. Click 'Add to Chrome' for each extension")
    print("2. Accept any permissions requested")
    print("3. Close the browser when done")
    print("4. The extensions will persist in the profile")
    print("="*60)
    
    input("\nPress Enter when done installing extensions...")
    driver.quit()

if __name__ == "__main__":
    install_extensions()
