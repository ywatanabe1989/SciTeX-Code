#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-08 04:05:49 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/browser/interaction/click_center.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/browser/interaction/click_center.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

__FILE__ = __file__

async def click_center_async(page):
    from ..debugging import show_popup_and_capture_async

    await show_popup_and_capture_async(
        page, "Clicking the center of the page..."
    )
    viewport_size = page.viewport_size
    center_x = viewport_size["width"] // 2
    center_y = viewport_size["height"] // 2
    clicked = await page.mouse.click(center_x, center_y)
    await page.wait_for_timeout(1_000)
    return clicked


# EOF
