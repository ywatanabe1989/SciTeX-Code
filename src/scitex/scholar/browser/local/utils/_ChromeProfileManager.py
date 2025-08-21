#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 14:27:54 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/local/utils/_ChromeProfileManager.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/local/utils/_ChromeProfileManager.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import subprocess
import time
from pathlib import Path
from typing import Dict, Optional

from scitex import logging
from scitex.scholar.config import ScholarConfig

logger = logging.getLogger(__name__)


class ChromeProfileManager:
    """Manages Chrome profile especially extensions for automated literature search."""

    EXTENSIONS = {
        "zotero_connector": {
            "id": "ekhagklcjbdpajgpjgmbionohlpdbjgc",
            "name": "Zotero Connector",
        },
        "lean_library": {
            "id": "hghakoefmnkhamdhenpbogkeopjlkpoa",
            "name": "Lean Library",
        },
        "popup_blocker": {
            "id": "bkkbcggnhapdmkeljlodobbkopceiche",
            "name": "Pop-up Blocker",
        },
        "accept_cookies": {
            "id": "ofpnikijgfhlmmjlpkfaifhhdonchhoi",
            "name": "Accept all cookies",
        },
        "2captcha_solver": {
            "id": "ifibfemgeogfhoebkmokieepdoobkbpo",
            "name": "2Captcha Solver",
        },
        "captcha_solver": {
            "id": "hlifkpholllijblknnmbfagnkjneagid",
            "name": "CAPTCHA Solver",
        },
    }

    AVAILABLE_PROFILE_NAMES = ["system", "extension", "auth", "stealth"]

    def __init__(
        self, profile_name: str, config: Optional[ScholarConfig] = None
    ):
        self.config = config or ScholarConfig()
        assert profile_name in self.AVAILABLE_PROFILE_NAMES

        self.profile_name = profile_name
        self.profile_dir = self.config.get_chrome_cache_dir(profile_name)

    def _get_extension_statuses(self, profile_dir: Path) -> Dict[str, bool]:
        """Get detailed status of each extension."""
        status = {}
        extensions_path = profile_dir / "Default" / "Extensions"

        if not extensions_path.exists():
            return {key: False for key in self.EXTENSIONS}

        for key, ext_info in self.EXTENSIONS.items():
            ext_id = ext_info["id"]
            ext_dir = extensions_path / ext_id

            if ext_dir.exists():
                version_dirs = [d for d in ext_dir.iterdir() if d.is_dir()]
                if version_dirs:
                    latest_version = max(version_dirs, key=lambda x: x.name)
                    manifest_file = latest_version / "manifest.json"
                    status[key] = manifest_file.exists()
                else:
                    status[key] = False
            else:
                status[key] = False

        return status

    def check_extensions_installed(
        self, profile_dir: Path = None, verbose: bool = True
    ) -> bool:
        """Check installation status of all extensions from profile directory."""
        if profile_dir is None:
            profile_dir = self.profile_dir

        status = self._get_extension_statuses(profile_dir)
        installed_count = sum(status.values())

        if verbose:
            for key, ext_info in self.EXTENSIONS.items():
                ext_id = ext_info["id"]
                if status.get(key, False):
                    logger.debug(
                        f"Found {ext_info['name']} ({ext_id}) installed"
                    )
                else:
                    logger.warn(f"{ext_info['name']} ({ext_id}) not installed")

            all_installed = installed_count == len(self.EXTENSIONS)
            if all_installed:
                logger.success(
                    f"All {installed_count}/{len(self.EXTENSIONS)} extensions installed"
                )
            else:
                logger.warn(
                    f"Only {installed_count}/{len(self.EXTENSIONS)} extensions installed"
                )

        return installed_count == len(self.EXTENSIONS)

    def _get_installed_extension_paths(self, profile_dir: Path) -> list[str]:
        """Get paths to installed extensions for --load-extension argument."""
        extension_paths = []
        extensions_dir = profile_dir / "Default" / "Extensions"

        if not extensions_dir.exists():
            return extension_paths

        for key, ext_info in self.EXTENSIONS.items():
            ext_id = ext_info["id"]
            ext_dir = extensions_dir / ext_id

            if ext_dir.exists():
                version_dirs = [d for d in ext_dir.iterdir() if d.is_dir()]
                if version_dirs:
                    latest_version = max(version_dirs, key=lambda x: x.name)
                    manifest_file = latest_version / "manifest.json"
                    if manifest_file.exists():
                        extension_paths.append(str(latest_version))

        return extension_paths

    def get_extension_args(self):
        """Get extension args using appropriate profile directory."""
        # profile_dir = self._get_profile_dir_with_system_handling()

        extension_paths = self._get_installed_extension_paths(self.profile_dir)

        extension_args = []
        if extension_paths:
            extensions_list = ",".join(extension_paths)
            extension_args.extend(
                [
                    f"--load-extension={extensions_list}",
                    f"--disable-extensions-except={extensions_list}",
                    "--enable-extensions",
                    "--disable-extensions-file-access-check",
                    "--disable-web-security",
                ]
            )
            logger.debug(
                f"Loading {len(extension_paths)} extensions from {self.profile_dir}"
            )

        return extension_args

    async def install_extensions_manually_if_not_installed_async(
        self, verbose=False
    ):
        """Open Chrome for manual extension installation."""
        if self.check_extensions_installed(verbose=verbose):
            return True

        # Build Chrome command
        chrome_cmd = [
            "google-chrome",
            f"--user-data-dir={self.profile_dir}",
            "--enable-extensions",
            "--new-window",
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ]
        chrome_cmd_str = " ".join(chrome_cmd)
        logger.warn(f"Chrome command: {chrome_cmd_str}")

        # Add extension URLs
        for ext_info in self.EXTENSIONS.values():
            url = f"https://chrome.google.com/webstore/detail/{ext_info['id']}"
            chrome_cmd.append(url)

        # Set environment for WSL2
        env = os.environ.copy()
        if "WSL_DISTRO_NAME" in env and "DISPLAY" not in env:
            env["DISPLAY"] = ":0.0"

        # Try to launch Chrome
        try:
            process = subprocess.Popen(
                chrome_cmd,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            logger.debug(f"Launched Chrome with PID {process.pid}")

            time.sleep(2)
            if process.poll() is not None:
                logger.error("Chrome exited immediately")
                return False

        except FileNotFoundError:
            logger.error("Chrome not found")
            return False

        print("\n" + "=" * 60)
        print("Chrome Extension Installation")
        print("=" * 60)
        print(
            "Install extensions from the opened Chrome tabs, then press Enter"
        )

        try:
            input("Press Enter when done...")
        except (EOFError, KeyboardInterrupt):
            pass

        time.sleep(2)

        if self.check_extensions_installed(verbose=False):
            logger.success("Extension installation complete!")
            return True
        else:
            logger.warn("Extension installation may be incomplete")
            return False

    async def handle_runtime_extension_dialogs_async(self, page):
        """Handle extension consent dialogs that appear at runtime."""
        try:
            await page.wait_for_timeout(2000)

            consent_selectors = [
                'button:has-text("Agree")',
                'button:has-text("Accept")',
                'button:has-text("Continue")',
                'button:has-text("OK")',
                'button:has-text("Dismiss")',
                'button:has-text("Close")',
            ]

            for selector in consent_selectors:
                element = await page.query_selector(selector)
                if element:
                    await element.click()
                    logger.success(f"Clicked dialog: {selector}")
                    return True

            return False

        except Exception as e:
            logger.error(f"Error handling dialogs: {e}")
            return False


if __name__ == "__main__":
    import asyncio

    # manager = ChromeProfileManager("extension")
    manager = ChromeProfileManager("system")

    asyncio.run(
        manager.install_extensions_manually_if_not_installed_async(
            verbose=True
        )
    )


# python -m scitex.scholar.browser.local.utils._ChromeProfileManager

# EOF
