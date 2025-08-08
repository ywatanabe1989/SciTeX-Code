#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-07 22:41:42 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/download/run_zotero_translators.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/download/run_zotero_translators.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
import re
from urllib.parse import urljoin

import httpx
from playwright.async_api import Page

from scitex import logging

from ..config import ScholarConfig

# --- CONFIGURATION ---
__DIR__ = os.path.dirname(os.path.abspath(__file__))
zotero_translators_dir = os.path.join(__DIR__, "zotero_translators")
config = ScholarConfig()
DOWNLOADS_DIR = config.get_downloads_dir()
logger = logging.getLogger(__name__)


# --- DYNAMIC TRANSLATOR FINDER ---
def find_translator_for_url(
    url: str, translators_dir: str = zotero_translators_dir
) -> str | None:
    """Finds the correct Zotero translator file for a given URL."""
    logger.info(f"Searching for translator for {url} in {translators_dir}...")
    for filename in os.listdir(translators_dir):
        if not filename.endswith(".js"):
            continue
        filepath = os.path.join(translators_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                header = "".join(f.readlines(2048))
                match = re.search(
                    r"[\"']target[\"']:\s*[\"'](.+?)[\"']", header
                )
                if match:
                    target_regex = match.group(1).replace("\\\\", "\\")
                    if re.search(target_regex, url):
                        logger.info(
                            f"✅ Found matching translator: {filename}"
                        )
                        return filepath
        except Exception as e:
            logger.warning(f"Could not parse translator {filename}: {e}")
    logger.error(f"❌ No matching translator found for URL: {url}")
    return None


# --- HELPER: Filename Sanitizer ---
def _sanitize_filename(name: str) -> str:
    """Removes invalid characters from a string to make it a valid filename."""
    name = os.path.splitext(name)[0]
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    return name.replace(" ", "_")[:100]


# --- HELPER: Robust File Downloader ---
async def _download_file(page: Page, save_path: str, selector: str):
    """
    Downloads a file by clicking a selector and handling either a direct
    download or a new tab opening.
    """
    logger.info(f"Attempting to download via click on selector: {selector}")
    try:
        # Simultaneously wait for either a new page or a download event
        page_task = asyncio.create_task(
            page.context.expect_event("page", timeout=15000)
        )
        download_task = asyncio.create_task(
            page.expect_download(timeout=15000)
        )

        # Use force=True to click through any overlays
        await page.locator(selector).first.click(force=True, timeout=10000)

        # Wait for whichever event happens first
        done, pending = await asyncio.wait(
            [page_task, download_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        # Cancel the event that didn't happen
        for task in pending:
            task.cancel()

        if page_task in done:
            # A new page opened (in-browser PDF viewer)
            new_page = page_task.result()
            await new_page.wait_for_load_state("domcontentloaded")
            pdf_url = new_page.url
            logger.info(f"New tab opened. Intercepted PDF URL: {pdf_url}")

            # Download the content from the new page's URL
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    pdf_url, follow_redirects=True, timeout=60
                )
                response.raise_for_status()
            with open(save_path, "wb") as f:
                f.write(response.content)
            logger.success(
                f"✅ Download via interception successful. Saved to: {save_path}"
            )
            await new_page.close()

        elif download_task in done:
            # A direct download was triggered
            download = download_task.result()
            await download.save_as(save_path)
            logger.success(
                f"✅ Direct download successful. Saved to: {save_path}"
            )

    except Exception as e:
        logger.error(
            f"❌ Download failed for selector '{selector}'. Reason: {e}"
        )


# --- MAIN ORCHESTRATOR ---
async def download_article_and_supplements(
    page: Page, translator_path: str
) -> dict | None:
    """Finds, downloads, and organizes the main PDF and all supplementary files."""
    logger.info(f"--- Starting Download Process for: {page.url} ---")
    article_slug = page.url.strip("/").split("/")[-1]
    article_dir = os.path.join(DOWNLOADS_DIR, _sanitize_filename(article_slug))
    os.makedirs(article_dir, exist_ok=True)
    logger.info(f"📁 Saving files to: {article_dir}")

    downloaded_files = {"main_pdf": None, "supplementary": []}

    # 1. Download Main PDF by clicking the most robust selector
    main_pdf_selector = "//a[@data-track-action='download pdf' or normalize-space(.)='Download PDF']"
    pdf_save_path = os.path.join(article_dir, "main_article.pdf")
    await _download_file(page, pdf_save_path, selector=main_pdf_selector)
    if os.path.exists(pdf_save_path) and os.path.getsize(pdf_save_path) > 0:
        downloaded_files["main_pdf"] = pdf_save_path

    # 2. Extract and Download Supplementary Files
    supplementary_script = "()=>(Array.from((document.evaluate(\"//div[@id='supplementary-information']|//div[./h2[starts-with(normalize-space(.),'Supplementary')]]\",document,null,XPathResult.FIRST_ORDERED_NODE_TYPE,null).singleNodeValue||document).querySelectorAll('a')).map(a=>a.href&&{text:a.textContent.trim(),href:a.href}).filter(Boolean))"
    supplementary_links = await page.evaluate(supplementary_script)
    logger.info(
        f"Found {len(supplementary_links)} potential supplementary file(s)."
    )

    for i, link in enumerate(supplementary_links):
        ext = os.path.splitext(link["href"])[1] or ".html"
        safe_filename = (
            f"supplement_{i+1}_{_sanitize_filename(link['text'])}{ext}"
        )
        supp_save_path = os.path.join(article_dir, safe_filename)
        # For supplementary files, the selector is the link itself
        supp_selector = f"a[href='{link['href']}']"
        await _download_file(page, supp_save_path, selector=supp_selector)
        if (
            os.path.exists(supp_save_path)
            and os.path.getsize(supp_save_path) > 0
        ):
            downloaded_files["supplementary"].append(supp_save_path)

    return downloaded_files


# --- PUBLIC INTERFACE FUNCTION ---
async def download_using_zotero_translator(
    page: Page, url: str
) -> dict | None:
    """Top-level function to find the correct translator and orchestrate the download."""
    try:
        translator_path = find_translator_for_url(
            page.url, zotero_translators_dir
        )

        if translator_path:
            return await download_article_and_supplements(
                page, translator_path
            )
        else:
            logger.error(
                f"Could not proceed with download, no translator found for {url}."
            )
            return None

    except Exception as e:
        logger.fail(
            f"A critical error occurred in download_using_zotero_translator: {e}"
        )
        return None

# EOF
