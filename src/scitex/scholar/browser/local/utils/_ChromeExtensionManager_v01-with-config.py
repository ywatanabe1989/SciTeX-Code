#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-03 19:55:58 (ywatanabe)"
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
from pathlib import Path
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
        config: Optional[ScholarConfig] = None
    ):
        """Initialize extension manager.

        Args:
            profile_name: Chrome profile name
            config: Scholar configuration instance
        """
        self.profile_name = profile_name
        self.config = config or ScholarConfig()
        self.profile_dir = self._get_profile_path(profile_name)
        self._ensure_profile_directory()

    def _get_profile_path(self, profile_name: str) -> Path:
        """Get Chrome profile path using config manager."""
        # Use config system for proper cache directory management
        chrome_cache_dir = self.config.get_chrome_cache_dir()
        return chrome_cache_dir / profile_name

    def _ensure_profile_directory(self):
        """Ensure profile directory exists."""
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Chrome profile directory: {self.profile_dir}")

    async def check_extensions_installed_async(self) -> Dict[str, bool]:
        """Check installation status of all extensions from profile directory."""
        status = {}
        extensions_path = self.profile_dir / "Default" / "Extensions"

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
                            f"✓ {ext_info['name']} ({ext_id}) is installed at {latest_version}"
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
        """Open Chrome for manual extension installation."""
        print("\n" + "=" * 60)
        print("Chrome Extension Installation")
        print("=" * 60)

        print(f"\n⚠ Need to install ({len(self.EXTENSIONS)}):")
        for key, ext in self.EXTENSIONS.items():
            print(f"  - {ext['name']}: {ext['description']}")

        print("\nOpening Chrome...")

        chrome_cmd = [
            "google-chrome-stable",
            f"--user-data-dir={self.profile_dir}",
            "--enable-extensions",
        ]

        # Add extension URLs
        for key, ext_info in self.EXTENSIONS.items():
            ext_id = ext_info["id"]
            url = f"https://chrome.google.com/webstore/detail/{ext_id}"
            chrome_cmd.append(url)

        try:
            subprocess.Popen(chrome_cmd)
        except FileNotFoundError:
            print("Chrome not found. Please install extensions manually:")
            for key, ext_info in self.EXTENSIONS.items():
                ext_id = ext_info["id"]
                url = f"https://chrome.google.com/webstore/detail/{ext_id}"
                print(f"  {url}")

        print("\n" + "=" * 60)
        print("INSTRUCTIONS:")
        print("1. Login to your Google account (IMPORTANT)")
        print("2. Click 'Add to Chrome' for each extension")
        print("3. Accept any permissions requested")
        print("4. Close the browser when done")
        print("=" * 60)

        input("\nPress Enter when done installing extensions...")
        print("\n✓ Extension installation complete!")

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
            "profile_path": str(self.profile_dir),
            "profile_exists": self.profile_dir.exists(),
        }

    def reset_profile(self):
        """Reset Chrome profile."""
        if self.profile_dir.exists():
            shutil.rmtree(self.profile_dir)
            logger.success(f"Chrome profile reset: {self.profile_name}")
        self._ensure_profile_directory()

# EOF
