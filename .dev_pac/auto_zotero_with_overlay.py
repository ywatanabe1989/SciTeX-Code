#!/usr/bin/env python3
"""
Automated Zotero saves with browser overlay warning.
Shows a visual warning on the browser during automation.
"""

import subprocess
import time
import requests
import sys

def check_zotero_connection():
    """Verify Zotero is accessible."""
    endpoints = [
        "http://localhost:23119/connector/ping",
        "http://127.0.0.1:23119/connector/ping", 
        "http://ywata-note-win.local:23119/connector/ping"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, timeout=2)
            if response.status_code == 200:
                print(f"✅ Zotero connected at: {endpoint}")
                return True
        except:
            continue
    
    print("❌ Cannot connect to Zotero!")
    print("\nPlease ensure:")
    print("1. Zotero Desktop is running on Windows")
    print("2. Zotero WSL ProxyServer is running")
    print("3. Run: curl -I http://ywata-note-win.local:23119/connector/ping")
    return False

def inject_overlay_script():
    """Inject JavaScript to show overlay warning in Chrome."""
    
    # JavaScript to inject into the page
    overlay_js = """
    // Create overlay
    var overlay = document.createElement('div');
    overlay.id = 'scitex-overlay';
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        z-index: 999999;
        display: flex;
        align-items: center;
        justify-content: center;
        pointer-events: all;
        cursor: not-allowed;
    `;
    
    // Create message box
    var message = document.createElement('div');
    message.style.cssText = `
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        animation: pulse 2s infinite;
    `;
    
    message.innerHTML = `
        <h1 style="margin: 0 0 20px 0; font-size: 32px;">
            🤖 SciTeX PDF Download in Progress
        </h1>
        <p style="font-size: 18px; margin: 10px 0;">
            Automated download running - Please wait...
        </p>
        <p style="font-size: 16px; opacity: 0.9;">
            DO NOT CLICK OR TYPE
        </p>
        <div style="margin-top: 20px;">
            <div style="width: 200px; height: 4px; background: rgba(255,255,255,0.3); border-radius: 2px; margin: 0 auto;">
                <div style="width: 50%; height: 100%; background: white; border-radius: 2px; animation: loading 2s infinite;"></div>
            </div>
        </div>
    `;
    
    // Add animations
    var style = document.createElement('style');
    style.textContent = `
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.02); }
        }
        @keyframes loading {
            0% { width: 0%; }
            50% { width: 100%; }
            100% { width: 0%; }
        }
    `;
    document.head.appendChild(style);
    
    overlay.appendChild(message);
    document.body.appendChild(overlay);
    
    // Block all interactions
    document.addEventListener('click', function(e) { e.stopPropagation(); e.preventDefault(); }, true);
    document.addEventListener('keydown', function(e) { e.stopPropagation(); e.preventDefault(); }, true);
    """
    
    # Remove overlay JavaScript
    remove_overlay_js = """
    var overlay = document.getElementById('scitex-overlay');
    if (overlay) overlay.remove();
    """
    
    return overlay_js, remove_overlay_js

def run_automation_with_overlay(num_tabs=15, wait_time=4):
    """Run automation with visual overlay."""
    
    overlay_js, remove_js = inject_overlay_script()
    
    print("\n🤖 AUTOMATION STARTING\n")
    
    # Focus Chrome
    subprocess.run(['xdotool', 'search', '--name', 'Google Chrome', 'windowactivate'],
                   capture_output=True)
    time.sleep(1)
    
    # Go to first tab
    subprocess.run(['xdotool', 'key', 'ctrl+1'], capture_output=True)
    time.sleep(2)
    
    for i in range(num_tabs):
        print(f"Tab {i+1}/{num_tabs}:")
        
        # Inject overlay using devtools protocol (F12 → Console → Paste → Enter)
        print("  Adding overlay...")
        
        # Open console
        subprocess.run(['xdotool', 'key', 'F12'], capture_output=True)
        time.sleep(1)
        
        # Switch to console tab
        subprocess.run(['xdotool', 'key', 'ctrl+shift+k'], capture_output=True)
        time.sleep(0.5)
        
        # Type the JavaScript (simplified version)
        simple_overlay = "document.body.insertAdjacentHTML('beforeend', '<div style=\"position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.9);z-index:99999;display:flex;align-items:center;justify-content:center;color:white;font-size:24px;\"><div><h1>SciTeX Downloading PDFs</h1><p>Please wait...</p></div></div>');"
        
        subprocess.run(['xdotool', 'type', '--delay', '10', simple_overlay], capture_output=True)
        subprocess.run(['xdotool', 'key', 'Return'], capture_output=True)
        
        # Close devtools
        time.sleep(0.5)
        subprocess.run(['xdotool', 'key', 'F12'], capture_output=True)
        time.sleep(1)
        
        # Save with Zotero
        print("  Saving with Zotero...")
        subprocess.run(['xdotool', 'key', 'ctrl+shift+s'], capture_output=True)
        
        # Wait for save
        print(f"  Waiting {wait_time}s...")
        time.sleep(wait_time)
        
        # Next tab
        if i < num_tabs - 1:
            subprocess.run(['xdotool', 'key', 'ctrl+Tab'], capture_output=True)
            time.sleep(0.5)
    
    print("\n✅ AUTOMATION COMPLETE!")

def main():
    """Main entry point."""
    
    print("=" * 80)
    print("ZOTERO AUTOMATED SAVE WITH OVERLAY")
    print("=" * 80)
    
    # Check xdotool
    try:
        subprocess.run(['which', 'xdotool'], check=True, capture_output=True)
    except:
        print("ERROR: Please install xdotool")
        print("Run: sudo apt-get install xdotool")
        sys.exit(1)
    
    # Check Zotero connection
    if not check_zotero_connection():
        print("\n⚠️  Zotero connection failed!")
        print("\nTrying to restart Zotero WSL Proxy...")
        
        # Try to start the proxy
        subprocess.Popen([
            'python3', '-m', 'http.server', '23119',
            '--bind', '127.0.0.1'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        time.sleep(2)
        if not check_zotero_connection():
            sys.exit(1)
    
    # Get parameters
    try:
        num_tabs = int(input("\nNumber of tabs (default 15): ") or "15")
    except:
        num_tabs = 15
    
    try:
        wait_time = int(input("Wait time per save (default 4): ") or "4")
    except:
        wait_time = 4
    
    print(f"\nWill process {num_tabs} tabs")
    print(f"Total time: ~{num_tabs * (wait_time + 3)} seconds")
    
    if input("\nStart? (y/n): ").lower() == 'y':
        print("\nStarting in 3 seconds...")
        time.sleep(3)
        run_automation_with_overlay(num_tabs, wait_time)
    else:
        print("Cancelled.")

if __name__ == "__main__":
    main()