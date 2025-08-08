#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-07 22:57:14 (ywatanabe)"
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
import json
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

# --- ZOTERO JAVASCRIPT SHIM ---
# This JavaScript code emulates the environment Zotero provides for its translators.
ZOTERO_SHIM_JS = """
    window.Zotero = {
        Item: function(itemType) {
            this.itemType = itemType;
            this.creators = [];
            this.tags = [];
            this.notes = [];
            this.attachments = [];
            this.seeAlso = [];
        },
        debug: (msg) => console.log('Zotero.debug:', msg),
        log: (msg) => console.log('Zotero.log:', msg),
        done: () => window._py_done(),
        selectItems: async function(items, callback) {
            const selected = await window._py_selectItems(items);
            callback(selected);
        },
        loadTranslator: function(type) {
            return {
                setTranslator: function(guid) { this.guid = guid; },
                setString: function(str) { this.str = str; },
                setHandler: function(event, handler) { this.handler = handler; },
                translate: function() {
                    if (this.guid === '951c027d-74ac-47d4-a107-9c3069ab7b48') {
                        const item = new Zotero.Item('webpage');
                        item.title = document.querySelector('meta[property="og:title"]')?.content || document.title;
                        this.handler('itemDone', this, item);
                    }
                }
            };
        }
    };
    window.Zotero.Item.prototype.complete = async function() {
        await window._py_completeItem(JSON.stringify(this));
    };
    window.ZU = {
        xpath: (doc, path) => {
            const results = [];
            const snapshot = doc.evaluate(path, doc, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
            for (let i = 0; i < snapshot.snapshotLength; i++) results.push(snapshot.snapshotItem(i));
            return results;
        },
        xpathText: (doc, path) => {
            const result = doc.evaluate(path, doc, null, XPathResult.STRING_TYPE, null);
            return result.stringValue ? result.stringValue.trim() : null;
        },
        trimInternal: (str) => str.replace(/\\s+/g, ' ').trim(),
        cleanAuthor: (name, type, useComma) => {
            if (!name) return { creatorType: type, lastName: '' };
            const parts = useComma ? name.split(/,\\s*/) : name.split(/\\s+/);
            const lastName = useComma ? parts.shift() : parts.pop();
            return { creatorType: type, lastName, firstName: parts.join(' ') };
        },
        strToISO: (str) => { try { return new Date(str).toISOString().split('T')[0]; } catch (e) { return str; } },
        doGet: async function(url, callback) {
            try {
                const responseText = await window._py_doGet(url);
                callback(responseText);
            } catch (e) { console.error("ZU.doGet failed:", e); }
        }
    };
"""


class ZoteroExecutor:
    """Orchestrates the execution of a Zotero translator in a Playwright page."""

    def __init__(self, page: Page):
        self.page = page
        self._completion_event = asyncio.Event()
        self._results = []

    async def _py_completeItem(self, item_json: str):
        logger.success("Item completed by translator.")
        self._results.append(json.loads(item_json))

    async def _py_done(self):
        logger.info("Translator signaled completion.")
        self._completion_event.set()

    async def _py_doGet(self, url: str) -> str:
        logger.info(f"Proxying GET request for: {url}")
        async with httpx.AsyncClient() as client:
            try:
                abs_url = urljoin(self.page.url, url)
                response = await client.get(abs_url, follow_redirects=True)
                response.raise_for_status()
                return response.text
            except Exception as e:
                logger.error(f"Failed to GET {url}: {e}")
                return ""

    async def _py_selectItems(self, items: dict) -> dict:
        logger.info("Translator requests item selection:")
        if not items:
            return {}
        print("\n--- Please select items to import ---")
        item_keys = list(items.keys())
        for i, key in enumerate(item_keys):
            print(f"  [{i+1}] {items[key]}")
        print("-------------------------------------")
        while True:
            try:
                choice_str = input("Enter numbers (e.g., 1,3), or 'all': ")
                if choice_str.lower() == "all":
                    return items
                choices = [int(c.strip()) for c in choice_str.split(",")]
                selected = {
                    item_keys[c - 1]: items[item_keys[c - 1]]
                    for c in choices
                    if 1 <= c <= len(item_keys)
                }
                return selected
            except (ValueError, IndexError):
                print("Invalid input. Please try again.")

    async def execute(self, translator_path: str) -> list[dict]:
        """Injects and runs a Zotero translator, returning the scraped items."""
        self._results = []
        self._completion_event.clear()

        await self.page.expose_function(
            "_py_completeItem", self._py_completeItem
        )
        await self.page.expose_function("_py_done", self._py_done)
        await self.page.expose_function("_py_doGet", self._py_doGet)
        await self.page.expose_function(
            "_py_selectItems", self._py_selectItems
        )
        await self.page.evaluate(ZOTERO_SHIM_JS)

        with open(translator_path, "r", encoding="utf-8") as f:
            translator_code = f.read()
        js_start_pos = translator_code.find("}")
        executable_code = translator_code[js_start_pos + 1 :]
        await self.page.evaluate(executable_code)

        logger.info(
            f"Executing translator: {os.path.basename(translator_path)}"
        )
        await self.page.evaluate("doWeb(document, document.location.href)")

        try:
            await asyncio.wait_for(self._completion_event.wait(), timeout=60.0)
        except asyncio.TimeoutError:
            logger.warning(
                "Translator did not call Zotero.done() within timeout."
            )

        return self._results


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
                header = f.read(2048)  # Read first 2KB to be safe
                match = re.search(
                    r"[\"\']target[\"\']:\s*[\"\'](.+?)[\"\']", header
                )
                if match:
                    target_regex = match.group(1).replace("\\\\", "\\")
                    if re.search(target_regex, url, re.IGNORECASE):
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
    name = os.path.splitext(name)[0]
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    return name.replace(" ", "_")[:100]


# --- HELPER: File Downloader ---
async def _download_attachment(url: str, save_path: str):
    logger.info(f"Attempting direct download from URL: {url}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True, timeout=60)
            response.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(response.content)
        logger.success(f"✅ Direct download successful. Saved to: {save_path}")
    except Exception as e:
        logger.error(f"❌ Download failed for {url}. Reason: {e}")


# --- PUBLIC INTERFACE FUNCTION ---
async def download_using_zotero_translator(
    page: Page, url: str
) -> dict | None:
    """
    Top-level function to find and execute the correct translator,
    then download the main item and its attachments.
    """
    translator_path = find_translator_for_url(page.url)
    if not translator_path:
        return None

    executor = ZoteroExecutor(page)
    scraped_items = await executor.execute(translator_path)

    if not scraped_items:
        logger.warning("Translator executed but returned no items.")
        return None

    # For now, process the first item found
    item = scraped_items[0]
    logger.info(f"Successfully scraped item: {item.get('title', 'No Title')}")

    article_slug = page.url.strip("/").split("/")[-1]
    article_dir = os.path.join(DOWNLOADS_DIR, _sanitize_filename(article_slug))
    os.makedirs(article_dir, exist_ok=True)
    logger.info(f"📁 Saving files to: {article_dir}")

    downloaded_files = []
    for attachment in item.get("attachments", []):
        if attachment.get("url"):
            attachment_url = urljoin(page.url, attachment["url"])
            filename = attachment.get(
                "title", os.path.basename(attachment_url).split("?")[0]
            )
            ext = (
                os.path.splitext(filename)[1]
                or f".{attachment.get('mimeType', 'application/octet-stream').split('/')[-1]}"
            )
            save_path = os.path.join(
                article_dir, f"{_sanitize_filename(filename)}{ext}"
            )

            await _download_attachment(attachment_url, save_path)
            if os.path.exists(save_path):
                downloaded_files.append(save_path)

    return {"metadata": item, "files": downloaded_files}

# EOF
