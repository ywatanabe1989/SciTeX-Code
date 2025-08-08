#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-07 22:55:46 (ywatanabe)"
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
            // This is a simplified stub for meta-translators
            return {
                setTranslator: function(guid) { this.guid = guid; },
                setString: function(str) { this.str = str; },
                setHandler: function(event, handler) { this.handler = handler; },
                translate: function() {
                    // For now, we only handle a basic "Embedded Metadata" case
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
            for (let i = 0; i < snapshot.snapshotLength; i++) {
                results.push(snapshot.snapshotItem(i));
            }
            return results;
        },
        xpathText: (doc, path) => {
            const result = doc.evaluate(path, doc, null, XPathResult.STRING_TYPE, null);
            return result.stringValue ? result.stringValue.trim() : null;
        },
        trimInternal: (str) => str.replace(/\\s+/g, ' ').trim(),
        cleanAuthor: (name, type, useComma) => {
            if (!name) return { creatorType: type, lastName: '' };
            if (useComma) {
                const parts = name.split(/,\\s*/);
                return { creatorType: type, lastName: parts[0], firstName: parts.slice(1).join(' ') };
            }
            const parts = name.split(/\\s+/);
            return { creatorType: type, lastName: parts.pop(), firstName: parts.join(' ') };
        },
        strToISO: (str) => {
            try {
                return new Date(str).toISOString().split('T')[0];
            } catch (e) { return str; }
        },
        doGet: async function(url, callback) {
            try {
                const responseText = await window._py_doGet(url);
                callback(responseText);
            } catch (e) {
                console.error("ZU.doGet failed:", e);
            }
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
        """Callback for when a translator completes an item."""
        logger.success("Item completed by translator.")
        self._results.append(json.loads(item_json))

    async def _py_done(self):
        """Callback for when a translator signals it is finished."""
        logger.info("Translator signaled completion.")
        self._completion_event.set()

    async def _py_doGet(self, url: str) -> str:
        """Proxies ZU.doGet requests to Python's httpx."""
        logger.info(f"Proxying GET request for: {url}")
        async with httpx.AsyncClient() as client:
            try:
                # Construct absolute URL if it's relative
                abs_url = await self.page.evaluate(
                    f"new URL('{url}', document.baseURI).href"
                )
                response = await client.get(abs_url, follow_redirects=True)
                response.raise_for_status()
                return response.text
            except Exception as e:
                logger.error(f"Failed to GET {url}: {e}")
                return ""

    async def _py_selectItems(self, items: dict) -> dict:
        """Handles Zotero.selectItems by prompting user in the console."""
        logger.info("Translator requests item selection:")
        if not items:
            return {}

        print("\\n--- Please select items to import ---")
        item_keys = list(items.keys())
        for i, key in enumerate(item_keys):
            print(f"  [{i+1}] {items[key]}")
        print("-------------------------------------")

        while True:
            try:
                choice_str = input(
                    "Enter numbers separated by commas (e.g., 1,3), or 'all': "
                )
                if choice_str.lower() == "all":
                    return items

                choices = [int(c.strip()) for c in choice_str.split(",")]
                selected = {}
                for c in choices:
                    if 1 <= c <= len(item_keys):
                        key = item_keys[c - 1]
                        selected[key] = items[key]
                return selected
            except (ValueError, IndexError):
                print("Invalid input. Please try again.")

    async def execute(self, translator_path: str) -> list[dict]:
        """Injects and runs a Zotero translator, returning the scraped items."""
        self._results = []
        self._completion_event.clear()

        # 1. Expose Python callbacks to the JavaScript environment
        await self.page.expose_function(
            "_py_completeItem", self._py_completeItem
        )
        await self.page.expose_function("_py_done", self._py_done)
        await self.page.expose_function("_py_doGet", self._py_doGet)
        await self.page.expose_function(
            "_py_selectItems", self._py_selectItems
        )

        # 2. Inject the Zotero shim environment
        await self.page.evaluate(ZOTERO_SHIM_JS)

        # 3. Read and inject the specific translator's code
        with open(translator_path, "r", encoding="utf-8") as f:
            translator_code = f.read()

        # Remove the JSON metadata block
        js_start_pos = translator_code.find("}")
        executable_code = translator_code[js_start_pos + 1 :]
        await self.page.evaluate(executable_code)

        # 4. Execute the translator's doWeb function
        logger.info(
            f"Executing translator: {os.path.basename(translator_path)}"
        )
        await self.page.evaluate("doWeb(document, document.location.href)")

        # 5. Wait for the translator to signal completion
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
    logger.info(f"Searching for translator for {url} in {translators_dir}...")

    for filename in os.listdir(translators_dir):
        if not filename.endswith(".js"):
            continue
        filepath = os.path.join(translators_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                header = "".join(f.readlines()[:50])
            match = re.search(r"[\"']target[\"']:\s*[\"'](.+?)[\"']", header)
            if match:
                target_regex = match.group(1).replace("\\\\", "\\")
                logger.info(
                    f"Testing {filename}: {target_regex} against {url}"
                )
                if re.search(target_regex, url):
                    logger.info(f"✅ Found matching translator: {filename}")
                    return filepath
        except Exception as e:
            logger.warning(f"Could not parse translator {filename}: {e}")

    logger.error(f"❌ No matching translator found for URL: {url}")
    return None


# Example usage would be in your _BrowserManager.py
if __name__ == "__main__":
    from scitex.scholar.auth import AuthenticationManager
    from scitex.scholar.browser.local import BrowserManager

    async def demo():
        auth_manager = AuthenticationManager()
        browser_manager = BrowserManager(
            auth_manager=auth_manager, browser_mode="interactive"
        )
        browser, context = (
            await browser_manager.get_authenticated_browser_and_context_async()
        )
        page = await context.new_page()

        test_url = "https://www.nature.com/articles/s41593-025-01990-7"
        await page.goto(test_url, wait_until="domcontentloaded")

        translator_path = find_translator_for_url(page.url)
        if translator_path:
            executor = ZoteroExecutor(page)
            scraped_items = await executor.execute(translator_path)

            print("\\n--- Scraped Items ---")
            for item in scraped_items:
                print(json.dumps(item, indent=2, ensure_ascii=False))
            print("---------------------")

        await asyncio.sleep(10)  # Keep browser open for a bit
        await browser.close()

    asyncio.run(demo())

# EOF
