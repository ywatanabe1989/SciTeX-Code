#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-09 11:49:04 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/browser/debugging/_show_popup_and_capture.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/browser/debugging/_show_popup_and_capture.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from datetime import datetime
from pathlib import Path

from scitex import logging

logger = logging.getLogger(__name__)


async def show_popup_and_capture_async(
    page,
    message: str,
    duration_ms: int = 60_000,
    take_screenshot: bool = True,
    screenshot_category: str = "default",
    screenshot_dir: Path | str = None,
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

    Args:
        page: Playwright page object
        message: Message text to display in popup
        duration_ms: How long message stays visible (default 60 seconds)
        take_screenshot: Whether to capture screenshot (default True)
        screenshot_category: Category for organizing screenshots (default "default")
        screenshot_dir: Custom screenshot directory (default None = ~/.scitex/browser/screenshots)

    Returns:
        bool: True if successful, False otherwise

    Example:
    >>> from scitex.browser.debugging import show_popup_and_capture_async
    >>> await show_popup_and_capture_async(
    ...     page,
    ...     "OpenURL: ✓ Found publisher link",
    ...     take_screenshot=True,
    ...     screenshot_category="authentication"
    ... )

    Note:
        This function is designed to be non-blocking and fail-safe.
        Screenshot failures do not break the popup system. Messages persist
        across page navigations using a framenavigated event handler.
    """
    logger.info(f"show_popup_and_capture_async: {message}")
    try:
        if page is None or page.is_closed():
            return False

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
    }}

    const message = {{
        text: `{message}`,
        timestamp: Date.now(),
        expiresAt: Date.now() + {duration_ms}
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
                background: rgba(0, 0, 0, 0.9);
                color: white;
                padding: 12px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-family: 'Courier New', monospace;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
                border-left: 3px solid #4CAF50;
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
                        background: rgba(0, 0, 0, 0.9);
                        color: white;
                        padding: 12px 20px;
                        border-radius: 6px;
                        font-size: 14px;
                        font-family: 'Courier New', monospace;
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
                        border-left: 3px solid #4CAF50;
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
                    background: rgba(0, 0, 0, 0.9);
                    color: white;
                    padding: 12px 20px;
                    border-radius: 6px;
                    font-size: 14px;
                    font-family: 'Courier New', monospace;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
                    border-left: 3px solid #4CAF50;
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

        if take_screenshot:
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
                    screenshot_base = (
                        Path.home() / ".scitex" / "browser" / "screenshots"
                    )
                else:
                    screenshot_base = Path(screenshot_dir).expanduser()

                screenshot_path = screenshot_base / screenshot_category
                screenshot_path.mkdir(parents=True, exist_ok=True)

                clean_message = "".join(
                    c if c.isalnum() or c in (" ", "-", "_") else "_"
                    for c in message
                )[:100]

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                screenshot_filename = f"{timestamp}_{clean_message}.png"
                screenshot_full_path = screenshot_path / screenshot_filename

                await page.screenshot(
                    path=str(screenshot_full_path),
                    full_page=False,
                )
                logger.debug(f"Screenshot saved: {screenshot_full_path}")
            except Exception as e:
                logger.debug(f"Screenshot failed (non-fatal): {e}")

        return True
    except Exception as e:
        logger.debug(f"show_popup_and_capture: {str(e)}")
        return False

# EOF
