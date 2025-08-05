#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-03 15:29:41 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/local/utils/_ChromeExtensionManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/local/utils/_ChromeExtensionManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
import shutil
import subprocess
import webbrowser
from typing import Dict, Optional

from scitex import logging

from ....config import ScholarConfig

logger = logging.getLogger(__name__)


class ChromeExtensionManager:
    """Manages Chrome extensions for automated literature search."""

    EXTENSIONS = {
        "lean_library": {
            "id": "hghakoefmnkhamdhenpbogkeopjlkpoa",
            "name": "Lean Library",
            "description": "Academic access redirection",
        },
        "popup_blocker": {
            "id": "bkkbcggnhapdmkeljlodobbkopceiche",
            "name": "Pop-up Blocker",
            "description": "Block popups and ads",
        },
        "accept_cookies_async": {
            "id": "ofpnikijgfhlmmjlpkfaifhhdonchhoi",
            "name": "Accept all cookies",
            "description": "Auto-accept cookie prompts",
        },
        "captcha_solver_2captcha": {
            "id": "ifibfemgeogfhoebkmokieepdoobkbpo",
            "name": "2Captcha Solver",
            "description": "reCAPTCHA v2/v3 solving",
        },
        "captcha_solver_hcaptcha": {
            "id": "hlifkpholllijblknnmbfagnkjneagid",
            "name": "CAPTCHA Solver",
            "description": "hCaptcha solving",
        },
    }

    def __init__(
        self,
        profile_name: str = "scholar_default",
        config: Optional[ScholarConfig] = None,
    ):
        """Initialize extension manager.

        Args:
            profile_name: Chrome profile name
            config: Scholar configuration instance
        """
        self.profile_name = profile_name
        self.config = config or ScholarConfig()
        self.cache_dir = self.config.get_chrome_cache_dir()
        # Provide profile_dir alias for compatibility with BrowserManager
        self.profile_dir = self.cache_dir

    def _detect_wsl2_environment(self) -> bool:
        """Detect if running in WSL2 environment."""
        try:
            with open('/proc/version', 'r') as f:
                version_info = f.read().lower()
                return 'microsoft' in version_info and 'wsl' in version_info
        except:
            return False

    def _find_chrome_executable(self) -> Optional[str]:
        """Find Chrome executable on the system."""
        # Common Chrome executable names in order of preference
        chrome_names = [
            "google-chrome-stable",
            "google-chrome",
            "chromium-browser", 
            "chromium",
            "chrome"
        ]
        
        for chrome_name in chrome_names:
            chrome_path = shutil.which(chrome_name)
            if chrome_path:
                logger.info(f"Found Chrome at: {chrome_path}")
                
                # WSL2 environment detection and warning
                if self._detect_wsl2_environment():
                    logger.info("🖥️ WSL2 environment detected")
                    logger.info("📺 Display forwarding required for Chrome visibility")
                    
                return chrome_name
        
        logger.warning("No Chrome executable found in PATH")
        return None

    async def install_extensions_fallback_async(self):
        """Install extensions using default browser as fallback."""
        logger.info("🌐 Opening extension URLs in default browser...")
        
        urls = []
        for key, ext_info in self.EXTENSIONS.items():
            ext_id = ext_info["id"]
            url = f"https://chrome.google.com/webstore/detail/{ext_id}"
            urls.append((ext_info['name'], url))
            
        logger.info(f"📋 Opening {len(urls)} extension pages:")
        
        for name, url in urls:
            try:
                webbrowser.open(url)
                logger.success(f"✅ Opened {name}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to open {name}: {e}")
                logger.info(f"  Manual URL: {url}")
        
        logger.info("\n" + "=" * 60)
        logger.info("INSTRUCTIONS:")
        logger.info("1. Install each extension by clicking 'Add to Chrome'")
        logger.info("2. Accept any permissions requested")
        logger.info("3. Repeat for all extension tabs")
        logger.info("=" * 60)

    async def check_extensions_installed_async(self) -> Dict[str, bool]:
        """Check installation status of all extensions."""
        status = {}
        extensions_path = self.cache_dir / "Default" / "Extensions"

        if not extensions_path.exists():
            logger.warning(
                f"Extensions directory not found: {extensions_path}"
            )
            return {key: False for key in self.EXTENSIONS}

        for key, ext_info in self.EXTENSIONS.items():
            ext_id = ext_info["id"]
            ext_dir = extensions_path / ext_id

            # Check if extension directory exists and has a valid version
            if ext_dir.exists():
                version_dirs = [d for d in ext_dir.iterdir() if d.is_dir()]
                if version_dirs:
                    # Check for manifest.json in latest version
                    latest_version = max(version_dirs, key=lambda x: x.name)
                    manifest_file = latest_version / "manifest.json"
                    status[key] = manifest_file.exists()
                    if status[key]:
                        logger.info(
                            f"✓ {ext_info['name']} ({ext_id}) is installed"
                        )
                    else:
                        logger.warning(
                            f"✗ {ext_info['name']} ({ext_id}) directory exists but no manifest"
                        )
                else:
                    status[key] = False
                    logger.warning(
                        f"✗ {ext_info['name']} ({ext_id}) directory exists but no versions"
                    )
            else:
                status[key] = False
                logger.warning(
                    f"✗ {ext_info['name']} ({ext_id}) is not installed"
                )

        return status

    async def install_extensions_interactive_async(self):
        """
        Open regular Chrome browser for manual extension installation.
        
        This method opens a human-controlled Chrome browser (not automated by Playwright)
        because Chrome Web Store blocks extension installation in automated browsers.
        The extensions are installed to the shared profile cache, so Playwright can
        use them afterwards for automated literature search.
        """
        logger.info("\n" + "=" * 60)
        logger.info("Chrome Extension Installation (Human-Controlled Browser)")
        logger.info("=" * 60)

        logger.info(f"\n⚠ Need to install ({len(self.EXTENSIONS)}):")
        for key, ext in self.EXTENSIONS.items():
            logger.info(f"  - {ext['name']}: {ext['description']}")

        logger.info("\n🔍 Looking for Chrome executable...")
        chrome_exec = self._find_chrome_executable()
        
        if not chrome_exec:
            logger.error("❌ Chrome not found. Please install extensions manually:")
            for key, ext_info in self.EXTENSIONS.items():
                ext_id = ext_info["id"]
                url = f"https://chrome.google.com/webstore/detail/{ext_id}"
                logger.info(f"  {url}")
            return

        logger.info(f"🚀 Opening regular Chrome browser ({chrome_exec})...")
        logger.info("📋 This will open a HUMAN-CONTROLLED Chrome (not automated)")

        # Chrome command for human-controlled browser (NOT automated)
        # Key differences from Playwright browser:
        # - No --remote-debugging-port (prevents automation detection)
        # - No --disable-blink-features=AutomationControlled
        # - No automation-related flags that trigger "controlled by test software" message
        
        # WSL2-optimized Chrome arguments for better visibility and persistence
        if self._detect_wsl2_environment():
            logger.info("🖥️ Using WSL2-optimized Chrome arguments for maximum visibility")
            
            # Use the main Scholar profile for extension installation
            # This ensures extensions are installed to the profile that Playwright will use
            chrome_cmd = [
                chrome_exec,
                f"--user-data-dir={self.cache_dir}",  # Use Scholar profile cache
                "--enable-extensions",  # Allow extension installation
                "--no-first-run",  # Skip first run setup
                "--disable-default-browser-check",  # Skip default browser prompt
                "--new-window",  # Force new window
                "--start-maximized",  # Maximize for WSL2 visibility
                "--force-device-scale-factor=1",  # Prevent scaling issues
                "--high-dpi-support=1",  # Better display support
                "--disable-background-mode",  # Prevent Chrome from running in background
                "--keep-alive-for-test",  # Keep process alive
                "--no-sandbox",  # Better WSL2 compatibility
                "--disable-gpu-sandbox",  # Prevent GPU issues in WSL2
                "--disable-software-rasterizer",  # Prevent rendering issues
                # IMPORTANT: Focus and visibility flags for WSL2
                "--focus-on-open",  # Keep focus when opening
                "--restore-last-session",  # Prevent session conflicts
            ]
        else:
            # Standard arguments for non-WSL2 environments
            chrome_cmd = [
                chrome_exec,
                f"--user-data-dir={self.cache_dir}",  # Use Scholar profile cache
                "--enable-extensions",  # Allow extension installation
                "--window-size=1200,800",  # Ensure visible window size
                "--window-position=100,100",  # Position on screen
                "--no-first-run",  # Skip first run setup
                "--disable-default-browser-check",  # Skip default browser prompt
                "--new-window",  # Force new window
            ]
        # IMPORTANT: We deliberately avoid automation flags here so Chrome Web Store
        # doesn't show_async "Chrome is being controlled by automated test software" message

        # Add extension URLs
        for key, ext_info in self.EXTENSIONS.items():
            ext_id = ext_info["id"]
            url = f"https://chrome.google.com/webstore/detail/{ext_id}"
            chrome_cmd.append(url)

        try:
            if self._detect_wsl2_environment():
                logger.info("🚀 Launching Chrome maximized for WSL2 visibility")
            else:
                logger.info("🚀 Launching Chrome with window size 1200x800 at position (100,100)")
            
            # IMPORTANT FIX for WSL2: Use simplified launch for better compatibility
            # The user confirmed that just running `google-chrome` works fine
            if self._detect_wsl2_environment():
                logger.info("🖥️ Using WSL2-optimized Chrome launch with maximized window")
                # Simple launch for WSL2 - no complex process management
                process = subprocess.Popen(
                    chrome_cmd, 
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL,
                )
            else:
                logger.info("🖥️ Using standard Chrome launch with positioned window")
                # For non-WSL2: use detached process
                process = subprocess.Popen(
                    chrome_cmd, 
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,  # Start in new session to fully detach
                    preexec_fn=os.setsid if hasattr(os, 'setsid') else None  # Create new process group
                )
                
            logger.success(f"✅ Chrome launched successfully (PID: {process.pid})")
            
            if self._detect_wsl2_environment():
                logger.info("📱 Chrome should appear MAXIMIZED on your Windows desktop")
                logger.info("🖥️ If not visible, check Windows taskbar or try Alt+Tab")
            else:
                logger.info("📱 Chrome window should be visible on your screen")
            
            # Give Chrome a moment to start up and become visible
            import time
            time.sleep(3)  # Wait for Chrome to start
            
            # Check if process is still running 
            if process.poll() is None:
                logger.success("🔍 Chrome process is running")
                
                if self._detect_wsl2_environment():
                    logger.info("🖥️ Chrome should be maximized and visible on Windows desktop")
                    logger.info("💡 If Chrome is not visible:")
                    logger.info("   1. Check Windows taskbar (Chrome icon)")
                    logger.info("   2. Try Alt+Tab to switch to Chrome")
                    logger.info("   3. Click Chrome icon in taskbar if minimized")
                    logger.info("   4. Chrome may need manual activation in WSL2")
                    
                    # Try to activate Chrome window using Windows-specific method
                    try:
                        # Send a notification to help user find Chrome
                        logger.info("🔔 Attempting to bring Chrome to foreground...")
                        # Use Windows PowerShell to activate Chrome if available
                        ps_cmd = "powershell.exe -Command \"Add-Type -AssemblyName Microsoft.VisualBasic; [Microsoft.VisualBasic.Interaction]::AppActivate('Google Chrome')\""
                        subprocess.run(ps_cmd, shell=True, capture_output=True, timeout=2)
                        logger.info("📱 Attempted to activate Chrome window")
                    except:
                        # Fallback: just inform user
                        pass
                else:
                    logger.info("🖥️ Chrome window should now be visible for extension installation")
            else:
                logger.warning("⚠️ Chrome process exited immediately - display issue likely")
                
        except Exception as e:
            logger.error(f"❌ Failed to launch Chrome: {e}")
            logger.info("Please install extensions manually:")
            for key, ext_info in self.EXTENSIONS.items():
                ext_id = ext_info["id"]
                url = f"https://chrome.google.com/webstore/detail/{ext_id}"
                logger.info(f"  {url}")

        logger.warn("\n" + "=" * 60)
        logger.warn("🔧 EXTENSION INSTALLATION INSTRUCTIONS:")
        
        if self._detect_wsl2_environment():
            logger.warn("🖥️ WSL2 ENVIRONMENT DETECTED:")
            logger.warn("1. Chrome should now be visible on your Windows desktop")
            logger.warn("2. If Chrome is not visible, try: export DISPLAY=:0")
            logger.warn("3. Or use Windows Chrome and copy profile after installation")
        else:
            logger.warn("1. A regular Chrome browser should open (NOT automated)")
            
        logger.warn("2. Login to your Google account if prompted")
        logger.warn("3. Extension pages should open automatically")
        logger.warn("4. Click 'Add to Chrome' for each extension tab")
        logger.warn("5. Accept any permissions requested")
        logger.warn("6. Close Chrome when all extensions are installed")
        logger.warn("7. Extensions will be saved to the Scholar profile")
        logger.warn("=" * 60)
        
        logger.info("\n📋 Manual URLs (if needed):")
        for key, ext_info in self.EXTENSIONS.items():
            ext_id = ext_info["id"]
            url = f"https://chrome.google.com/webstore/detail/{ext_id}"
            logger.info(f"• {ext_info['name']}: {url}")
        
        logger.info(f"\n💾 Extensions will be saved to: {self.cache_dir}")

        input("\nPress Enter when done installing extensions...")
        logger.success("✅ Extension installation complete!")
        logger.info("🔄 Playwright will now use the profile with installed extensions")

    async def check_lean_library_active_async(self, page, url: str) -> bool:
        """Check if Lean Library is providing PDF access."""
        try:
            await page.goto(url)
            await page.wait_for_timeout(3000)

            pdf_selectors = [
                '[data-lean-library="pdf"]',
                ".lean-library-pdf",
                'button:has-text("PDF")',
                'a:has-text("Get PDF")',
                ".ll-pdf-button",
            ]

            for selector in pdf_selectors:
                element = await page.query_selector(selector)
                if element:
                    return True

            return False
        except Exception as e:
            logger.error(f"Error checking Lean Library: {e}")
            return False

    def get_extension_info(self) -> Dict:
        """Get extension manager information."""
        return {
            "profile_name": self.profile_name,
            "profile_path": str(self.cache_dir),
            "profile_exists": self.cache_dir.exists(),
        }

    def reset_profile(self):
        """Reset Chrome profile."""
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            logger.success(f"Chrome profile reset: {self.profile_name}")
        self._ensure_cache_directory()

# EOF
