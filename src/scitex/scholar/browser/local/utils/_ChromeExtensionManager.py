#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-04 06:54:33 (ywatanabe)"
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
            "description": "reCAPTCHA v2/v3 solving (may need API for advanced features)",
        },
        "captcha_solver_hcaptcha": {
            "id": "hlifkpholllijblknnmbfagnkjneagid",
            "name": "CAPTCHA Solver",
            "description": "hCaptcha solving (may need API for advanced features)",
        },
    }

    AVAILABLE_PROFILE_NAMES = [
        "extension",
        "auth",
        "stealth",
        "debug",
    ]

    def __init__(
        self,
        profile_name: str,
        config: Optional[ScholarConfig] = None,
    ):
        """Initialize extension manager.

        Args:
            profile_name: Chrome profile name
            config: Scholar configuration instance
        """
        assert profile_name in self.AVAILABLE_PROFILE_NAMES, (
            f"Profile '{profile_name}' not allowed. Please specify from: {self.AVAILABLE_PROFILE_NAMES}."
            "This is due to Chrome limitations: "
        )
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
        logger.warn(f"Chrome profile directory: {self.profile_dir}")

    def _get_installed_extension_paths(self) -> list[str]:
        """Get paths to installed extensions for --load-extension argument."""
        extension_paths = []
        extensions_dir = self.profile_dir / "Default" / "Extensions"

        if not extensions_dir.exists():
            logger.warning(f"Extensions directory not found: {extensions_dir}")
            return extension_paths

        for key, ext_info in self.EXTENSIONS.items():
            ext_id = ext_info["id"]
            ext_dir = extensions_dir / ext_id

            if ext_dir.exists():
                # Find the latest version directory
                version_dirs = [d for d in ext_dir.iterdir() if d.is_dir()]
                if version_dirs:
                    latest_version = max(version_dirs, key=lambda x: x.name)
                    manifest_file = latest_version / "manifest.json"
                    if manifest_file.exists():
                        extension_paths.append(str(latest_version))
                        logger.info(
                            f"Extension path added: {ext_info['name']} -> {latest_version}"
                        )

        logger.info(
            f"Found {len(extension_paths)} extension paths for loading"
        )
        return extension_paths

    async def check_extensions_installed_async(self) -> bool:
        """Check installation status of all extensions from profile directory."""
        status = {}
        extensions_path = self.profile_dir / "Default" / "Extensions"

        if not extensions_path.exists():
            logger.warning(
                f"Extensions directory not found: {extensions_path}"
            )
            status = {key: False for key in self.EXTENSIONS}

        else:
            for key, ext_info in self.EXTENSIONS.items():
                ext_id = ext_info["id"]
                ext_dir = extensions_path / ext_id

                # Check if extension directory exists and has a valid version
                if ext_dir.exists():
                    version_dirs = [d for d in ext_dir.iterdir() if d.is_dir()]
                    if version_dirs:
                        # Check for manifest.json in latest version
                        latest_version = max(
                            version_dirs, key=lambda x: x.name
                        )
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

        # Status to bool
        installed_count = sum(status.values())
        print(
            f"Found {installed_count}/{len(self.EXTENSIONS)} extensions installed"
        )
        is_all_installed = installed_count == len(self.EXTENSIONS)
        return is_all_installed

    async def install_extensions_interactive_asyncly_if_not_installed(self):
        """Open Chrome for manual extension installation.
        IMPORTANT: Why we use regular Chrome instead of Playwright:
        1. Playwright-controlled browsers show_async "Chrome is being controlled by automated test software"
        2. Chrome Web Store blocks extension installation when this message appears
        3. Extensions can only be installed in "human-controlled" browsers
        4. Once installed to the profile, Playwright can use them automatically
        5. This is a one-time setup - afterwards Playwright reuses the profile with extensions
        """
        if await self.check_extensions_installed_async():
            return True
        else:
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

            try:
                print("\n" + "=" * 60)
                print("INSTRUCTIONS:")
                print("1. Login to your Google account (IMPORTANT)")
                print("2. Click 'Add to Chrome' for each extension")
                print("3. Accept any permissions requested")
                print("4. Close the browser when done")
                print("=" * 60)

                input("\nPress Enter when done installing extensions...")
                print("\n✓ Extension installation complete!")
                return True
            except Exception as e:
                logger.warn(e)
                return False

    async def check_lean_library_active_async(
        self, page, url: str, timeout_sec=5
    ) -> bool:
        """Check if Lean Library is providing PDF access."""
        try:
            await page.goto(url)
            logger.info(
                f"Checking Lean Library Activated (Timeout: {timeout_sec}s)"
            )
            await page.wait_for_timeout(timeout_sec * 1000)

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
                    logger.succes(f"PDF Lean Library Button Found on {url}")
                    return True

            logger.fail(f"PDF Lean Library Button Not Found on {url}")
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

    def get_extension_args(self):
        extension_paths = self._get_installed_extension_paths()
        extension_args = []
        if extension_paths:
            # Load extensions explicitly with both required flags
            extensions_list = ",".join(extension_paths)
            # See https://playwright.dev/docs/chrome-extensions
            extension_args.extend(
                [
                    f"--load-extension={extensions_list}",
                    f"--disable-extensions-except={extensions_list}",
                ]
            )
            logger.info(
                f"Loading {len(extension_paths)} extensions explicitly with both flags"
            )

        # Add extension-related args for better compatibility
        extension_args.extend(
            [
                "--enable-extensions",
                "--disable-extensions-file-access-check",
                "--enable-extension-activity-logging",
                "--disable-web-security",  # Some extensions require this
                "--disable-features=VizDisplayCompositor",  # Better extension compatibility
            ]
        )
        return extension_args

    def reset_profile(self):
        """Reset Chrome profile."""
        if self.profile_dir.exists():
            shutil.rmtree(self.profile_dir)
            logger.success(f"Chrome profile reset: {self.profile_name}")
        self._ensure_profile_directory()


if __name__ == "__main__":

    def main():
        """Simple demonstration of extension installation and checking."""
        import asyncio

        PROFILE_NAME = ["extension", "auth", "stealth", "debug"][0]

        # Create extension manager
        manager = ChromeExtensionManager(PROFILE_NAME)

        print("Chrome Extension Manager Demo")
        print("=" * 40)

        # Check current status
        print("\nChecking current extensions...")
        is_all_installed = asyncio.run(manager.check_extensions_installed_async())

        # If not all installed, offer to install
        if not is_all_installed:
            answer = input("Install missing extensions? (y/n): ")
            if answer.lower() == "y":
                print("\nStarting installation...")
                asyncio.run(
                    manager.install_extensions_interactive_asyncly_if_not_installed()
                )

                # Check again after installation
                print("\nRe-checking extensions...")
                new_status = asyncio.run(manager.check_extensions_installed_async())
                new_installed = sum(new_status.values())
                print(
                    f"Now have {new_installed}/{len(manager.EXTENSIONS)} extensions installed"
                )

    main()

# python -m src.scitex.scholar.browser.local.utils._ChromeExtensionManager

# EOF
