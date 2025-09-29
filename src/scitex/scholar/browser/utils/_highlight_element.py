#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-20 08:51:47 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/utils/_highlight_element.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/utils/_highlight_element.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from playwright.async_api import Locator


async def highlight_element(element: Locator, duration_ms: int = 1_000):
    """Highlight element with red overlay rectangle."""
    await element.evaluate(
        """(element, duration) => {
            // Get element position and size
            const rect = element.getBoundingClientRect();

            // Create overlay div
            const overlay = document.createElement('div');
            overlay.id = 'highlight-overlay-' + Date.now();
            overlay.style.cssText = `
                position: fixed;
                top: ${rect.top}px;
                left: ${rect.left}px;
                width: ${rect.width}px;
                height: ${rect.height}px;
                border: 5px solid red;
                background-color: rgba(255, 0, 0, 0.2);
                pointer-events: none;
                z-index: 999999;
                box-shadow: 0 0 20px red;
            `;

            document.body.appendChild(overlay);

            // Scroll element into view
            element.scrollIntoView({behavior: 'smooth', block: 'center'});

            // Remove overlay after duration
            setTimeout(() => {
                if (overlay && overlay.parentNode) {
                    overlay.parentNode.removeChild(overlay);
                }
            }, duration);
        }""",
        duration_ms,
    )
    await element.page.wait_for_timeout(duration_ms)


# async def highlight_element(element: Locator, duration_ms: int = 5000):
#     """Highlight element with red overlay rectangle."""
#     await element.evaluate(
#         """
#     element => {
#         // Get element position and size
#         const rect = element.getBoundingClientRect();

#         // Create overlay div
#         const overlay = document.createElement('div');
#         overlay.id = 'highlight-overlay-' + Date.now();
#         overlay.style.cssText = `
#             position: fixed;
#             top: ${rect.top}px;
#             left: ${rect.left}px;
#             width: ${rect.width}px;
#             height: ${rect.height}px;
#             border: 5px solid red;
#             background-color: rgba(255, 0, 0, 0.2);
#             pointer-events: none;
#             z-index: 999999;
#             box-shadow: 0 0 20px red;
#         `;

#         document.body.appendChild(overlay);

#         // Scroll element into view
#         element.scrollIntoView({behavior: 'smooth', block: 'center'});

#         // Remove overlay after duration
#         setTimeout(() => {
#             if (overlay && overlay.parentNode) {
#                 overlay.parentNode.removeChild(overlay);
#             }
#         }, arguments[1]);
#     }
#     """,
#         duration_ms,
#     )

#     await element.page.wait_for_timeout(duration_ms)

# EOF
