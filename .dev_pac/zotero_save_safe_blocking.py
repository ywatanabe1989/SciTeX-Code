#!/usr/bin/env python3
"""
Safer version with fullscreen blocking window instead of disabling devices.
Shows a fullscreen window that captures all input during automation.
"""

import subprocess
import time
import threading
import tkinter as tk
from tkinter import ttk

class BlockingOverlay:
    """Fullscreen window that blocks input."""
    
    def __init__(self):
        self.root = None
        self.thread = None
        
    def create_window(self):
        """Create fullscreen blocking window."""
        self.root = tk.Tk()
        self.root.title("SciTeX Automation")
        
        # Make fullscreen
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.configure(bg='black')
        
        # Override close button
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Capture all key events
        self.root.bind("<Key>", lambda e: "break")
        self.root.bind("<Button>", lambda e: "break")
        
        # Main frame
        frame = tk.Frame(self.root, bg='black')
        frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Title
        title = tk.Label(
            frame,
            text="🤖 SciTeX PDF Download",
            font=('Arial', 48, 'bold'),
            fg='white',
            bg='black'
        )
        title.pack(pady=20)
        
        # Subtitle
        subtitle = tk.Label(
            frame,
            text="Automated download in progress",
            font=('Arial', 24),
            fg='#888888',
            bg='black'
        )
        subtitle.pack(pady=10)
        
        # Warning
        warning = tk.Label(
            frame,
            text="⚠️ DO NOT TOUCH KEYBOARD OR MOUSE",
            font=('Arial', 20, 'bold'),
            fg='#ff6b6b',
            bg='black'
        )
        warning.pack(pady=20)
        
        # Progress bar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TProgressbar", 
                       background='#4a90e2',
                       troughcolor='#222222',
                       bordercolor='black',
                       lightcolor='#4a90e2',
                       darkcolor='#4a90e2')
        
        self.progress = ttk.Progressbar(
            frame,
            length=400,
            mode='indeterminate',
            style="TProgressbar"
        )
        self.progress.pack(pady=30)
        self.progress.start(10)
        
        # Status
        self.status = tk.Label(
            frame,
            text="Initializing...",
            font=('Arial', 16),
            fg='#cccccc',
            bg='black'
        )
        self.status.pack(pady=10)
        
        # Counter
        self.counter = tk.Label(
            frame,
            text="",
            font=('Arial', 14),
            fg='#888888',
            bg='black'
        )
        self.counter.pack(pady=5)
        
        # Focus the window
        self.root.focus_force()
        self.root.grab_set()
        
    def show(self):
        """Show the blocking window in a separate thread."""
        def run():
            self.create_window()
            self.root.mainloop()
        
        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()
        time.sleep(1)  # Give window time to appear
        
    def update_status(self, text):
        """Update status text."""
        if self.root:
            self.root.after(0, lambda: self.status.config(text=text))
    
    def update_counter(self, text):
        """Update counter text."""
        if self.root:
            self.root.after(0, lambda: self.counter.config(text=text))
    
    def close(self):
        """Close the blocking window."""
        if self.root:
            self.root.after(0, self.root.destroy)
            time.sleep(0.5)

def run_automation_with_overlay(num_tabs=15):
    """Run automation with blocking overlay."""
    
    # Create and show overlay
    overlay = BlockingOverlay()
    overlay.show()
    
    try:
        # Focus Chrome
        overlay.update_status("Focusing Chrome window...")
        subprocess.run(['xdotool', 'search', '--name', 'Google Chrome', 'windowactivate'],
                      capture_output=True)
        time.sleep(1)
        
        # Go to first tab
        overlay.update_status("Going to first tab...")
        subprocess.run(['xdotool', 'key', 'ctrl+1'], capture_output=True)
        time.sleep(2)
        
        # Process tabs
        for i in range(num_tabs):
            overlay.update_status(f"Processing tab {i+1} of {num_tabs}")
            overlay.update_counter(f"Tab {i+1}/{num_tabs}")
            
            # Wait for page
            time.sleep(2)
            
            # Save with Zotero
            overlay.update_status(f"Saving with Zotero...")
            subprocess.run(['xdotool', 'key', 'ctrl+shift+s'], capture_output=True)
            
            # Wait for save
            for j in range(5):
                overlay.update_counter(f"Tab {i+1}/{num_tabs} - Saving{'.' * (j+1)}")
                time.sleep(1)
            
            # Next tab
            if i < num_tabs - 1:
                subprocess.run(['xdotool', 'key', 'ctrl+Tab'], capture_output=True)
                time.sleep(0.5)
        
        overlay.update_status("✅ Complete!")
        overlay.update_counter(f"Processed {num_tabs} tabs successfully")
        time.sleep(2)
        
    finally:
        overlay.close()

def main():
    """Main entry point."""
    
    print("=" * 80)
    print("ZOTERO SAFE AUTOMATED SAVE")
    print("=" * 80)
    print("\nThis version uses a fullscreen window to block input")
    print("(Safer than disabling input devices)")
    
    # Check xdotool
    try:
        subprocess.run(['which', 'xdotool'], check=True, capture_output=True)
    except:
        print("❌ xdotool not installed!")
        print("   Install with: sudo apt-get install xdotool")
        return
    
    # Get number of tabs
    try:
        num_tabs = int(input("\nNumber of tabs (default 15): ") or "15")
    except:
        num_tabs = 15
    
    print(f"\nWill process {num_tabs} tabs")
    print(f"Estimated time: {num_tabs * 7} seconds")
    
    print("\n📋 Checklist:")
    print("✓ Chrome is open with paper tabs")
    print("✓ Zotero Desktop is running")
    print("✓ Zotero WSL Proxy is active")
    print("✓ Logged into institutional access")
    
    if input("\nReady? (y/n): ").lower() == 'y':
        print("\nStarting in 3 seconds...")
        print("A fullscreen blocking window will appear!")
        time.sleep(3)
        
        run_automation_with_overlay(num_tabs)
        
        print("\n✅ Complete! Check Zotero for saved papers.")
    else:
        print("Cancelled.")

if __name__ == "__main__":
    main()