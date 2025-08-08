#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-07 22:43:59 (ywatanabe)"
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


async def _download_file(page: Page, save_path: str, url: str, selector: str):
    """Downloads a file by clicking a selector and handling either a direct download or a new tab opening."""
    logger.info(f"Attempting to download '{os.path.basename(save_path)}'...")

    try:
        page_task = asyncio.create_task(
            page.context.expect_event("page", timeout=20000)
        )
        download_task = asyncio.create_task(
            page.expect_download(timeout=20000)
        )

        await page.locator(selector).first.click(force=True, timeout=15000)

        done, pending = await asyncio.wait(
            [page_task, download_task], return_when=asyncio.FIRST_COMPLETED
        )

        for task in pending:
            task.cancel()

        if page_task in done:
            new_page = page_task.result()
            await new_page.wait_for_load_state("domcontentloaded")
            intercepted_url = new_page.url
            logger.info(f"New tab opened. Intercepted URL: {intercepted_url}")

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    intercepted_url, follow_redirects=True, timeout=60
                )
                response.raise_for_status()

                # Check if content is actually HTML instead of expected file type
                content_type = response.headers.get("content-type", "").lower()
                if "text/html" in content_type and save_path.endswith(".pdf"):
                    logger.error(
                        f"❌ Expected PDF but received HTML content. Skipping save."
                    )
                    await new_page.close()
                    return

                with open(save_path, "wb") as f:
                    f.write(response.content)

            logger.success(
                f"✅ Download via interception successful. Saved to: {save_path}"
            )
            await new_page.close()

        elif download_task in done:
            download = download_task.result()
            await download.save_as(save_path)
            logger.success(
                f"✅ Direct download successful. Saved to: {save_path}"
            )

    except Exception as e:
        logger.warning(
            f"Click-based download failed. Reason: {type(e).__name__}. Falling back to direct URL download."
        )

        try:
            logger.info(f"Attempting direct download from URL: {url}")
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url, follow_redirects=True, timeout=60
                )
                response.raise_for_status()

                # Check content type for direct downloads too
                content_type = response.headers.get("content-type", "").lower()
                if "text/html" in content_type and save_path.endswith(".pdf"):
                    logger.error(
                        f"❌ Expected PDF but received HTML content from {url}. Skipping save."
                    )
                    return

                with open(save_path, "wb") as f:
                    f.write(response.content)

            logger.success(
                f"✅ Direct download successful. Saved to: {save_path}"
            )

        except Exception as direct_e:
            logger.error(
                f"❌ All download methods failed for '{os.path.basename(save_path)}'. Final error: {direct_e}"
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

    main_pdf_selector = "//a[@data-track-action='download pdf' or normalize-space(.)='Download PDF']"
    try:
        main_pdf_relative_url = await page.locator(
            main_pdf_selector
        ).first.get_attribute("href", timeout=5000)
        if main_pdf_relative_url:
            main_pdf_url = urljoin(page.url, main_pdf_relative_url)
            logger.success(f"Found Main PDF URL: {main_pdf_url}")
            pdf_save_path = os.path.join(article_dir, "main_article.pdf")

            await _download_file(
                page, pdf_save_path, main_pdf_url, main_pdf_selector
            )

            if (
                os.path.exists(pdf_save_path)
                and os.path.getsize(pdf_save_path) > 0
            ):
                downloaded_files["main_pdf"] = pdf_save_path
        else:
            logger.warning("⚠️ Could not find main PDF URL.")
    except Exception as e:
        logger.warning(f"⚠️ Could not extract main PDF URL. Reason: {e}")

    supplementary_script = "()=>(Array.from((document.evaluate(\"//div[@id='supplementary-information']|//div[./h2[starts-with(normalize-space(.),'Supplementary')]]\",document,null,XPathResult.FIRST_ORDERED_NODE_TYPE,null).singleNodeValue||document).querySelectorAll('a')).map(a=>a.href&&{text:a.textContent.trim(),href:a.href}).filter(Boolean))"
    supplementary_links = await page.evaluate(supplementary_script)
    logger.info(
        f"Found {len(supplementary_links)} potential supplementary file(s)."
    )

    for ii, link in enumerate(supplementary_links):
        supp_url = urljoin(page.url, link["href"])
        logger.success(
            f"Found Supplementary File #{ii+1} ({link['text']}): {supp_url}"
        )
        ext = os.path.splitext(link["href"])[1] or ".html"
        safe_filename = (
            f"supplement_{ii+1}_{_sanitize_filename(link['text'])}{ext}"
        )
        supp_save_path = os.path.join(article_dir, safe_filename)
        supp_selector = f"a[href='{link['href']}']"

        await _download_file(page, supp_save_path, supp_url, supp_selector)

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
