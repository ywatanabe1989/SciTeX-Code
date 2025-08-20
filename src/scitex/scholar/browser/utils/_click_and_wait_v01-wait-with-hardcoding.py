#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-20 10:09:47 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/browser/utils/_click_and_wait.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/browser/utils/_click_and_wait.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from playwright.async_api import Locator, Page

from scitex import logging

logger = logging.getLogger(__name__)


async def click_and_wait(
    link: Locator, message: str = "Clicking link..."
) -> tuple[bool, str, Page]:
    """Click link with visual highlight and wait for all redirects to complete."""
    from ._highlight_element import highlight_element
    from ._show_popup_message_async import show_popup_message_async

    page = link.page
    context = page.context

    await show_popup_message_async(page, message)
    await highlight_element(link, 1000)

    initial_url = page.url
    href = await link.get_attribute("href") or ""
    text = await link.inner_text() or ""
    logger.info(f"Clicking: '{text[:30]}' -> {href[:50]}")

    try:
        async with context.expect_page(timeout=5000) as new_page_info:
            await link.click()
            new_page = await new_page_info.value
            page = new_page
            logger.info("New page opened, switching context")
    except:
        await link.click()

    await page.wait_for_timeout(10_000)

    try:
        await page.wait_for_load_state("networkidle", timeout=10000)
    except:
        pass

    for _ in range(5):
        old_url = page.url
        await page.wait_for_timeout(2_000)
        new_url = page.url
        if old_url == new_url:
            break

    final_url = page.url
    success = final_url != initial_url

    if success:
        await show_popup_message_async(
            page, f"Navigation complete: {final_url[:50]}..."
        )
        logger.success(f"Navigation: {initial_url} -> {final_url}")

    else:
        logger.warning("No navigation occurred")

    return dict(success=success, final_url=final_url, page=page)


# async def click_and_wait(
#     link: Locator, message: str = "Clicking link..."
# ) -> tuple[bool, str, Page]:
#     """Click link with visual highlight and wait for all redirects to complete."""
#     from ._highlight_element import highlight_element
#     from ._show_popup_message_async import show_popup_message_async

#     page = link.page
#     context = page.context

#     await show_popup_message_async(page, message)
#     await highlight_element(link, 1000)

#     initial_url = page.url
#     href = await link.get_attribute("href") or ""
#     text = await link.inner_text() or ""
#     logger.info(f"Clicking: '{text[:30]}' -> {href[:50]}")

#     async with context.expect_page() as new_page_info:
#         await link.click()
#         try:
#             new_page = await new_page_info.value
#             page = new_page
#             logger.info("New page opened, switching context")
#         except:
#             pass

#     await page.wait_for_timeout(2000)

#     for attempt in range(15):
#         try:
#             await page.wait_for_load_state("networkidle", timeout=3000)
#             break
#         except:
#             await page.wait_for_timeout(1000)

#     for _ in range(10):
#         old_url = page.url
#         await page.wait_for_timeout(1500)
#         new_url = page.url
#         if old_url == new_url:
#             break

#     final_url = page.url
#     success = final_url != initial_url

#     if success:
#         await show_popup_message_async(
#             page, f"Navigation complete: {final_url[:50]}..."
#         )
#         logger.success(f"Navigation: {initial_url} -> {final_url}")
#     else:
#         logger.warning("No navigation occurred")

#     return dict(success=success, final_url=final_url, page=page)


# async def click_and_wait(
#     link: Locator, message: str = "Clicking link..."
# ) -> bool:
#     """Click link with visual highlight and wait for all redirects to complete."""
#     from ._highlight_element import highlight_element
#     from ._show_popup_message_async import show_popup_message_async

#     try:
#         page = link.page
#         context = page.context

#         await show_popup_message_async(page, message)
#         await highlight_element(link, 1000)

#         initial_url = page.url
#         href = await link.get_attribute("href") or ""
#         text = await link.inner_text() or ""
#         logger.info(f"Clicking: '{text[:30]}' -> {href[:50]}")

#         # Listen for new pages
#         async with context.expect_page() as new_page_info:
#             await link.click()
#             try:
#                 new_page = await new_page_info.value
#                 page = new_page
#                 logger.info("New page opened, switching context")
#             except:
#                 # No new page, continue with current page
#                 pass

#         await page.wait_for_timeout(2000)

#         for attempt in range(15):
#             try:
#                 await page.wait_for_load_state("networkidle", timeout=3000)
#                 break
#             except:
#                 await page.wait_for_timeout(1000)

#         for _ in range(10):
#             old_url = page.url
#             await page.wait_for_timeout(1500)
#             new_url = page.url
#             if old_url == new_url:
#                 break

#         final_url = page.url
#         if final_url != initial_url:
#             await show_popup_message_async(
#                 page, f"Navigation complete: {final_url[:50]}..."
#             )
#             logger.success(f"Navigation: {initial_url} -> {final_url}")
#             return True
#         else:
#             logger.warning("No navigation occurred")
#             return False

#     except Exception as e:
#         logger.error(f"Click and wait failed: {e}")
#         return False


# async def click_and_wait(
#     link: Locator, message: str = "Clicking link..."
# ) -> bool:
#     """Click link with visual highlight and wait for all redirects to complete."""
#     from ._highlight_element import highlight_element
#     from ._show_popup_message_async import show_popup_message_async

#     try:
#         page = link.page
#         await show_popup_message_async(page, message)
#         await highlight_element(link, 1000)

#         initial_url = page.url
#         href = await link.get_attribute("href") or ""
#         text = await link.inner_text() or ""
#         logger.info(f"Clicking: '{text[:30]}' -> {href[:50]}")

#         await link.click()
#         await page.wait_for_timeout(2000)

#         for attempt in range(15):
#             try:
#                 await page.wait_for_load_state("networkidle", timeout=3000)
#                 break
#             except:
#                 await page.wait_for_timeout(1000)

#         for _ in range(10):
#             old_url = page.url
#             await page.wait_for_timeout(1500)
#             new_url = page.url
#             if old_url == new_url:
#                 break

#         final_url = page.url
#         if final_url != initial_url:
#             await show_popup_message_async(
#                 page, f"Navigation complete: {final_url[:50]}..."
#             )
#             logger.success(f"Navigation: {initial_url} -> {final_url}")
#             return True
#         else:
#             logger.warning("No navigation occurred")
#             return False

#     except Exception as e:
#         logger.error(f"Click and wait failed: {e}")
#         return False

# EOF
