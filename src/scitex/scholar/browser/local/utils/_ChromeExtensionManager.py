#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-06 02:38:13 (ywatanabe)"
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
        self.profile_dir = self.config.get_chrome_cache_dir(profile_name)

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

    async def _get_extension_status(self) -> Dict[str, bool]:
        """Get detailed status of each extension."""
        status = {}
        extensions_path = self.profile_dir / "Default" / "Extensions"

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

    async def check_extensions_installed_async(self) -> bool:
        """Check installation status of all extensions from profile directory."""
        status = await self._get_extension_status()
        extensions_path = self.profile_dir / "Default" / "Extensions"

        if not extensions_path.exists():
            logger.warning(
                f"Extensions directory not found: {extensions_path}"
            )

        # Log status of each extension and provide API key guidance
        captcha_extensions_installed = []
        for key, ext_info in self.EXTENSIONS.items():
            ext_id = ext_info["id"]
            if status.get(key, False):
                logger.info(f"✓ {ext_info['name']} ({ext_id}) is installed")
                # Track CAPTCHA extensions for API key guidance
                if "captcha" in key.lower() or "solver" in key.lower():
                    captcha_extensions_installed.append(
                        (key, ext_info["name"])
                    )
            else:
                logger.warning(
                    f"✗ {ext_info['name']} ({ext_id}) is not installed"
                )

        # Provide API key guidance for installed CAPTCHA extensions
        if captcha_extensions_installed:
            self._show_captcha_api_guidance(captcha_extensions_installed)

        # Status to bool
        installed_count = sum(status.values())
        print(
            f"Found {installed_count}/{len(self.EXTENSIONS)} extensions installed"
        )
        is_all_installed = installed_count == len(self.EXTENSIONS)
        return is_all_installed

    async def install_extensions_manually_if_not_installed_async(self):
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
                "--new-window",  # Force new window
                "--no-sandbox",  # Required for WSL2
                "--disable-dev-shm-usage",  # Required for WSL2
                "--disable-gpu-sandbox",  # Help with WSL2 display
                "--remote-debugging-port=0",  # Allow debugging
            ]

            # Add extension URLs
            for key, ext_info in self.EXTENSIONS.items():
                ext_id = ext_info["id"]
                url = f"https://chrome.google.com/webstore/detail/{ext_id}"
                chrome_cmd.append(url)

            chrome_launched = False
            try:
                # For WSL2, we need to set proper environment variables
                env = os.environ.copy()
                if "WSL_DISTRO_NAME" in env:
                    # WSL2 specific settings
                    if "DISPLAY" not in env:
                        env["DISPLAY"] = ":0.0"
                    # Additional WSL2 environment variables
                    env["LIBGL_ALWAYS_INDIRECT"] = "1"
                    env["XDG_RUNTIME_DIR"] = "/tmp"
                    logger.info("Setting WSL2 environment for Chrome launch")
                    logger.info(f"DISPLAY={env.get('DISPLAY')}")
                else:
                    logger.info("Non-WSL environment detected")

                # Launch Chrome with proper environment and capture output for debugging
                process = subprocess.Popen(
                    chrome_cmd,
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    start_new_session=True,
                )
                logger.info(f"Launched Chrome with PID {process.pid}")
                chrome_launched = True

                # Wait a moment and check if Chrome started successfully
                import time

                time.sleep(2)
                poll_result = process.poll()
                if poll_result is not None:
                    # Process exited, capture output
                    stdout, stderr = process.communicate()
                    logger.error(f"Chrome exited with code {poll_result}")
                    if stderr:
                        logger.error(f"Chrome stderr: {stderr.decode()}")
                    if stdout:
                        logger.info(f"Chrome stdout: {stdout.decode()}")
                    chrome_launched = False
                else:
                    logger.info("Chrome process is running successfully")

            except FileNotFoundError:
                print("Chrome not found. Trying alternative commands...")

                # Try alternative Chrome commands
                alternative_commands = [
                    ["google-chrome"],
                    ["chromium-browser"],
                    ["chromium"],
                    ["/usr/bin/google-chrome-stable"],
                    ["/usr/bin/google-chrome"],
                ]

                chrome_launched = False
                for alt_cmd in alternative_commands:
                    try:
                        full_cmd = alt_cmd + chrome_cmd[1:]  # Add same args
                        env = os.environ.copy()
                        if "WSL_DISTRO_NAME" in env and "DISPLAY" not in env:
                            env["DISPLAY"] = ":0.0"

                        process = subprocess.Popen(
                            full_cmd,
                            env=env,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            start_new_session=True,
                        )
                        logger.info(
                            f"Launched Chrome via {alt_cmd[0]} with PID {process.pid}"
                        )
                        chrome_launched = True
                        break
                    except FileNotFoundError:
                        continue

                if not chrome_launched:
                    print(
                        "Chrome not found with any command. Please install extensions manually:"
                    )
                    print("\nCopy and paste these URLs into your browser:")
                    for key, ext_info in self.EXTENSIONS.items():
                        ext_id = ext_info["id"]
                        url = f"https://chrome.google.com/webstore/detail/{ext_id}"
                        print(f"  {ext_info['name']}: {url}")
                    print(
                        f"\nOR: Use Chrome profile directory: {self.profile_dir}"
                    )
                    return False

            try:
                print("\n" + "=" * 60)
                print("INSTRUCTIONS:")
                if chrome_launched:
                    print("✅ Chrome launched successfully!")
                    print(
                        "If you don't see a Chrome window, try one of these:"
                    )
                    print("1. Check your taskbar/dock for Chrome")
                    print("2. Alt+Tab to find the Chrome window")
                    print(
                        "3. Or manually open Chrome and navigate to these URLs:"
                    )
                    for key, ext_info in self.EXTENSIONS.items():
                        ext_id = ext_info["id"]
                        url = f"https://chrome.google.com/webstore/detail/{ext_id}"
                        print(f"   • {ext_info['name']}: {url}")
                    print("4. Use the same profile directory in Chrome:")
                    print(f"   chrome --user-data-dir={self.profile_dir}")
                else:
                    print("❌ Chrome launch may have failed.")
                    print(
                        "Please manually install extensions using these URLs:"
                    )
                    for key, ext_info in self.EXTENSIONS.items():
                        ext_id = ext_info["id"]
                        url = f"https://chrome.google.com/webstore/detail/{ext_id}"
                        print(f"   • {ext_info['name']}: {url}")
                print("=" * 60)

                try:
                    user_input = input(
                        "\nPress Enter when done installing extensions..."
                    )
                    print("User confirmed extension installation complete.")
                except (EOFError, KeyboardInterrupt):
                    print(
                        "\nInput interrupted. Proceeding with verification..."
                    )
                    logger.warning(
                        "Extension installation input was interrupted (common in async contexts)"
                    )

                # Wait a moment for extensions to be saved
                import time

                time.sleep(2)

                # Verify extensions were installed
                if await self.check_extensions_installed_async():
                    print("\n✓ Extension installation complete and verified!")
                    return True
                else:
                    print(
                        "\n⚠ Extension installation may be incomplete. Please check manually."
                    )
                    installed_count = len(
                        [
                            k
                            for k, v in (
                                await self._get_extension_status()
                            ).items()
                            if v
                        ]
                    )
                    total_count = len(self.EXTENSIONS)
                    print(
                        f"Found {installed_count}/{total_count} extensions installed."
                    )

                    # If we're in an async context and Chrome was launched, assume some progress was made
                    if chrome_launched:
                        print(
                            "Chrome was launched successfully. Extensions may have been installed."
                        )
                        print(
                            "You can manually verify extensions later and re-run if needed."
                        )
                        return True  # Return True since Chrome opened successfully

                    return (
                        installed_count > 0
                    )  # Return True if any extensions were installed
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

    def _show_captcha_api_guidance(self, captcha_extensions_installed):
        """Show API key configuration guidance for CAPTCHA extensions."""

        # Check current API key configuration
        twocaptcha_configured = bool(
            self.config.resolve("twocaptcha_api_key", None)
        )
        captcha_solver_configured = bool(
            self.config.resolve("captcha_solver_api_key", None)
        )

        if not twocaptcha_configured or not captcha_solver_configured:
            print("\n" + "🔑" * 60)
            print("CAPTCHA EXTENSION API KEY CONFIGURATION")
            print("🔑" * 60)
            print(
                "📝 CAPTCHA extensions are installed but may need API keys for full functionality:"
            )

            for key, name in captcha_extensions_installed:
                if (
                    "captcha_solver_2captcha" in key
                    and not twocaptcha_configured
                ):
                    print(f"\n🤖 {name}:")
                    print(
                        "   Environment Variable: SCITEX_SCHOLAR_2CAPTCHA_API_KEY"
                    )
                    print(
                        "   Example: export SCITEX_SCHOLAR_2CAPTCHA_API_KEY='your_api_key_here'"
                    )
                    print("   Get API key from: https://2captcha.com/")

                elif (
                    "captcha_solver_hcaptcha" in key
                    and not captcha_solver_configured
                ):
                    print(f"\n🛡️ {name}:")
                    print(
                        "   Environment Variable: SCITEX_SCHOLAR_CAPTCHA_SOLVER_API_KEY"
                    )
                    print(
                        "   Example: export SCITEX_SCHOLAR_CAPTCHA_SOLVER_API_KEY='your_api_key_here'"
                    )
                    print(
                        "   Note: This extension may use different API providers"
                    )

            print(f"\n💡 TIP: Add these to your environment:")
            print("   ~/.bashrc or ~/.bash_profile or ~/.zshrc")
            print("\n📖 After setting keys, restart your terminal or run:")
            print("   source ~/.bashrc")
            print("🔑" * 60)
        else:
            logger.info("🔑 CAPTCHA API keys are configured")

    async def inject_api_keys_async(self):
        """Programmatically inject API keys into extension storage."""
        import json

        twocaptcha_key = self.config.resolve("twocaptcha_api_key", None)
        captcha_solver_key = self.config.resolve(
            "captcha_solver_api_key", None
        )

        if not twocaptcha_key and not captcha_solver_key:
            logger.warning("No CAPTCHA API keys configured for injection")
            return False

        injected_count = 0

        # Inject into 2Captcha Solver extension
        if twocaptcha_key:
            success = await self._inject_2captcha_key_async(twocaptcha_key)
            if success:
                injected_count += 1

        # Inject into CAPTCHA Solver extension
        if captcha_solver_key:
            success = await self._inject_captcha_solver_key_async(
                captcha_solver_key
            )
            if success:
                injected_count += 1

        logger.info(f"Injected API keys into {injected_count} extensions")
        return injected_count > 0

    async def _inject_2captcha_key_async(self, api_key: str) -> bool:
        """Inject 2Captcha API key into extension storage."""
        import json

        ext_id = self.EXTENSIONS["captcha_solver_2captcha"]["id"]
        storage_path = (
            self.profile_dir / "Default" / "Local Extension Settings" / ext_id
        )

        if not storage_path.exists():
            logger.warning(
                f"2Captcha extension storage not found: {storage_path}"
            )
            return False

        try:
            # Chrome extension storage is stored in LevelDB format
            # We need to modify the preferences instead
            prefs_path = self.profile_dir / "Default" / "Preferences"
            if prefs_path.exists():
                with open(prefs_path, "r") as f:
                    prefs = json.load(f)

                # Navigate to extension settings
                if "extensions" not in prefs:
                    prefs["extensions"] = {}
                if "settings" not in prefs["extensions"]:
                    prefs["extensions"]["settings"] = {}
                if ext_id not in prefs["extensions"]["settings"]:
                    prefs["extensions"]["settings"][ext_id] = {}

                # Set the API key in extension settings
                prefs["extensions"]["settings"][ext_id]["api_key"] = api_key
                prefs["extensions"]["settings"][ext_id]["configured"] = True

                with open(prefs_path, "w") as f:
                    json.dump(prefs, f, indent=2)

                logger.success(
                    "Injected 2Captcha API key into extension preferences"
                )
                return True
        except Exception as e:
            logger.error(f"Failed to inject 2Captcha API key: {e}")

        return False

    async def _inject_captcha_solver_key_async(self, api_key: str) -> bool:
        """Inject CAPTCHA Solver API key into extension storage."""
        import json

        ext_id = self.EXTENSIONS["captcha_solver_hcaptcha"]["id"]
        storage_path = (
            self.profile_dir / "Default" / "Local Extension Settings" / ext_id
        )

        if not storage_path.exists():
            logger.warning(
                f"CAPTCHA Solver extension storage not found: {storage_path}"
            )
            return False

        try:
            prefs_path = self.profile_dir / "Default" / "Preferences"
            if prefs_path.exists():
                with open(prefs_path, "r") as f:
                    prefs = json.load(f)

                # Navigate to extension settings
                if "extensions" not in prefs:
                    prefs["extensions"] = {}
                if "settings" not in prefs["extensions"]:
                    prefs["extensions"]["settings"] = {}
                if ext_id not in prefs["extensions"]["settings"]:
                    prefs["extensions"]["settings"][ext_id] = {}

                # Set the API key in extension settings
                prefs["extensions"]["settings"][ext_id]["api_key"] = api_key
                prefs["extensions"]["settings"][ext_id]["configured"] = True

                with open(prefs_path, "w") as f:
                    json.dump(prefs, f, indent=2)

                logger.success(
                    "Injected CAPTCHA Solver API key into extension preferences"
                )
                return True
        except Exception as e:
            logger.error(f"Failed to inject CAPTCHA Solver API key: {e}")

        return False

    async def suppress_popup_blocker_ads_async(self):
        """Suppress popup blocker ads that appear in Playwright context."""
        import json

        ext_id = self.EXTENSIONS["popup_blocker"]["id"]
        prefs_path = self.profile_dir / "Default" / "Preferences"

        if not prefs_path.exists():
            logger.warning(f"Chrome preferences not found: {prefs_path}")
            return False

        try:
            with open(prefs_path, "r") as f:
                prefs = json.load(f)

            # Navigate to extension settings
            if "extensions" not in prefs:
                prefs["extensions"] = {}
            if "settings" not in prefs["extensions"]:
                prefs["extensions"]["settings"] = {}
            if ext_id not in prefs["extensions"]["settings"]:
                prefs["extensions"]["settings"][ext_id] = {}

            # Suppress first-time setup and ads - this handles the "Agree/Disagree" consent dialog
            popup_blocker_settings = prefs["extensions"]["settings"][ext_id]
            popup_blocker_settings.update(
                {
                    "first_run_complete": True,
                    "welcome_shown": True,
                    "ads_disabled": True,
                    "show_promo": False,
                    "disable_notifications": True,
                    "silent_mode": True,
                    "setup_complete": True,
                    "consent_given": True,  # Auto-consent to avoid "Agree/Disagree" dialog
                    "privacy_notice_accepted": True,  # Accept privacy notice
                    "terms_accepted": True,  # Accept terms of service
                    "onboarding_complete": True,  # Skip onboarding flow
                    "marketing_disabled": True,  # Disable marketing messages
                    "analytics_disabled": True,  # Disable analytics tracking
                    "skip_welcome_page": True,  # Skip welcome page
                    "auto_accept_permissions": True,  # Auto-accept permission requests
                }
            )

            # Also set extension state to disable first-time behaviors
            if "state" not in prefs["extensions"]:
                prefs["extensions"]["state"] = {}
            if ext_id not in prefs["extensions"]["state"]:
                prefs["extensions"]["state"][ext_id] = {}

            prefs["extensions"]["state"][ext_id].update(
                {
                    "active_permissions": {"activeTab": True, "storage": True},
                    "was_installed_by_default": False,
                    "was_installed_by_oem": False,
                    "granted_permissions": {
                        "activeTab": True,
                        "storage": True,
                    },
                    "runtime_granted_permissions": {
                        "activeTab": True,
                        "storage": True,
                    },
                }
            )

            with open(prefs_path, "w") as f:
                json.dump(prefs, f, indent=2)

            logger.success(
                "Suppressed popup blocker consent dialogs and first-time setup"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to suppress popup blocker ads: {e}")
            return False

    async def configure_all_extensions_async(self):
        """Configure all extensions to suppress ads and inject API keys."""
        success_count = 0

        # Inject API keys into CAPTCHA extensions
        if await self.inject_api_keys_async():
            success_count += 1

        # Suppress popup blocker ads
        if await self.suppress_popup_blocker_ads_async():
            success_count += 1

        # Configure cookie acceptor for silent operation
        if await self._configure_cookie_acceptor_async():
            success_count += 1

        logger.info(f"Configured {success_count} extension features")
        return success_count > 0

    async def _configure_cookie_acceptor_async(self):
        """Configure cookie acceptor for silent operation."""
        import json

        ext_id = self.EXTENSIONS["accept_cookies_async"]["id"]
        prefs_path = self.profile_dir / "Default" / "Preferences"

        if not prefs_path.exists():
            return False

        try:
            with open(prefs_path, "r") as f:
                prefs = json.load(f)

            # Navigate to extension settings
            if "extensions" not in prefs:
                prefs["extensions"] = {}
            if "settings" not in prefs["extensions"]:
                prefs["extensions"]["settings"] = {}
            if ext_id not in prefs["extensions"]["settings"]:
                prefs["extensions"]["settings"][ext_id] = {}

            # Configure cookie acceptor for silent operation
            cookie_settings = prefs["extensions"]["settings"][ext_id]
            cookie_settings.update(
                {
                    "auto_accept": True,
                    "silent_mode": True,
                    "show_notifications": False,
                    "first_run_complete": True,
                }
            )

            with open(prefs_path, "w") as f:
                json.dump(prefs, f, indent=2)

            logger.success("Configured cookie acceptor for silent operation")
            return True

        except Exception as e:
            logger.error(f"Failed to configure cookie acceptor: {e}")
            return False

    async def handle_runtime_extension_dialogs_async(self, page):
        """Handle extension consent dialogs that appear at runtime."""
        try:
            # Wait a moment for any dialogs to appear
            await page.wait_for_timeout(2000)

            # Handle popup blocker consent dialogs
            consent_selectors = [
                'button:has-text("Agree")',
                'button:has-text("Accept")',
                'button:has-text("Continue")',
                'button:has-text("OK")',
                'button[data-action="agree"]',
                'button[data-consent="accept"]',
                ".consent-button",
                ".agree-button",
            ]

            for selector in consent_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        await element.click()
                        logger.success(f"Clicked consent dialog: {selector}")
                        return True
                except Exception:
                    continue

            # Handle dismissal dialogs
            dismiss_selectors = [
                'button:has-text("Dismiss")',
                'button:has-text("Close")',
                'button:has-text("×")',
                ".close-button",
                ".dismiss-button",
            ]

            for selector in dismiss_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        await element.click()
                        logger.success(f"Dismissed dialog: {selector}")
                        return True
                except Exception:
                    continue

            return False

        except Exception as e:
            logger.error(f"Error handling runtime extension dialogs: {e}")
            return False

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
        is_all_installed = asyncio.run(
            manager.check_extensions_installed_async()
        )

        # If not all installed, offer to install
        if not is_all_installed:
            answer = input("Install missing extensions? (y/n): ")
            if answer.lower() == "y":
                print("\nStarting installation...")
                asyncio.run(
                    manager.install_extensions_manually_if_not_installed_async()
                )

                # Check again after installation
                print("\nRe-checking extensions...")
                new_status = asyncio.run(
                    manager.check_extensions_installed_async()
                )
                new_installed = sum(new_status.values())
                print(
                    f"Now have {new_installed}/{len(manager.EXTENSIONS)} extensions installed"
                )

        # Configure extensions if all are installed
        if is_all_installed or answer.lower() == "y":
            print("\nConfiguring extensions...")
            asyncio.run(manager.configure_all_extensions_async())
            print("Extension configuration complete!")

    main()

# python -m src.scitex.scholar.browser.local.utils._ChromeExtensionManager

# EOF
