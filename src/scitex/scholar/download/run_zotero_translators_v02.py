#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-07 22:15:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/download/run_zotero_translators.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/download/run_zotero_translators.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import re

from playwright.async_api import Page

from scitex import logging

from scitex.scholar.config import ScholarConfig

# --- CONFIGURATION ---
__DIR__ = os.path.dirname(os.path.abspath(__file__))
zotero_translators_dir = os.path.join(__DIR__, "zotero_translators")
config = ScholarConfig()
DOWNLOADS_DIR = config.get_downloads_dir()
logger = logging.getLogger(__name__)


# --- STEP 1: DYNAMIC TRANSLATOR FINDER ---
def find_translator_for_url(
    url: str, translators_dir: str = zotero_translators_dir
) -> str | None:
    """
    Finds the correct Zotero translator file for a given URL by matching the 'target' regex.
    """
    logger.info(f"Searching for translator for {url} in {translators_dir}...")
    for filename in os.listdir(translators_dir):
        if not filename.endswith(".js"):
            continue

        filepath = os.path.join(translators_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                header = "".join(f.readlines(2048))
                match = re.search(
                    r"[\"\']target[\"\']:\s*[\"\'](.+?)[\"\']", header
                )
                if not match:
                    continue

                target_regex = match.group(1).replace("\\\\", "\\")
                if re.search(target_regex, url):
                    logger.info(f"✅ Found matching translator: {filename}")
                    return filepath
        except Exception as e:
            logger.warning(f"Could not parse translator {filename}: {e}")

    logger.error(f"❌ No matching translator found for URL: {url}")
    return None


# --- HELPER: Filename Sanitizer ---
def _sanitize_filename(name: str) -> str:
    name = os.path.splitext(name)[0]
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = name.replace(" ", "_")
    return name[:100]


# --- NEW HELPER: Robust File Downloader ---
async def _download_file(page: Page, url: str, save_path: str):
    """
    Downloads a file by first trying to click its link on the page,
    then falling back to direct navigation.
    """
    try:
        # Strategy 1 (Preferred): Find the link by its href and click it.
        link_selector = f'a[href="{url}"]'
        link = page.locator(link_selector).first

        if await link.is_visible():
            logger.info(f"Attempting to download via click: {url}")
            async with page.expect_download() as download_info:
                await link.click()
            download = await download_info.value
            await download.save_as(save_path)
            logger.success(
                f"✅ Click-download successful. Saved to: {save_path}"
            )
            return

    except Exception:
        logger.warning(
            f"Click-based download failed. Falling back to direct navigation for {url}"
        )

    # Strategy 2 (Fallback): Navigate directly to the URL.
    try:
        logger.info(f"Attempting to download via navigation: {url}")
        async with page.expect_download() as download_info:
            # Use a new page for isolation
            downloader_page = await page.context.new_page()
            await downloader_page.goto(url)

        download = await download_info.value
        await download.save_as(save_path)
        logger.success(
            f"✅ Navigation-download successful. Saved to: {save_path}"
        )
        if not downloader_page.is_closed():
            await downloader_page.close()

    except Exception as e:
        logger.error(
            f"❌ Both click and navigation downloads failed for {url}. Reason: {e}"
        )


# --- MAIN ORCHESTRATOR (Modified to use the new downloader) ---
async def download_article_and_supplements(
    page: Page, translator_path: str
) -> dict | None:
    logger.info(f"--- Starting Download Process for: {page.url} ---")

    article_slug = page.url.strip("/").split("/")[-1]
    article_dir = os.path.join(DOWNLOADS_DIR, _sanitize_filename(article_slug))
    os.makedirs(article_dir, exist_ok=True)
    logger.info(f"📁 Saving files to: {article_dir}")

    downloaded_files = {"main_pdf": None, "supplementary": []}

    try:
        # 1. Extract Main PDF URL
        pdf_override_script = "()=>(document.evaluate(\"//a[normalize-space(.)='Download PDF']\",document,null,XPathResult.FIRST_ORDERED_NODE_TYPE,null).singleNodeValue||document.evaluate(\"//a[@data-track-action='download pdf']\",document,null,XPathResult.FIRST_ORDERED_NODE_TYPE,null).singleNodeValue)?.href||(window.location.hostname.includes('nature.com')?window.location.href.split('?')[0]+'.pdf':null)"
        main_pdf_url = await page.evaluate(pdf_override_script)

        if main_pdf_url:
            pdf_save_path = os.path.join(article_dir, "main_article.pdf")
            await _download_file(
                page, main_pdf_url, pdf_save_path
            )  # Use new downloader
            downloaded_files["main_pdf"] = pdf_save_path
        else:
            logger.warning("⚠️ Could not find main PDF URL to download.")

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
            await _download_file(
                page, link["href"], supp_save_path
            )  # Use new downloader
            downloaded_files["supplementary"].append(supp_save_path)

        return downloaded_files

    except Exception as e:
        logger.error(f"❌ An error occurred during the download process: {e}")
        return None


# --- MAIN ORCHESTRATOR ---
async def download_article_and_supplements(
    page: Page, translator_path: str
) -> dict | None:
    """
    Finds, downloads, and organizes the main PDF and all supplementary files for an article.
    """
    logger.info(f"--- Starting Download Process for: {page.url} ---")

    article_slug = page.url.strip("/").split("/")[-1]
    article_dir = os.path.join(DOWNLOADS_DIR, _sanitize_filename(article_slug))
    os.makedirs(article_dir, exist_ok=True)
    logger.info(f"📁 Saving files to: {article_dir}")

    downloaded_files = {"main_pdf": None, "supplementary": []}

    try:
        pdf_override_script = """
            () => {
                let n = document.evaluate("//a[normalize-space(.)='Download PDF']",document,null,XPathResult.FIRST_ORDERED_NODE_TYPE,null).singleNodeValue; if(n&&n.href)return n.href;
                n=document.evaluate("//a[@data-track-action='download pdf']",document,null,XPathResult.FIRST_ORDERED_NODE_TYPE,null).singleNodeValue; if(n&&n.href)return n.href;
                if(window.location.hostname.includes("nature.com")&&window.location.pathname.includes("/articles/"))return window.location.href.split("?")[0]+".pdf";
                return null
            }
        """
        main_pdf_url = await page.evaluate(pdf_override_script)

        if main_pdf_url:
            pdf_save_path = os.path.join(article_dir, "main_article.pdf")
            await _download_and_save_file(page, main_pdf_url, pdf_save_path)
            downloaded_files["main_pdf"] = pdf_save_path
        else:
            logger.warning("⚠️ Could not find main PDF URL to download.")

        supplementary_script = """
            () => {
                const p=['//div[@id="supplementary-information"]','//div[./h2[starts-with(normalize-space(.),"Supplementary")]]']; let c=null;
                for(const t of p){if(c=document.evaluate(t,document,null,XPathResult.FIRST_ORDERED_NODE_TYPE,null).singleNodeValue)break} if(!c)return[];
                const l=c.querySelectorAll("a"),r=[];return l.forEach(t=>{t.href&&r.push({text:t.textContent.trim(),href:t.href})}),r
            }
        """
        supplementary_links = await page.evaluate(supplementary_script)
        logger.info(
            f"Found {len(supplementary_links)} potential supplementary file(s)."
        )

        for i, link in enumerate(supplementary_links):
            ext = os.path.splitext(link["href"])[1] or ".html"
            safe_filename = (
                f"supplement_{i+1}_{_sanitize_filename(link['text'])}{ext}"
            )
            await _download_and_save_file(
                page, link["href"], os.path.join(article_dir, safe_filename)
            )
            downloaded_files["supplementary"].append(
                os.path.join(article_dir, safe_filename)
            )

        return downloaded_files

    except Exception as e:
        error_message = str(e).splitlines()[0]
        logger.error(
            f"❌ An error occurred during the download process: {error_message}"
        )
        return None


# --- PUBLIC INTERFACE FUNCTION ---
async def download_using_zotero_translator(
    page: Page, url: str
) -> dict | None:
    """
    Top-level function to find the correct translator and orchestrate the download.
    """
    try:
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        translator_path = find_translator_for_url(
            page.url, zotero_translators_dir
        )

        if translator_path:
            download_results = await download_article_and_supplements(
                page, translator_path
            )
            if download_results:
                logger.success("Download process completed successfully.")
                return download_results
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
