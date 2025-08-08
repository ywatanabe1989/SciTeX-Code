#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-07 22:09:45 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/download/run_zotero_translators.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/download/run_zotero_translators.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

#!/USSR/bin/env python3

import re

from playwright.async_api import Page

from scitex import logging

__DIR__ = os.path.dirname(
    os.path.abspath(__FILE__)
)  # Use abspath for robustness

zotero_translators_dir = os.path.join(__DIR__, "zotero_translators")

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


# --- STEP 2: ROBUST TRANSLATOR EXECUTOR ---
# async def run_zotero_translator(page: Page, translator_path: str):
#     """
#     Loads a Zotero translator and uses custom overrides to reliably extract data.
#     """
#     logger.info(f"Executing translator: {os.path.basename(translator_path)}")
#     try:
#         # Part A: Load the original translator's functions (e.g., for abstract, keywords).
#         zotero_shim = "window.Zotero={Utilities:{xpath:(d,p,n)=>{const r=[];const s=d.evaluate(p,d,n,XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,null);for(let i=0;i<s.snapshotLength;i++){r.push(s.snapshotItem(i))};return r},xpathText:(d,p,n)=>{const res=d.evaluate(p,d,n,XPathResult.STRING_TYPE,null);return res.stringValue?res.stringValue.trim():''}},debug:m=>console.log(m)};"
#         with open(translator_path, "r", encoding="utf-8") as f:
#             translator_code = f.read()
#         js_start_pos = translator_code.find("}")
#         executable_code = translator_code[js_start_pos + 1 :]
#         full_script = f"{zotero_shim}\n{executable_code}"
#         await page.evaluate(full_script)

#         # Part B: Define and execute our NEW, smarter PDF search logic.
#         pdf_override_script = """
#             () => {
#                 // Strategy 1: Find the main "Download PDF" button by its visible text.
#                 let pdfLinkNode = document.evaluate("//a[normalize-space(.)='Download PDF']", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
#                 if (pdfLinkNode && pdfLinkNode.href) return pdfLinkNode.href;

#                 // Strategy 2: Find the link by its 'data-track-action' attribute.
#                 pdfLinkNode = document.evaluate("//a[@data-track-action='download pdf']", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
#                 if (pdfLinkNode && pdfLinkNode.href) return pdfLinkNode.href;

#                 // Strategy 3 (Fallback): Construct the URL directly for known patterns.
#                 if (window.location.hostname.includes('nature.com') && window.location.pathname.includes('/articles/')) {
#                     return window.location.href.split('?')[0] + '.pdf';
#                 }
#                 return null;
#             }
#         """
#         pdf_url = await page.evaluate(pdf_override_script)
#         if pdf_url:
#             logger.success(f"✅ Extracted PDF URL: {pdf_url}")
#         else:
#             logger.warning("⚠️ All custom strategies failed to find a PDF URL.")

#         # Part C: Use the original translator for other data, like the abstract.
#         if await page.evaluate("typeof getAbstract === 'function'"):
#             abstract = await page.evaluate("getAbstract(document)")
#             if abstract:
#                 logger.success(f"✅ Extracted Abstract: {abstract[:150]}...")


#     except Exception as e:
#         error_message = str(e).splitlines()[0]
#         logger.error(
#             f"❌ Failed to execute translator: {type(e).__name__} - {error_message}"
#         )
async def run_zotero_translator(page: Page, translator_path: str) -> dict:
    """
    Loads a Zotero translator, extracts data, and returns it as a dictionary.
    """
    logger.info(f"Executing translator: {os.path.basename(translator_path)}")

    # This dictionary will store our results.
    results = {"pdf_url": None, "abstract": None}

    try:
        # Part A: Load the original translator's functions.
        zotero_shim = "window.Zotero={Utilities:{xpath:(d,p,n)=>{const r=[];const s=d.evaluate(p,d,n,XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,null);for(let i=0;i<s.snapshotLength;i++){r.push(s.snapshotItem(i))};return r},xpathText:(d,p,n)=>{const res=d.evaluate(p,d,n,XPathResult.STRING_TYPE,null);return res.stringValue?res.stringValue.trim():''}},debug:m=>console.log(m)};"
        with open(translator_path, "r", encoding="utf-8") as f:
            translator_code = f.read()
        js_start_pos = translator_code.find("}")
        executable_code = translator_code[js_start_pos + 1 :]
        full_script = f"{zotero_shim}\n{executable_code}"
        await page.evaluate(full_script)

        # Part B: Execute our smarter PDF search logic.
        pdf_override_script = """
            () => {
                let pdfLinkNode = document.evaluate("//a[normalize-space(.)='Download PDF']", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                if (pdfLinkNode && pdfLinkNode.href) return pdfLinkNode.href;

                pdfLinkNode = document.evaluate("//a[@data-track-action='download pdf']", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                if (pdfLinkNode && pdfLinkNode.href) return pdfLinkNode.href;

                if (window.location.hostname.includes('nature.com') && window.location.pathname.includes('/articles/')) {
                    return window.location.href.split('?')[0] + '.pdf';
                }
                return null;
            }
        """
        # Store the PDF URL in our results dictionary.
        results["pdf_url"] = await page.evaluate(pdf_override_script)
        if results["pdf_url"]:
            logger.success(f"✅ Extracted PDF URL: {results['pdf_url']}")
        else:
            logger.warning("⚠️ All custom strategies failed to find a PDF URL.")

        # Part C: Use the original translator for the abstract.
        if await page.evaluate("typeof getAbstract === 'function'"):
            # Store the abstract in our results dictionary.
            results["abstract"] = await page.evaluate("getAbstract(document)")
            if results["abstract"]:
                logger.success(
                    f"✅ Extracted Abstract: {results['abstract'][:150]}..."
                )

    except Exception as e:
        error_message = str(e).splitlines()[0]
        logger.error(
            f"❌ Failed to execute translator: {type(e).__name__} - {error_message}"
        )

    # Return the dictionary containing all extracted data.
    return results


# --- HELPER: Filename Sanitizer ---
def _sanitize_filename(name: str) -> str:
    """Removes invalid characters from a string to make it a valid filename."""
    # Remove extension and invalid characters
    name = os.path.splitext(name)[0]
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = name.replace(" ", "_")
    return name[:100]  # Truncate to a reasonable length


# --- HELPER: File Downloader ---
async def _download_and_save_file(page: Page, url: str, save_path: str):
    """Uses Playwright's download handling to save a file from a URL."""
    try:
        async with page.expect_download() as download_info:
            # Using a separate "downloader" page is more reliable than page.goto()
            downloader_page = await page.context.new_page()
            await downloader_page.goto(url, wait_until="domcontentloaded")
            # For some sites, a click is needed. This is a robust fallback.
            # If goto doesn't trigger download, a click on a link would.

        download = await download_info.value
        await download.save_as(save_path)
        logger.success(f"✅ Downloaded and saved to: {save_path}")
        if "downloader_page" in locals() and not downloader_page.is_closed():
            await downloader_page.close()
    except Exception as e:
        logger.error(f"❌ Failed to download {url}. Reason: {e}")


# --- MAIN ORCHESTRATOR ---
async def download_article_and_supplements(
    page: Page, translator_path: str
) -> dict | None:
    """
    Finds, downloads, and organizes the main PDF and all supplementary files for an article.
    """
    logger.info(f"--- Starting Download Process for: {page.url} ---")

    # 1. Create a dedicated directory for this article's files
    article_slug = page.url.strip("/").split("/")[-1]
    article_dir = os.path.join(DOWNLOADS_DIR, _sanitize_filename(article_slug))
    os.makedirs(article_dir, exist_ok=True)
    logger.info(f"📁 Saving files to: {article_dir}")

    downloaded_files = {"main_pdf": None, "supplementary": []}

    try:
        # 2. Extract Main PDF URL (using our robust override)
        pdf_override_script = """
            () => {
                let pdfLinkNode = document.evaluate("//a[normalize-space(.)='Download PDF']", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                if (pdfLinkNode && pdfLinkNode.href) return pdfLinkNode.href;
                pdfLinkNode = document.evaluate("//a[@data-track-action='download pdf']", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                if (pdfLinkNode && pdfLinkNode.href) return pdfLinkNode.href;
                if (window.location.hostname.includes('nature.com') && window.location.pathname.includes('/articles/')) {
                    return window.location.href.split('?')[0] + '.pdf';
                }
                return null;
            }
        """
        main_pdf_url = await page.evaluate(pdf_override_script)

        # 3. Download the Main PDF
        if main_pdf_url:
            pdf_save_path = os.path.join(article_dir, "main_article.pdf")
            await _download_and_save_file(page, main_pdf_url, pdf_save_path)
            downloaded_files["main_pdf"] = pdf_save_path
        else:
            logger.warning("⚠️ Could not find main PDF URL to download.")

        # 4. Extract Supplementary File Links
        # This script is inspired by the Zotero translator's 'attachSupplementary' logic
        supplementary_script = """
            () => {
                const suppContainerPaths = [
                    '//div[@id="supplementary-information"]',
                    '//div[./h2[starts-with(normalize-space(.), "Supplementary")]]'
                ];
                let suppContainer = null;
                for (const path of suppContainerPaths) {
                    suppContainer = document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    if (suppContainer) break;
                }

                if (!suppContainer) return [];

                const links = suppContainer.querySelectorAll('a');
                const results = [];
                links.forEach(link => {
                    if(link.href) {
                        results.push({ text: link.textContent.trim(), href: link.href });
                    }
                });
                return results;
            }
        """
        supplementary_links = await page.evaluate(supplementary_script)
        logger.info(
            f"Found {len(supplementary_links)} potential supplementary file(s)."
        )

        # 5. Download Supplementary Files
        for i, link in enumerate(supplementary_links):
            file_extension = os.path.splitext(link["href"])[1]
            if not file_extension:
                file_extension = ".html"  # Default extension

            # Sanitize the link text to create a safe filename
            safe_filename = f"supplement_{i+1}_{_sanitize_filename(link['text'])}{file_extension}"
            supp_save_path = os.path.join(article_dir, safe_filename)

            await _download_and_save_file(page, link["href"], supp_save_path)
            downloaded_files["supplementary"].append(supp_save_path)

        return downloaded_files

    except Exception as e:
        error_message = str(e).splitlines()[0]
        logger.error(
            f"❌ An error occurred during the download process: {error_message}"
        )
        return None


async def download_using_zotero_translator_async(page, url):
    try:

        # logger.info(f"--- Processing site: {site['name']} ---")
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        # First, find the correct translator for the URL
        translator_path = find_translator_for_url(url, zotero_translators_dir)

        # Then, pass the found path to the downloader/orchestrator
        if translator_path:
            download_results = await download_article_and_supplements(
                page, translator_path  # Pass the correct path here
            )
        else:
            logger.error(
                f"Could not proceed with download, no translator found for {url}."
            )
            return None  # Or handle the error as needed

        if download_results:
            logger.success("Download process completed.")
            logger.info(f"Main PDF at: {download_results.get('main_pdf')}")
            logger.info(
                f"Supplementary files: {download_results.get('supplementary')}"
            )
            return download_results

        # await browser_manager.take_screenshot_safe_async(
        #     page, site["screenshot_fname"]
        # )
    except Exception as e:
        logger.fail(f"Failed to process {url}: {e}")

# EOF
