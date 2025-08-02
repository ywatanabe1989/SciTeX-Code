#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-02 11:44:33 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/local/_ChromeExtensionManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/local/_ChromeExtensionManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import shutil
import subprocess
from pathlib import Path
from typing import Dict

from scitex import logging

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
        "accept_cookies": {
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

    def __init__(self, profile_name: str = "scholar_default"):
        """Initialize extension manager.

        Args:
            profile_name: Chrome profile name
        """
        self.profile_name = profile_name
        self.profile_dir = self._get_profile_path(profile_name)
        self._ensure_profile_directory()

    def _get_profile_path(self, profile_name: str) -> Path:
        """Get Chrome profile path."""
        base_dir = Path(os.environ.get("SCITEX_DIR", Path.home() / ".scitex"))
        return base_dir / "scholar" / "profiles" / profile_name

    def _ensure_profile_directory(self):
        """Ensure profile directory exists."""
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Chrome profile directory: {self.profile_dir}")

    async def check_extensions_installed(self) -> Dict[str, bool]:
        """Check installation status of all extensions."""
        # Is this implementation correct?
        return {key: False for key in self.EXTENSIONS}

    async def install_extensions_interactive(self):
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

    async def check_lean_library_active(self, page, url: str) -> bool:
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
