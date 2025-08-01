#!/usr/bin/env python3
"""
Chrome Extension Automation for SciTeX Scholar Module

This script demonstrates methods to automate Chrome extension installation
for the scholar workflow.
"""

import os
import json
import time
import subprocess
import shutil
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ChromeExtensionInstaller:
    """Automates Chrome extension installation for SciTeX Scholar workflow"""
    
    EXTENSIONS = {
        "lean_library": {
            "id": "hghakoefmnkhamdhenpbogkeopjlkpoa",
            "name": "Lean Library",
            "crx_url": "https://clients2.google.com/service/update2/crx?response=redirect&prodversion=49.0&acceptformat=crx3&x=id%3D{id}%26installsource%3Dondemand%26uc"
        },
        "zotero_connector": {
            "id": "ekhagklcjbdpajgpjgmbionohlpdbjgc", 
            "name": "Zotero Connector",
            "crx_url": "https://clients2.google.com/service/update2/crx?response=redirect&prodversion=49.0&acceptformat=crx3&x=id%3D{id}%26installsource%3Dondemand%26uc"
        },
        "accept_cookies": {
            "id": "ofpnikijgfhlmmjlpkfaifhhdonchhoi",
            "name": "Accept all cookies",
            "crx_url": "https://clients2.google.com/service/update2/crx?response=redirect&prodversion=49.0&acceptformat=crx3&x=id%3D{id}%26installsource%3Dondemand%26uc"
        },
        "captcha_solver": {
            "id": "ifibfemgeogfhoebkmokieepdoobkbpo",
            "name": "Captcha Solver",
            "crx_url": "https://clients2.google.com/service/update2/crx?response=redirect&prodversion=49.0&acceptformat=crx3&x=id%3D{id}%26installsource%3Dondemand%26uc"
        }
    }
    
    def __init__(self, profile_dir=None):
        """Initialize with optional Chrome profile directory"""
        self.profile_dir = profile_dir or Path.home() / ".scitex" / "scholar" / "chrome_profile"
        self.extensions_dir = Path.home() / ".scitex" / "scholar" / "extensions"
        self.ensure_directories()
        
    def ensure_directories(self):
        """Create necessary directories"""
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.extensions_dir.mkdir(parents=True, exist_ok=True)
        
    def download_extension_crx(self, extension_key):
        """Download CRX file for extension"""
        ext = self.EXTENSIONS[extension_key]
        crx_path = self.extensions_dir / f"{extension_key}.crx"
        
        if crx_path.exists():
            print(f"Extension {ext['name']} already downloaded")
            return crx_path
            
        print(f"Downloading {ext['name']}...")
        url = ext['crx_url'].format(id=ext['id'])
        
        # Use wget or curl to download
        subprocess.run([
            'wget', '-O', str(crx_path), url
        ], check=True)
        
        return crx_path
        
    def method1_policy_installation(self):
        """Method 1: Install via Chrome policies (requires admin rights on some systems)"""
        print("\n=== Method 1: Policy-based Installation ===")
        
        # Create policy file for Linux
        policy_dir = Path("/etc/opt/chrome/policies/managed")
        policy_file = policy_dir / "scitex_extensions.json"
        
        policy = {
            "ExtensionInstallForcelist": [
                f"{ext['id']};https://clients2.google.com/service/update2/crx"
                for ext in self.EXTENSIONS.values()
            ]
        }
        
        print(f"Policy content:\n{json.dumps(policy, indent=2)}")
        print(f"\nTo install via policy (requires sudo):")
        print(f"1. sudo mkdir -p {policy_dir}")
        print(f"2. Create {policy_file} with the above content")
        print(f"3. Restart Chrome")
        
        # Save policy file for user reference
        user_policy_file = self.extensions_dir / "chrome_policy.json"
        with open(user_policy_file, 'w') as f:
            json.dump(policy, f, indent=2)
        print(f"\nPolicy file saved to: {user_policy_file}")
        
    def method2_unpacked_extensions(self):
        """Method 2: Load unpacked extensions (developer mode)"""
        print("\n=== Method 2: Unpacked Extensions ===")
        
        options = Options()
        options.add_experimental_option("detach", True)
        options.add_argument(f"--user-data-dir={self.profile_dir}")
        
        # Enable developer mode
        prefs = {
            "extensions.ui.developer_mode": True
        }
        options.add_experimental_option("prefs", prefs)
        
        print("Note: This method requires:")
        print("1. Extensions to be downloaded and unpacked")
        print("2. Developer mode to be enabled")
        print("3. Manual loading of unpacked extensions")
        
        # Add extensions if unpacked versions exist
        for ext_key in self.EXTENSIONS:
            unpacked_dir = self.extensions_dir / ext_key
            if unpacked_dir.exists():
                options.add_argument(f"--load-extension={unpacked_dir}")
                print(f"Loading unpacked extension: {unpacked_dir}")
                
    def method3_selenium_automation(self):
        """Method 3: Selenium automation to install from Chrome Web Store"""
        print("\n=== Method 3: Selenium Automation ===")
        
        options = Options()
        options.add_experimental_option("detach", True)
        options.add_argument(f"--user-data-dir={self.profile_dir}")
        options.add_argument("--no-sandbox")  # Required for some environments
        options.add_argument("--disable-dev-shm-usage")
        
        # Create driver
        driver = webdriver.Chrome(options=options)
        
        try:
            for ext_key, ext_info in self.EXTENSIONS.items():
                print(f"\nInstalling {ext_info['name']}...")
                
                # Navigate to extension page
                url = f"https://chrome.google.com/webstore/detail/{ext_info['id']}"
                driver.get(url)
                time.sleep(3)
                
                # Try to find and click "Add to Chrome" button
                try:
                    add_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add to Chrome')]"))
                    )
                    add_button.click()
                    
                    # Handle confirmation popup
                    time.sleep(2)
                    try:
                        confirm_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Add extension')]")
                        confirm_button.click()
                        print(f"✓ {ext_info['name']} installed successfully")
                    except:
                        print(f"⚠ Confirmation popup not found for {ext_info['name']}")
                        
                except Exception as e:
                    print(f"✗ Failed to install {ext_info['name']}: {str(e)}")
                    
            print("\nKeeping browser open for manual verification...")
            input("Press Enter to close browser...")
            
        finally:
            driver.quit()
            
    def method4_crx_installation(self):
        """Method 4: Direct CRX installation (may be blocked in newer Chrome)"""
        print("\n=== Method 4: CRX File Installation ===")
        
        # Download all CRX files first
        crx_files = []
        for ext_key in self.EXTENSIONS:
            crx_path = self.download_extension_crx(ext_key)
            crx_files.append((ext_key, crx_path))
            
        options = Options()
        options.add_experimental_option("detach", True)
        options.add_argument(f"--user-data-dir={self.profile_dir}")
        
        # Add CRX files as extensions
        for ext_key, crx_path in crx_files:
            options.add_extension(str(crx_path))
            print(f"Added {self.EXTENSIONS[ext_key]['name']} to Chrome options")
            
        print("\nLaunching Chrome with extensions...")
        driver = webdriver.Chrome(options=options)
        
        print("Extensions should be installed. Check chrome://extensions/")
        input("Press Enter to close browser...")
        driver.quit()
        
    def method5_playwright_approach(self):
        """Method 5: Using Playwright (alternative to Selenium)"""
        print("\n=== Method 5: Playwright Approach ===")
        
        script = '''
from playwright.sync_api import sync_playwright
import time

def install_extensions():
    with sync_playwright() as p:
        # Launch Chrome with persistent context
        browser = p.chromium.launch_persistent_context(
            user_data_dir="{profile_dir}",
            headless=False,
            channel="chrome",
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )
        
        page = browser.new_page()
        
        # Install extensions
        extensions = {extensions}
        
        for ext_key, ext_info in extensions.items():
            print(f"Installing {{ext_info['name']}}...")
            page.goto(f"https://chrome.google.com/webstore/detail/{{ext_info['id']}}")
            time.sleep(3)
            
            try:
                # Click "Add to Chrome"
                page.click("button:has-text('Add to Chrome')")
                time.sleep(2)
                
                # Confirm installation
                page.click("button:has-text('Add extension')")
                print(f"✓ {{ext_info['name']}} installed")
                
            except Exception as e:
                print(f"✗ Failed to install {{ext_info['name']}}: {{e}}")
                
        input("Press Enter to close browser...")
        browser.close()

if __name__ == "__main__":
    install_extensions()
'''
        
        script_path = self.extensions_dir / "playwright_installer.py"
        with open(script_path, 'w') as f:
            f.write(script.format(
                profile_dir=self.profile_dir,
                extensions=repr(self.EXTENSIONS)
            ))
            
        print(f"Playwright script saved to: {script_path}")
        print("To use: pip install playwright && playwright install chrome")
        print(f"Then run: python {script_path}")

def main():
    """Demonstrate all methods for Chrome extension automation"""
    installer = ChromeExtensionInstaller()
    
    print("Chrome Extension Automation Methods for SciTeX Scholar")
    print("=" * 60)
    
    # Method 1: Policy installation
    installer.method1_policy_installation()
    
    # Method 2: Unpacked extensions
    installer.method2_unpacked_extensions()
    
    # Method 3: Selenium automation
    print("\nTo test Selenium automation, uncomment the next line:")
    # installer.method3_selenium_automation()
    
    # Method 4: CRX installation
    print("\nTo test CRX installation, uncomment the next line:")
    # installer.method4_crx_installation()
    
    # Method 5: Playwright approach
    installer.method5_playwright_approach()
    
    print("\n" + "=" * 60)
    print("Summary of Methods:")
    print("1. Policy Installation - Most reliable for managed environments")
    print("2. Unpacked Extensions - Good for development")
    print("3. Selenium Automation - Can handle Chrome Web Store interactions")
    print("4. CRX Installation - Direct but may be blocked")
    print("5. Playwright - Modern alternative to Selenium")
    
    print(f"\nExtension files stored in: {installer.extensions_dir}")
    print(f"Chrome profile stored in: {installer.profile_dir}")

if __name__ == "__main__":
    main()