#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-23 18:02:42 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/utils/_show_popup_message_async.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from scitex import logging

logger = logging.getLogger(__name__)


async def show_popup_message_async(
    page,
    message: str,
    duration_ms: int = 60_000,
    take_screenshot_flag: bool = True,
    screenshot_category: str = "visual_tracking"
):
    """
    Show stacking popup messages that persist across page navigations,
    with automatic screenshot capture for visual timeline.

    Features:
    - Messages stack vertically from top to bottom
    - Each message stays for 60 seconds by default
    - Messages persist across page navigations (re-injected on load)
    - Older messages automatically removed when stack exceeds 10 items
    - Automatic screenshot capture at each message (optional)

    Args:
        page: Playwright page object
        message: Message text to display
        duration_ms: How long message stays visible (default 60 seconds)
        take_screenshot_flag: Whether to capture screenshot (default True)
        screenshot_category: Category for organizing screenshots (default "visual_tracking")
    """
    try:
        if page is None or page.is_closed():
            return False

        # Inject the stacking popup system
        await page.evaluate(
            f"""
            () => {{
                // Initialize message stack in window if not exists
                if (!window._scitexMessages) {{
                    window._scitexMessages = [];
                    window._scitexPopupContainer = null;
                }}

                // Create container if not exists
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

                // Add new message
                const message = {{
                    text: `{message}`,
                    timestamp: Date.now(),
                    expiresAt: Date.now() + {duration_ms}
                }};

                window._scitexMessages.push(message);

                // Keep only last 10 messages
                if (window._scitexMessages.length > 10) {{
                    window._scitexMessages.shift();
                }}

                // Render all active messages
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

                // Clean up expired messages periodically
                setTimeout(() => {{
                    if (window._scitexMessages) {{
                        window._scitexMessages = window._scitexMessages.filter(
                            msg => Date.now() < msg.expiresAt
                        );
                        // Re-render
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

        # Set up page load handler to re-inject popups after navigation
        # This is called BEFORE each page loads, ensuring popups persist
        if not hasattr(page, '_scitex_popup_handler_added'):
            async def restore_popups_on_load(frame):
                """Re-inject popup container and messages after page navigation"""
                if frame == page.main_frame:
                    try:
                        # Wait a bit for body to be ready
                        await page.wait_for_load_state('domcontentloaded', timeout=5000)
                        await page.evaluate("""
                            () => {
                                // Re-create container if messages exist
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

                                        // Re-render all non-expired messages
                                        window._scitexMessages = window._scitexMessages.filter(
                                            msg => Date.now() < msg.expiresAt
                                        );

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
                        """)
                    except Exception:
                        pass  # Ignore errors during re-injection

            page.on('framenavigated', restore_popups_on_load)
            page._scitex_popup_handler_added = True

        # Take screenshot for visual timeline (if enabled)
        if take_screenshot_flag:
            try:
                from ._take_screenshot import take_screenshot
                from datetime import datetime

                # Clean message for filename (remove special chars)
                clean_message = "".join(
                    c if c.isalnum() or c in (' ', '-', '_') else '_'
                    for c in message
                )[:100]  # Limit length

                # Add timestamp prefix for chronological ordering
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # millisecond precision
                screenshot_message = f"{timestamp}_{clean_message}"

                await take_screenshot(
                    page,
                    category=screenshot_category,
                    message=screenshot_message,
                    full_page=False,  # Faster, captures visible area with popup
                )
            except Exception as e:
                # Screenshot failure should not break the popup system
                logger.debug(f"Screenshot failed (non-fatal): {e}")

        return True

    except Exception as e:
        logger.debug(f"show_popup_message_async: {str(e)}")
        return False


# async def show_popup_message_async(
#     page, message: str, duration_ms: int = 5_000
# ):
#     """Show popup message on page."""
#     try:
#         if page is not None and not page.is_closed():
#             await page.evaluate(
#                 f"""
#                 () => {{
#                     const popup = document.createElement('div');
#                     popup.innerHTML = `{message}`;
#                     popup.style.cssText = `
#                         position: fixed;
#                         top: 20px;
#                         left: 50%;
#                         transform: translateX(-50%);
#                         background: rgba(0, 0, 0, 0.8);
#                         color: white;
#                         padding: 15px 25px;
#                         border-radius: 8px;
#                         font-size: 16px;
#                         font-family: Arial, sans-serif;
#                         z-index: 10000;
#                         box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
#                     `;
#                     document.body.appendChild(popup);

#                     setTimeout(() => {{
#                         if (popup.parentNode) {{
#                             popup.parentNode.removeChild(popup);
#                         }}
#                     }}, {duration_ms});
#                 }}
#             """
#             )
#             return True
#         else:
#             return False
#     except Exception as e:
#         logger.fail(f"show_popup_message_async: {str(e)}")

# EOF
