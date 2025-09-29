#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: _ZoteroTranslatorRunner_v03-clean.py
# ----------------------------------------

"""
Clean Zotero translator runner with external JavaScript.

This version uses an external JavaScript file to avoid escaping issues.
"""

import asyncio
import json
import re
from pathlib import Path
from typing import Dict, List, Optional

from playwright.async_api import Page, async_playwright

from scitex import logging
from scitex.scholar.browser.utils.JSLoader import JSLoader

logger = logging.getLogger(__name__)


class ZoteroTranslatorRunner:
    """Execute Zotero translators to extract URLs from pages."""

    def __init__(self, translator_dir: Optional[Path] = None):
        """Initialize with translator directory."""
        self.translator_dir = translator_dir or (Path(__file__).parent / "zotero_translators")
        self._translators = self._load_translators()
        
        # Initialize JSLoader for managing JavaScript files
        js_base_dir = Path(__file__).parent.parent.parent.parent / "browser" / "js"
        self.js_loader = JSLoader(js_base_dir)
        
        # Pre-load essential Zotero JavaScript modules
        self._load_js_modules()
    
    def _load_js_modules(self):
        """Load JavaScript modules using JSLoader."""
        try:
            # Load Zotero environment and executor
            self.zotero_env_js = self.js_loader.load("integrations/zotero/zotero_environment.js")
            self.zotero_executor_js = self.js_loader.load("integrations/zotero/zotero_translator_executor.js")
            
            # Cache the combined JavaScript for injection
            self.combined_zotero_js = self.zotero_env_js + "\n" + self.zotero_executor_js
            
            logger.info("Loaded Zotero JavaScript modules successfully")
        except FileNotFoundError as e:
            logger.error(f"Failed to load JavaScript modules: {e}")
            # Fallback to inline JavaScript if files not found
            self.combined_zotero_js = self._get_fallback_js()
    
    def _get_fallback_js(self) -> str:
        """Get minimal fallback JavaScript if files not found."""
        logger.warning("Using minimal fallback JavaScript")
        return """
        console.warn('Using minimal Zotero environment fallback');
        window.Zotero = { Item: function() { this.complete = function() {}; } };
        window.Z = window.Zotero;
        window.ZU = {};
        window.attr = (doc, sel, attr) => doc.querySelector(sel)?.getAttribute(attr);
        window.text = (doc, sel) => doc.querySelector(sel)?.textContent.trim();
        window.requestDocument = async () => document;
        window.requestText = async () => '';
        """

    def _load_translators(self) -> Dict[str, Dict]:
        """Load translators with their code."""
        translators = {}

        if not self.translator_dir.exists():
            logger.warning(f"Translator directory not found: {self.translator_dir}")
            return translators

        for js_file in self.translator_dir.glob("*.js"):
            if js_file.name.startswith("_"):
                continue

            try:
                with open(js_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract metadata JSON
                lines = content.split("\n")
                json_end_idx = -1
                brace_count = 0

                for i, line in enumerate(lines):
                    if line.strip() == "{":
                        brace_count = 1
                    elif brace_count > 0:
                        brace_count += line.count("{") - line.count("}")
                        if brace_count == 0:
                            json_end_idx = i
                            break

                if json_end_idx == -1:
                    continue

                # Extract and parse metadata
                metadata_str = "\n".join(lines[: json_end_idx + 1])
                metadata_str = re.sub(r",(\s*})", r"\1", metadata_str)
                metadata = json.loads(metadata_str)

                # Only keep web translators
                if metadata.get("translatorType", 0) & 4 and metadata.get("target"):
                    # Extract JavaScript code (after metadata)
                    js_code = "\n".join(lines[json_end_idx + 1 :]).lstrip()

                    # Remove test cases section
                    test_idx = js_code.find("/** BEGIN TEST CASES **/")
                    if test_idx > 0:
                        js_code = js_code[:test_idx]

                    translators[js_file.stem] = {
                        "target_regex": metadata["target"],
                        "label": metadata.get("label", js_file.stem),
                        "code": js_code,
                    }
            except Exception as e:
                logger.warning(f"Failed to load {js_file.name}: {e}")
                continue

        logger.info(f"Loaded {len(translators)} Zotero translators")
        return translators

    def reload_js_modules(self):
        """Reload JavaScript modules, useful for development."""
        self.js_loader.clear_cache()
        self._load_js_modules()
        logger.info("Reloaded JavaScript modules")
    
    def get_loaded_modules(self) -> list:
        """Get list of loaded JavaScript modules."""
        return self.js_loader.get_cached_scripts()
    
    def find_translator_for_url(self, url: str) -> Optional[Dict]:
        """Find matching translator for URL."""
        for name, translator in self._translators.items():
            try:
                if re.match(translator["target_regex"], url):
                    logger.debug(f"URL matches translator: {translator['label']}")
                    return translator
            except:
                continue
        return None

    async def extract_urls_pdf_async(self, page: Page, capture_console: bool = True) -> List[str]:
        """Execute Zotero translator on page to extract PDF URLs."""
        url = page.url
        translator = self.find_translator_for_url(url)
        if not translator:
            logger.debug(f"No Zotero translator found for {url}")
            return []

        logger.info(f"Executing Zotero translator: {translator['label']}")
        
        # Capture console messages if requested
        console_messages = []
        if capture_console:
            def handle_console(msg):
                console_messages.append(f"[{msg.type}] {msg.text}")
                if msg.type in ["error", "warning"]:
                    logger.debug(f"Browser console: {msg.text}")
            
            page.on("console", handle_console)
        
        # Try to handle any popups before running translator
        try:
            # Check for cookie popup
            cookie_button = await page.query_selector('button#onetrust-accept-btn-handler')
            if cookie_button:
                await cookie_button.click()
                await page.wait_for_timeout(1000)
                logger.info("Accepted cookies")
            
            # Check for any other popups and close them
            close_selectors = [
                'button[aria-label*="Close"]',
                'button[aria-label*="close"]',
                'button.close-button',
                'button.close',
                '[aria-label*="dismiss"]',
            ]
            
            for selector in close_selectors:
                try:
                    btn = await page.query_selector(selector)
                    if btn and await btn.is_visible():
                        await btn.click()
                        await page.wait_for_timeout(500)
                        logger.info(f"Closed popup with selector: {selector}")
                        break
                except:
                    continue
        except Exception as e:
            logger.debug(f"Popup handling: {e}")
        
        try:
            # Inject the combined Zotero JavaScript environment
            await page.add_script_tag(content=self.combined_zotero_js)
            
            # Prepare translator code for execution
            # Use page.evaluate with arguments to avoid string interpolation issues
            translator_code = translator["code"]
            translator_label = translator["label"]
            
            # Execute the translator using the injected environment
            try:
                # Pass the translator code and label as a single argument object
                result = await page.evaluate(
                    '''
                    async (params) => {
                        return await executeZoteroTranslator(params.code, params.label);
                    }
                    ''',
                    {"code": translator_code, "label": translator_label}
                )
            except Exception as e:
                # Log the detailed error
                logger.error(f"Error executing translator JavaScript: {e}")
                
                # Check if it's a syntax error in the translator code
                if "SyntaxError" in str(e):
                    logger.error("Translator code may contain syntax errors or HTML content")
                    
                    # Try to understand what went wrong
                    page_info = await page.evaluate('''
                        () => ({
                            url: window.location.href,
                            title: document.title,
                            hasZoteroEnv: typeof window.Zotero !== 'undefined',
                            hasExecutor: typeof window.executeZoteroTranslator !== 'undefined'
                        })
                    ''')
                    logger.debug(f"Page state: {page_info}")
                
                # Return error result
                result = {
                    "success": False,
                    "translator": translator["label"],
                    "urls": [],
                    "error": str(e)
                }
            
            # Show console logs from translator execution
            if result.get("logs"):
                for log_entry in result.get("logs", []):
                    logger.debug(f"[Translator {log_entry.get('type')}] {log_entry.get('message')}")

            if result.get("error"):
                logger.error(f"Translator error: {result.get('error')}")
                
            # Log important console messages if captured
            if capture_console and console_messages:
                for msg in console_messages:
                    if any(keyword in msg.lower() for keyword in ["error", "auth", "login", "denied", "ris"]):
                        logger.debug(f"Console: {msg}")
                
            if result.get("success") and result.get("urls"):
                unique_urls = list(set(result.get("urls", [])))
                logger.success(
                    f"Zotero Translator extracted {len(unique_urls)} unique URLs from {page.url}"
                )
                return unique_urls
            else:
                logger.warning(
                    f"Zotero Translator did not extract any URLs from {page.url}"
                )
                # Show some console messages to help debug
                if capture_console and console_messages:
                    recent_msgs = console_messages[-5:]  # Last 5 messages
                    for msg in recent_msgs:
                        logger.debug(f"Recent console: {msg}")
                return []

        except Exception as e:
            logger.error(f"Error executing translator: {e}")
            return []


# Convenience function for use in finder
async def find_urls_pdf_with_translator(page: Page) -> List[str]:
    """
    Find PDF URLs by executing Zotero translator.

    Args:
        page: Loaded Playwright page

    Returns:
        List of PDF URLs found by translator
    """
    runner = ZoteroTranslatorRunner()
    return await runner.extract_urls_pdf_async(page)


async def main():
    """Demonstrate Zotero translator functionality."""
    import sys
    
    # Get URL from command line or use default
    test_url = sys.argv[1] if len(sys.argv) > 1 else "https://www.sciencedirect.com/science/article/pii/S1087079220300964"
    
    print(f"🔍 Testing Zotero Translator Runner")
    print(f"URL: {test_url}")
    print("-" * 50)
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Navigate to the URL
        print(f"📄 Navigating to {test_url}...")
        await page.goto(test_url, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)  # Wait for dynamic content
        
        # Try to handle cookie acceptance popup if present
        try:
            # Common cookie accept button selectors for ScienceDirect
            cookie_selectors = [
                'button#onetrust-accept-btn-handler',
                'button[aria-label*="accept"]',
                'button[id*="accept"]',
                'button:has-text("Accept")',
                'button:has-text("Accept all")',
                'button:has-text("I agree")',
            ]
            
            for selector in cookie_selectors:
                try:
                    accept_button = await page.query_selector(selector)
                    if accept_button:
                        print(f"🍪 Found cookie accept button with selector: {selector}")
                        await accept_button.click()
                        await page.wait_for_timeout(1000)  # Wait for popup to close
                        print("✅ Accepted cookies")
                        break
                except:
                    continue
        except Exception as e:
            print(f"⚠️ No cookie popup found or already accepted: {e}")
        
        # Check for any popups/modals and close them
        print("🔍 Checking for popups/modals...")
        try:
            # First check if any modal/overlay exists
            popup_check = await page.evaluate("""
                () => {
                    // Check for common modal/overlay selectors
                    const modalSelectors = [
                        '.modal',
                        '.overlay',
                        '[role="dialog"]',
                        '.popup',
                        '#onetrust-banner-sdk',
                        '.onetrust-pc-dark-filter',
                        '[class*="modal"]',
                        '[class*="popup"]',
                        '[class*="overlay"]'
                    ];
                    
                    for (const selector of modalSelectors) {
                        try {
                            const elements = document.querySelectorAll(selector);
                            for (const el of elements) {
                                const style = window.getComputedStyle(el);
                                if (style.display !== 'none' && style.visibility !== 'hidden' && el.offsetParent !== null) {
                                    return {
                                        found: true,
                                        selector: selector,
                                        text: el.innerText?.substring(0, 100)
                                    };
                                }
                            }
                        } catch (e) {
                            console.log('Error checking selector:', selector, e);
                        }
                    }
                    return { found: false };
                }
            """)
            
            if popup_check.get('found'):
                print(f"📢 Found popup: {popup_check.get('selector')}")
                print(f"   Text preview: {popup_check.get('text', '')[:50]}...")
                
                # Try to close any popup found
                close_selectors = [
                    'button[aria-label*="Close"]',
                    'button[aria-label*="close"]',
                    'button.close-button',
                    'button.close',
                    'button:has-text("No thanks")',
                    'button:has-text("Maybe later")',
                    'button:has-text("Skip")',
                    'button:has-text("Dismiss")',
                    '[aria-label*="dismiss"]',
                    '.modal-close',
                    '.popup-close',
                    '.close-icon',
                    'svg[class*="close"]',
                    'button[class*="close"]'
                ]
                
                for selector in close_selectors:
                    try:
                        close_button = await page.query_selector(selector)
                        if close_button and await close_button.is_visible():
                            print(f"   Clicking close button: {selector}")
                            await close_button.click()
                            await page.wait_for_timeout(1000)
                            print("   ✅ Closed popup")
                            break
                    except:
                        continue
            else:
                print("✅ No popups detected")
                
        except Exception as e:
            print(f"⚠️ Error checking for popups: {e}")
        
        # Initialize translator runner
        runner = ZoteroTranslatorRunner()
        
        # Check if translator matches
        translator = runner.find_translator_for_url(test_url)
        if translator:
            print(f"✅ Found translator: {translator['label']}")
        else:
            print("❌ No matching translator found")
            await browser.close()
            return
        
        # Set up console logging to capture translator debug output
        page.on("console", lambda msg: print(f"[Browser Console] {msg.text}"))
        
        # Check page content before extraction
        page_info = await page.evaluate("""
            () => {
                // Check for PDF-related elements that ScienceDirect translator looks for
                const pdfElements = {
                    pdfLink: document.querySelector('#pdfLink')?.href,
                    citationPdfUrl: document.querySelector('[name="citation_pdf_url"]')?.content,
                    pdfEmbed: document.querySelector('.PdfEmbed > object')?.getAttribute('data'),
                    downloadPdf: document.querySelector('a[aria-label*="Download PDF"]')?.href,
                    downloadButton: document.querySelector('.download-pdf-link')?.href,
                    accessContent: !!document.querySelector('.accessContent'),
                    checkAccess: !!document.querySelector('#check-access-popover'),
                    // Check for any link with PDF in it
                    anyPdfLink: Array.from(document.querySelectorAll('a[href*="pdf"], a[href*="PDF"]'))
                        .map(a => a.href)
                        .filter(url => url && !url.includes('#'))
                        .slice(0, 3)  // Just first 3 to avoid too much output
                };
                
                return {
                    title: document.title,
                    url: window.location.href,
                    bodyText: document.body.textContent.substring(0, 200),
                    bodyLength: document.body.textContent.length,
                    hasContent: document.body.textContent.trim().length > 0,
                    pdfElements: pdfElements
                };
            }
        """)
        print(f"📄 Page info:")
        print(f"   Title: {page_info.get('title')}")
        print(f"   URL: {page_info.get('url')}")
        print(f"   Body length: {page_info.get('bodyLength')} chars")
        print(f"   Has content: {page_info.get('hasContent')}")
        print(f"   PDF elements found:")
        for key, value in page_info.get('pdfElements', {}).items():
            if value:
                print(f"     {key}: {value}")
        
        # Extract PDF URLs
        print("🔍 Extracting PDF URLs...")
        pdf_urls = await runner.extract_urls_pdf_async(page)
        
        if pdf_urls:
            print(f"✅ Found {len(pdf_urls)} PDF URLs:")
            for url in pdf_urls:
                print(f"  - {url}")
        else:
            print("❌ No PDF URLs found")
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())