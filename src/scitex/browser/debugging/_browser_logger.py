#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-11 01:18:11 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/browser/debugging/_browser_logger.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/browser/debugging/_browser_logger.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
  - Shows stacking popup messages in browser with automatic screenshot capture
  - Provides real-time visual feedback for browser automation debugging
  - Creates timestamped screenshot timeline organized by category
  - Demonstrates popup and capture when run standalone

Dependencies:
  - packages:
    - playwright

IO:
  - input-files:
    - None
  - output-files:
    - ~/.scitex/browser/screenshots/{category}/{timestamp}_{message}.png
"""

"""Imports"""
import argparse
from datetime import datetime
from pathlib import Path

from scitex import logging

logger = logging.getLogger(__name__)

"""Functions & Classes"""
# Color mapping for log levels (for browser popups)
_POPUP_COLORS = {
    "debug": "#6C757D",  # Grey
    "info": "#17A2B8",  # Cyan/Teal
    "success": "#28A745",  # Green
    "warning": "#FFC107",  # Yellow
    "error": "#DC3545",  # Red
    "fail": "#DC3545",  # Red
}


async def log_page_async(
    page,
    message: str,
    duration_ms: int = 60_000,
    take_screenshot: bool = True,
    screenshot_dir: Path | str = None,
    verbose: bool = True,
    level: str = "info",
    func_name="BrowserLogger",
):
    """Show stacking popup messages in browser with automatic screenshot capture.

    This is a special, versatile, reusable function for visual browser debugging
    across the entire SciTeX ecosystem. It provides real-time visual feedback
    and creates a timestamped screenshot timeline of browser automation workflows.

    Features:
    - Stacking popup messages that persist across page navigations
    - Each message stays visible for 60 seconds by default
    - Messages re-injected automatically on page navigation (framenavigated handler)
    - Older messages automatically removed when stack exceeds 10 items
    - Automatic screenshot capture with millisecond-precision timestamps
    - Visual flash effect when screenshot is taken
    - Screenshots organized by category for easy review
    - Non-blocking and fail-safe design
    - Controlled by verbose flag for production environments
    - Colored popups matching scitex.logging levels

    Args:
        page: Playwright page object
        message: Message text to display in popup
        duration_ms: How long message stays visible (default 60 seconds)
        take_screenshot: Whether to capture screenshot (default True)
        screenshot_dir: Custom screenshot directory (default None = ~/.scitex/browser/screenshots)
        verbose: Enable/disable visual popups and screenshots (default True)
        level: Log level - one of: debug, info, success, warning, error, fail (default "info")

    Returns:
        bool: True if successful, False otherwise

    Example:
    >>> from scitex.browser.debugging import browser_logger_success
    >>> # Development mode - show popups
    >>> await browser_logger_success(
    ...     page,
    ...     "OpenURL: ✓ Found publisher link",
    ...     take_screenshot=True,
    ...     verbose=True
    ... )
    >>>
    >>> # Production mode - silent logging only
    >>> await browser_logger_info(
    ...     page,
    ...     "Processing authentication",
    ...     verbose=False
    ... )

    Note:
        This function is designed to be non-blocking and fail-safe.
        Screenshot failures do not break the popup system. Messages persist
        across page navigations using a framenavigated event handler.

        When verbose=False, only logger messages are generated without
        any visual feedback or screenshots, making it suitable for production.
    """
    # Log to terminal
    log_func = getattr(logger, level, logger.info)
    log_func(f"    {func_name} - {message}")

    # Check if this log level would actually be shown
    level_numeric = {
        "debug": 10,
        "info": 20,
        "success": 25,
        "warning": 30,
        "warn": 30,
        "error": 40,
        "fail": 40,
    }
    current_level_value = level_numeric.get(level, 20)
    effective_level = logger.getEffectiveLevel()
    should_take_screenshot = take_screenshot and (
        current_level_value >= effective_level
    )

    # If verbose is False, skip all visual feedback and screenshots
    if not verbose:
        return True

    # Check if we should show popup based on logging level
    # Only show popup if message level >= effective logging level
    should_show_popup = current_level_value >= effective_level

    # Get border color for popup based on level
    border_color = _POPUP_COLORS.get(level, _POPUP_COLORS["info"])
    try:
        if page is None or page.is_closed():
            return False

        # Only show popup if level is high enough
        if should_show_popup:
            await page.evaluate(
            f"""
() => {{
    if (!window._scitexMessages) {{
        window._scitexMessages = [];
        window._scitexPopupContainer = null;
    }}

    if (!window._scitexPopupContainer || !document.body.contains(window._scitexPopupContainer)) {{
        const container = document.createElement('div');
        container.id = '_scitex_popup_container';
        container.style.cssText = `
            position: fixed;
            top: 10px;
            left: 10px;
            z-index: 2147483646;
            display: flex;
            flex-direction: column;
            gap: 8px;
            max-width: 600px;
            pointer-events: none;
        `;
        document.body.appendChild(container);
        window._scitexPopupContainer = container;
    }}

    const message = {{
        text: `{message}`,
        timestamp: Date.now(),
        expiresAt: Date.now() + {duration_ms},
        borderColor: `{border_color}`
    }};
    window._scitexMessages.push(message);

    if (window._scitexMessages.length > 10) {{
        window._scitexMessages.shift();
    }}

    window._scitexPopupContainer.innerHTML = '';
    window._scitexMessages.forEach((msg, index) => {{
        if (Date.now() < msg.expiresAt) {{
            const popup = document.createElement('div');
            popup.innerHTML = msg.text;
            popup.style.cssText = `
                background: rgba(0, 0, 0, 0.75);
                color: white;
                padding: 12px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-family: 'Courier New', monospace;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
                border-left: 5px solid ${{msg.borderColor}};
                opacity: ${{1 - (index * 0.05)}};
                pointer-events: none;
                word-wrap: break-word;
            `;
            window._scitexPopupContainer.appendChild(popup);
        }}
    }});

    setTimeout(() => {{
        if (window._scitexMessages) {{
            window._scitexMessages = window._scitexMessages.filter(msg => Date.now() < msg.expiresAt);
            if (window._scitexPopupContainer) {{
                window._scitexPopupContainer.innerHTML = '';
                window._scitexMessages.forEach((msg, index) => {{
                    const popup = document.createElement('div');
                    popup.innerHTML = msg.text;
                    popup.style.cssText = `
                        background: rgba(0, 0, 0, 0.75);
                        color: white;
                        padding: 12px 20px;
                        border-radius: 6px;
                        font-size: 14px;
                        font-family: 'Courier New', monospace;
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
                        border-left: 5px solid ${{msg.borderColor}};
                        opacity: ${{1 - (index * 0.05)}};
                        pointer-events: none;
                        word-wrap: break-word;
                    `;
                    window._scitexPopupContainer.appendChild(popup);
                }});
            }}
        }}
    }}, {duration_ms});
}}
"""
            )

            if not hasattr(page, "_scitex_popup_handler_added"):

                async def restore_popups_on_load(frame):
                    """Re-inject popup container and messages after page navigation"""
                    if frame == page.main_frame:
                        try:
                            await page.wait_for_load_state(
                                "domcontentloaded", timeout=5000
                            )
                            await page.evaluate(
                            """
() => {
    if (window._scitexMessages && window._scitexMessages.length > 0) {
        if (!document.getElementById('_scitex_popup_container')) {
            const container = document.createElement('div');
            container.id = '_scitex_popup_container';
            container.style.cssText = `
                position: fixed;
                top: 10px;
                right: 10px;
                z-index: 2147483647;
                display: flex;
                flex-direction: column;
                gap: 8px;
                max-width: 600px;
                pointer-events: none;
            `;
            document.body.appendChild(container);
            window._scitexPopupContainer = container;

            window._scitexMessages = window._scitexMessages.filter(msg => Date.now() < msg.expiresAt);
            window._scitexMessages.forEach((msg, index) => {
                const popup = document.createElement('div');
                popup.innerHTML = msg.text;
                popup.style.cssText = `
                    background: rgba(0, 0, 0, 0.75);
                    color: white;
                    padding: 12px 20px;
                    border-radius: 6px;
                    font-size: 14px;
                    font-family: 'Courier New', monospace;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
                    border-left: 5px solid ${msg.borderColor || '#4CAF50'};
                    opacity: ${1 - (index * 0.05)};
                    pointer-events: none;
                    word-wrap: break-word;
                `;
                container.appendChild(popup);
            });
        }
    }
}
"""
                            )
                        except Exception:
                            pass

                page.on("framenavigated", restore_popups_on_load)
                page._scitex_popup_handler_added = True

        if should_take_screenshot:
            try:
                await page.evaluate(
                    """
() => {
    const overlay = document.createElement('div');
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: white;
        z-index: 2147483646;
        pointer-events: none;
        animation: flash 200ms ease-out;
    `;

    const style = document.createElement('style');
    style.textContent = `
        @keyframes flash {
            0% { opacity: 0; }
            50% { opacity: 0.5; }
            100% { opacity: 0; }
        }
    `;
    document.head.appendChild(style);
    document.body.appendChild(overlay);

    setTimeout(() => {
        overlay.remove();
        style.remove();
    }, 200);
}
"""
                )

                await page.wait_for_timeout(100)

                if screenshot_dir is None:
                    screenshot_path = (
                        Path.home() / ".scitex" / "browser" / "screenshots"
                    )
                else:
                    screenshot_path = Path(screenshot_dir).expanduser()

                screenshot_path.mkdir(parents=True, exist_ok=True)

                # Remove emojis and special characters, keep only alphanumeric, spaces, hyphens, underscores, dots
                clean_message = "".join(
                    (
                        c
                        if c.isascii()
                        and (c.isalnum() or c in (" ", "-", "_", "."))
                        else "_"
                    )
                    for c in message
                )
                # Replace multiple spaces with single space, then replace spaces with underscores
                import re

                clean_message = re.sub(r"\s+", " ", clean_message)
                clean_message = clean_message.replace(" ", "_")
                clean_message = clean_message.strip("_")[:100]

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                level_upper = level.upper()
                screenshot_filename = (
                    f"{timestamp}-{level_upper}-{clean_message}.png"
                )
                screenshot_full_path = screenshot_path / screenshot_filename

                await page.screenshot(
                    path=str(screenshot_full_path),
                    full_page=False,
                )
                log_func(
                    f"    {func_name} - Screenshot: {screenshot_full_path}",
                    c="grey",
                )
            except Exception as e:
                log_func(
                    f"    {func_name} - Screenshot failed: {screenshot_filename}\n{e}"
                )

        return True
    except Exception as e:
        logger.debug(f"{str(e)}")
        return False


# BrowserLogger class - logger-like interface for browser logging
class BrowserLogger:
    """Logger-like interface for browser page logging with colored popups.

    This class provides a familiar logging interface similar to scitex.logging,
    but for browser page debugging with visual popups and screenshots.

    Example:
    >>> from scitex.browser.debugging import BrowserLogger
    >>> browser_logger = BrowserLogger(page)
    >>> await browser_logger.info("Processing page")
    >>> await browser_logger.success("Authentication completed")
    >>> await browser_logger.warning("Popup detected")
    >>> await browser_logger.error("Failed to find element")
    """

    def __init__(
        self,
        page=None,
        duration_ms: int = 60_000,
        take_screenshot: bool = True,
        screenshot_dir: Path | str = None,
        verbose: bool = True,
    ):
        """Initialize BrowserLogger with page and default settings.

        Args:
            page: Playwright page object
            duration_ms: Default duration for popups (default 60 seconds)
            take_screenshot: Whether to take screenshots by default
            screenshot_dir: Default screenshot directory
            verbose: Enable/disable visual popups and screenshots
        """
        self.page = page
        self.duration_ms = duration_ms
        self.take_screenshot = take_screenshot
        self.screenshot_dir = screenshot_dir
        self.verbose = verbose

    async def _log(
        self,
        page,
        level: str,
        message: str,
        duration_ms: int = None,
        take_screenshot: bool = None,
        screenshot_dir: Path | str = None,
        func_name: str = "BrowserLogger",
    ):
        """Internal log method."""
        return await log_page_async(
            page,
            message,
            duration_ms=duration_ms or self.duration_ms,
            take_screenshot=(
                take_screenshot
                if take_screenshot is not None
                else self.take_screenshot
            ),
            screenshot_dir=screenshot_dir or self.screenshot_dir,
            verbose=self.verbose,
            level=level,
            func_name=func_name,
        )

    async def debug(
        self,
        page,
        message: str,
        duration_ms: int = None,
        take_screenshot: bool = None,
        screenshot_dir: Path | str = None,
        func_name: str = "BrowserLogger",
    ):
        """Log debug message (grey border)."""
        return await self._log(
            page,
            "debug",
            message,
            duration_ms,
            take_screenshot,
            screenshot_dir,
            func_name,
        )

    async def info(
        self,
        page,
        message: str,
        duration_ms: int = None,
        take_screenshot: bool = None,
        screenshot_dir: Path | str = None,
        func_name: str = "BrowserLogger",
    ):
        """Log info message (cyan/teal border)."""
        return await self._log(
            page,
            "info",
            message,
            duration_ms,
            take_screenshot,
            screenshot_dir,
            func_name,
        )

    async def success(
        self,
        page,
        message: str,
        duration_ms: int = None,
        take_screenshot: bool = None,
        screenshot_dir: Path | str = None,
        func_name: str = "BrowserLogger",
    ):
        """Log success message (green border)."""
        return await self._log(
            page,
            "success",
            message,
            duration_ms,
            take_screenshot,
            screenshot_dir,
            func_name,
        )

    async def warning(
        self,
        page,
        message: str,
        duration_ms: int = None,
        take_screenshot: bool = None,
        screenshot_dir: Path | str = None,
        func_name: str = "BrowserLogger",
    ):
        """Log warning message (yellow border)."""
        return await self._log(
            page,
            "warning",
            message,
            duration_ms,
            take_screenshot,
            screenshot_dir,
            func_name,
        )

    async def warn(
        self,
        page,
        message: str,
        duration_ms: int = None,
        take_screenshot: bool = None,
        screenshot_dir: Path | str = None,
        func_name: str = "BrowserLogger",
    ):
        """Log warning message (yellow border)."""
        return await self.warning(
            page,
            message,
            duration_ms,
            take_screenshot,
            screenshot_dir,
            func_name,
        )

    async def error(
        self,
        page,
        message: str,
        duration_ms: int = None,
        take_screenshot: bool = None,
        screenshot_dir: Path | str = None,
        func_name: str = "BrowserLogger",
    ):
        """Log error message (red border)."""
        return await self._log(
            page,
            "error",
            message,
            duration_ms,
            take_screenshot,
            screenshot_dir,
            func_name,
        )

    async def fail(
        self,
        page,
        message: str,
        duration_ms: int = None,
        take_screenshot: bool = None,
        screenshot_dir: Path | str = None,
        func_name: str = "BrowserLogger",
    ):
        """Log fail message (red border)."""
        return await self._log(
            page,
            "fail",
            message,
            duration_ms,
            take_screenshot,
            screenshot_dir,
            func_name,
        )


browser_logger = BrowserLogger()


def main(args):
    logger.info(
        "Popup and capture utility - use browser_logger.info() in your code"
    )
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    import scitex as stx

    parser = argparse.ArgumentParser(
        description="Popup and screenshot capture utility for debugging"
    )
    args = parser.parse_args()
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt, rng

    import sys

    import matplotlib.pyplot as plt

    import scitex as stx

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC, rng = stx.session.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        sdir_suffix=None,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# EOF
