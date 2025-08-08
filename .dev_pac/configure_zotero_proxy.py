#!/usr/bin/env python3
"""
Configure Zotero Connector to use the WSL proxy.
The Connector needs to know where to find Zotero.
"""

import subprocess
import json
import time
from pathlib import Path

def check_proxy_status():
    """Check if Zotero WSL Proxy is running."""
    import requests
    
    endpoints = [
        ("http://localhost:23119/connector/ping", "localhost:23119"),
        ("http://127.0.0.1:23119/connector/ping", "127.0.0.1:23119"),
        ("http://ywata-note-win.local:23119/connector/ping", "ywata-note-win.local:23119"),
        ("http://172.19.32.1:23119/connector/ping", "172.19.32.1:23119"),  # Windows host IP
    ]
    
    print("Checking Zotero proxy endpoints...")
    print("-" * 40)
    
    working_endpoint = None
    for url, name in endpoints:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print(f"✅ {name} - Working!")
                working_endpoint = name
                break
            else:
                print(f"❌ {name} - Status {response.status_code}")
        except Exception as e:
            print(f"❌ {name} - {str(e)[:30]}")
    
    return working_endpoint

def inject_zotero_config():
    """Inject JavaScript to configure Zotero Connector in Chrome."""
    
    print("\nConfiguring Zotero Connector in Chrome...")
    print("-" * 40)
    
    # JavaScript to configure Zotero Connector
    # This sets the Zotero base URL in the extension
    config_js = """
    // Configure Zotero Connector to use proxy
    console.log('Configuring Zotero Connector for WSL proxy...');
    
    // Try to access Zotero Connector's settings
    if (typeof Zotero !== 'undefined') {
        Zotero.Prefs.set('connector.url', 'http://172.19.32.1:23119');
        console.log('Zotero Connector configured!');
    } else {
        console.log('Zotero object not found - opening settings page');
        // Open Zotero Connector preferences
        chrome.runtime.sendMessage(
            'ekhagklcjbdpajgpjgmbionohlpdbjgc',  // Zotero Connector ID
            {action: 'openPreferences'}
        );
    }
    """
    
    print("Opening Chrome with Zotero Connector settings...")
    
    # Open Chrome with Zotero Connector options page
    profile_dir = '/home/ywatanabe/.scitex/scholar/cache/chrome'
    
    # Zotero Connector extension ID and options page
    zotero_options = "chrome-extension://ekhagklcjbdpajgpjgmbionohlpdbjgc/preferences/preferences.html"
    
    args = [
        'google-chrome',
        f'--user-data-dir={profile_dir}',
        '--profile-directory=Profile 1',
        zotero_options
    ]
    
    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("✅ Opened Zotero Connector preferences")
    print("\n📝 MANUAL CONFIGURATION NEEDED:")
    print("1. In the Zotero Connector preferences page that just opened:")
    print("2. Click on 'Advanced' tab")
    print("3. Under 'Zotero Base URL', change it to:")
    print("   http://172.19.32.1:23119")
    print("4. Or try: http://ywata-note-win.local:23119")
    print("5. Click 'Save'")
    print("\nThen the Connector should be able to find Zotero!")

def test_zotero_connection():
    """Test if Zotero is accessible after configuration."""
    
    print("\n" + "=" * 60)
    print("TESTING ZOTERO CONNECTION")
    print("=" * 60)
    
    # Focus Chrome
    subprocess.run(['xdotool', 'search', '--name', 'Google Chrome', 'windowactivate'],
                   capture_output=True)
    time.sleep(1)
    
    # Open a test page
    test_url = "https://www.nature.com/articles/s41586-018-0278-9"
    
    print(f"Opening test article: {test_url}")
    
    profile_dir = '/home/ywatanabe/.scitex/scholar/cache/chrome'
    args = [
        'google-chrome',
        f'--user-data-dir={profile_dir}',
        '--profile-directory=Profile 1',
        '--new-tab',
        test_url
    ]
    
    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("\n📋 TEST INSTRUCTIONS:")
    print("1. Wait for the page to load")
    print("2. Click the Zotero Connector icon")
    print("3. It should show 'Save to Zotero' (not 'Is Zotero Running?')")
    print("4. If it works, we can proceed with batch downloads!")

def main():
    """Main configuration workflow."""
    
    print("=" * 60)
    print("ZOTERO CONNECTOR PROXY CONFIGURATION")
    print("=" * 60)
    
    # Check proxy status
    working = check_proxy_status()
    
    if not working:
        print("\n❌ No working proxy endpoint found!")
        print("\nPlease ensure Zotero WSL Proxy is running:")
        print("In a separate terminal, run the proxy server")
        return
    
    print(f"\n✅ Proxy is working at: {working}")
    
    # Open configuration
    inject_zotero_config()
    
    # Wait for user to configure
    input("\nPress Enter after configuring the Connector...")
    
    # Test connection
    test_zotero_connection()

if __name__ == "__main__":
    main()