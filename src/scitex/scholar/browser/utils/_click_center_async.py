#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-20 06:49:04 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/utils/_click_center_async.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/utils/_click_center_async.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

async def click_center_async(page):
    from . import show_popup_message_async

    await show_popup_message_async(page, "Clicking the center of the page...")
    viewport_size = page.viewport_size
    center_x = viewport_size["width"] // 2
    center_y = viewport_size["height"] // 2
    clicked = await page.mouse.click(center_x, center_y)
    await page.wait_for_timeout(1_000)
    return clicked

# EOF
