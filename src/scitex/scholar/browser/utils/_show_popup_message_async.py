#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-19 12:06:14 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/utils/_show_popup_message_async.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/utils/_show_popup_message_async.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from scitex import log

logger = log.getLogger(__name__)


async def show_popup_message_async(
    page, message: str, duration_ms: int = 5_000
):
    """Show popup message on page."""
    try:
        if page is not None and not page.is_closed():
            await page.evaluate(
                f"""() => {{
                const popup = document.createElement('div');
                popup.innerHTML = `{message}`;
                popup.style.cssText = `
                    position: fixed;
                    top: 20px;
                    left: 50%;
                    transform: translateX(-50%);
                    background: rgba(0, 0, 0, 0.8);
                    color: white;
                    padding: 15px 25px;
                    border-radius: 8px;
                    font-size: 20px;
                    font-family: Arial, sans-serif;
                    z-index: 10000;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                `;
                document.body.appendChild(popup);
                setTimeout(() => {{
                    if (popup.parentNode) {{
                        popup.parentNode.removeChild(popup);
                    }}
                }}, {duration_ms});
            }}"""
            )
            return True
        else:
            return False
    except Exception as e:
        logger.debug(f"show_popup_message_async: {str(e)}")


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
