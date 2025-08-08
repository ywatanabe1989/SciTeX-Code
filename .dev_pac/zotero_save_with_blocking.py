#!/usr/bin/env python3
"""
Zotero automated save with input blocking and warning overlay.
Uses xinput to disable keyboard/mouse and shows fullscreen warning.
"""

import subprocess
import time
import sys
import signal
import atexit
from pathlib import Path

class InputBlocker:
    """Manages keyboard and mouse blocking."""
    
    def __init__(self):
        self.blocked_devices = []
        self.warning_process = None
        
    def get_input_devices(self):
        """Get list of keyboard and mouse devices."""
        try:
            result = subprocess.run(['xinput', 'list'], capture_output=True, text=True)
            devices = []
            
            for line in result.stdout.split('\n'):
                # Look for keyboards and mice
                if 'keyboard' in line.lower() or 'mouse' in line.lower():
                    # Extract device ID
                    if 'id=' in line:
                        device_id = line.split('id=')[1].split()[0]
                        devices.append(device_id)
            
            return devices
        except:
            return []
    
    def block_inputs(self):
        """Disable all input devices."""
        print("🔒 Blocking keyboard and mouse input...")
        
        devices = self.get_input_devices()
        for device_id in devices:
            try:
                subprocess.run(['xinput', 'disable', device_id], 
                              capture_output=True, check=True)
                self.blocked_devices.append(device_id)
            except:
                pass
        
        print(f"   Blocked {len(self.blocked_devices)} devices")
        return len(self.blocked_devices) > 0
    
    def unblock_inputs(self):
        """Re-enable all input devices."""
        print("🔓 Unblocking input devices...")
        
        for device_id in self.blocked_devices:
            try:
                subprocess.run(['xinput', 'enable', device_id], 
                              capture_output=True)
            except:
                pass
        
        self.blocked_devices = []
        print("   Input devices restored")
    
    def show_warning_overlay(self):
        """Show fullscreen warning using zenity."""
        
        # Create warning script
        warning_script = """#!/bin/bash
        zenity --warning \
            --title="⚠️ SCITEX AUTOMATION RUNNING" \
            --text="<span size='xx-large' weight='bold'>🤖 PDF DOWNLOAD IN PROGRESS</span>\n\n<span size='x-large'>DO NOT TOUCH KEYBOARD OR MOUSE</span>\n\n<span size='large'>Automated download running...</span>\n\nThis window will close when complete" \
            --width=600 \
            --height=300 \
            --no-wrap &
        """
        
        try:
            self.warning_process = subprocess.Popen(
                ['bash', '-c', warning_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("⚠️  Warning overlay displayed")
        except:
            pass
    
    def close_warning_overlay(self):
        """Close the warning overlay."""
        if self.warning_process:
            try:
                self.warning_process.terminate()
                self.warning_process = None
                print("   Warning overlay closed")
            except:
                pass

class ZoteroAutomation:
    """Handles the Zotero save automation."""
    
    def __init__(self, blocker):
        self.blocker = blocker
        
    def inject_browser_overlay(self):
        """Inject JavaScript overlay into Chrome using xdotool."""
        
        print("💉 Injecting browser overlay...")
        
        # JavaScript to create overlay
        js_code = '''
        (function() {
            if (document.getElementById("scitex-block")) return;
            var d = document.createElement("div");
            d.id = "scitex-block";
            d.style.cssText = "position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.95);z-index:2147483647;display:flex;align-items:center;justify-content:center;pointer-events:all;cursor:not-allowed";
            d.innerHTML = "<div style=\'text-align:center;color:white;font-family:sans-serif\'><h1 style=\'font-size:48px;margin:0\'>🤖 SciTeX Downloading</h1><p style=\'font-size:24px;margin:20px\'>Please wait...</p><div style=\'width:300px;height:4px;background:rgba(255,255,255,0.3);margin:20px auto;border-radius:2px\'><div style=\'width:50%;height:100%;background:white;animation:load 2s infinite;border-radius:2px\'></div></div></div><style>@keyframes load{0%,100%{width:0}50%{width:100%}}</style>";
            document.body.appendChild(d);
            document.body.style.overflow = "hidden";
            document.addEventListener("click", function(e){e.stopPropagation();e.preventDefault()}, true);
            document.addEventListener("keydown", function(e){e.stopPropagation();e.preventDefault()}, true);
        })();
        '''
        
        # Open developer console
        subprocess.run(['xdotool', 'key', 'F12'], capture_output=True)
        time.sleep(1)
        
        # Switch to console
        subprocess.run(['xdotool', 'key', 'Escape'], capture_output=True)
        time.sleep(0.5)
        subprocess.run(['xdotool', 'type', '--delay', '5', js_code], capture_output=True)
        subprocess.run(['xdotool', 'key', 'Return'], capture_output=True)
        time.sleep(0.5)
        
        # Close developer console
        subprocess.run(['xdotool', 'key', 'F12'], capture_output=True)
        time.sleep(0.5)
        
        print("   Browser overlay injected")
    
    def save_current_tab(self):
        """Trigger Zotero save on current tab."""
        subprocess.run(['xdotool', 'key', 'ctrl+shift+s'], capture_output=True)
    
    def next_tab(self):
        """Switch to next Chrome tab."""
        subprocess.run(['xdotool', 'key', 'ctrl+Tab'], capture_output=True)
    
    def run_automation(self, num_tabs=15):
        """Run the full automation with blocking."""
        
        print("\n" + "=" * 80)
        print("ZOTERO AUTOMATED SAVE - STARTING")
        print("=" * 80)
        
        # Show warning overlay
        self.blocker.show_warning_overlay()
        time.sleep(2)
        
        # Block inputs
        if not self.blocker.block_inputs():
            print("⚠️  Warning: Could not block all input devices")
            print("   Continuing anyway...")
        
        time.sleep(1)
        
        # Focus Chrome
        print("\n📍 Focusing Chrome window...")
        subprocess.run(['xdotool', 'search', '--name', 'Google Chrome', 'windowactivate'],
                      capture_output=True)
        time.sleep(1)
        
        # Go to first tab
        print("📑 Going to first tab...")
        subprocess.run(['xdotool', 'key', 'ctrl+1'], capture_output=True)
        time.sleep(2)
        
        # Inject overlay on first tab
        self.inject_browser_overlay()
        
        print("\n🤖 AUTOMATION RUNNING\n")
        
        # Process each tab
        for i in range(num_tabs):
            print(f"Tab {i+1}/{num_tabs}: ", end='', flush=True)
            
            # Wait for page
            time.sleep(2)
            
            # Save with Zotero
            self.save_current_tab()
            print("Saving", end='', flush=True)
            
            # Wait for save to complete
            for j in range(5):
                time.sleep(1)
                print(".", end='', flush=True)
            
            print(" ✓")
            
            # Move to next tab
            if i < num_tabs - 1:
                self.next_tab()
                time.sleep(0.5)
                
                # Inject overlay on new tab too
                if i % 5 == 0:  # Every 5 tabs
                    self.inject_browser_overlay()
        
        print("\n" + "=" * 80)
        print("✅ AUTOMATION COMPLETE!")
        print("=" * 80)

def cleanup(blocker):
    """Cleanup function to ensure inputs are unblocked."""
    blocker.unblock_inputs()
    blocker.close_warning_overlay()

def main():
    """Main entry point."""
    
    print("=" * 80)
    print("ZOTERO AUTOMATED SAVE WITH INPUT BLOCKING")
    print("=" * 80)
    
    # Check requirements
    for cmd in ['xdotool', 'xinput', 'zenity']:
        try:
            subprocess.run(['which', cmd], check=True, capture_output=True)
        except:
            print(f"❌ {cmd} not installed!")
            print(f"   Install with: sudo apt-get install {cmd}")
            sys.exit(1)
    
    print("\n✅ All requirements met")
    
    # Get parameters
    try:
        num_tabs = int(input("\nNumber of tabs to process (default 15): ") or "15")
    except:
        num_tabs = 15
    
    print(f"\nWill process {num_tabs} tabs")
    print("Total time: ~{} seconds".format(num_tabs * 7))
    
    print("\n⚠️  WARNING:")
    print("- Keyboard and mouse will be DISABLED during automation")
    print("- A warning overlay will appear")
    print("- Chrome must be open with papers loaded")
    print("- To emergency stop: Press Ctrl+Alt+F2, login, and run:")
    print("  xinput enable <device-id>")
    
    response = input("\nReady to start? (y/n): ").strip().lower()
    if response != 'y':
        print("Cancelled.")
        return
    
    # Create blocker and set up cleanup
    blocker = InputBlocker()
    atexit.register(cleanup, blocker)
    signal.signal(signal.SIGINT, lambda s, f: cleanup(blocker))
    signal.signal(signal.SIGTERM, lambda s, f: cleanup(blocker))
    
    # Create automation
    automation = ZoteroAutomation(blocker)
    
    print("\nStarting in 5 seconds...")
    print("SWITCH TO CHROME NOW!")
    for i in range(5, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    try:
        # Run automation
        automation.run_automation(num_tabs)
    finally:
        # Always cleanup
        cleanup(blocker)
    
    print("\n✨ All done! Check Zotero for saved papers and PDFs.")

if __name__ == "__main__":
    main()