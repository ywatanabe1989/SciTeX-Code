#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-07 23:01:37 (ywatanabe)"
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
import glob
import re
import shutil
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin

import httpx
from playwright.async_api import Page

from scitex import logging

from scitex.scholar.config import ScholarConfig

__DIR__ = os.path.dirname(os.path.abspath(__file__))
zotero_translators_dir = os.path.join(__DIR__, "zotero_translators")
config = ScholarConfig()
DOWNLOADS_DIR = config.get_downloads_dir()
logger = logging.getLogger(__name__)


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
                if re.search(target_regex, url):
                    logger.info(f"✅ Found matching translator: {filename}")
                    return filepath
        except Exception as e:
            logger.warning(f"Could not parse translator {filename}: {e}")

    logger.error(f"❌ No matching translator found for URL: {url}")
    return None


def _sanitize_filename(name: str) -> str:
    name = os.path.splitext(name)[0]
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    return name.replace(" ", "_")[:100]


async def _download_file(page: Page, save_path: str, url: str, selector: str):
    logger.info(f"Attempting to download '{os.path.basename(save_path)}'...")
    
    # Method 1: Try clicking the visible download button/link
    try:
        element = page.locator(selector).first
        
        # Check if element is visible, if not try to find a visible one
        if not await element.is_visible():
            # Try to find any visible download element
            visible_selectors = [
                'button:visible:has-text("Download PDF")',
                'a:visible:has-text("Download PDF")',
                '.u-button--primary:visible:has-text("Download")',
                'a[href$=".pdf"]:visible'
            ]
            
            for vis_selector in visible_selectors:
                try:
                    vis_element = page.locator(vis_selector).first
                    if await vis_element.is_visible():
                        element = vis_element
                        logger.info(f"Found visible element with selector: {vis_selector}")
                        break
                except:
                    continue
        
        if await element.is_visible():
            # First, try to dismiss any overlays/modals that might be blocking
            try:
                # Common overlay dismissal selectors
                dismiss_selectors = [
                    'button[aria-label="Close"]',
                    'button:has-text("Accept")',
                    'button:has-text("I agree")',
                    'button:has-text("OK")',
                    '[class*="close-button"]',
                    '[class*="dismiss"]'
                ]
                
                for dismiss_sel in dismiss_selectors:
                    try:
                        dismiss_btn = page.locator(dismiss_sel).first
                        if await dismiss_btn.is_visible():
                            await dismiss_btn.click()
                            await asyncio.sleep(0.5)
                            logger.info(f"Dismissed overlay with: {dismiss_sel}")
                    except:
                        pass
            except:
                pass
            
            # Try download with force click
            try:
                # Set up download with context manager
                async with page.expect_download(timeout=10000) as download_info:
                    # Click with force to bypass intercepting elements
                    await element.click(force=True)
                
                # Get the download
                download = await download_info.value
                
                # Save the file
                await download.save_as(save_path)
                
                # Verify it's a PDF
                with open(save_path, 'rb') as f:
                    header = f.read(10)
                    if header.startswith(b'%PDF'):
                        logger.success(f"✅ Downloaded valid PDF to: {save_path}")
                        return True
                    else:
                        logger.warning(f"Downloaded file is not a PDF")
                        os.remove(save_path)
                        
            except asyncio.TimeoutError:
                logger.info("Download didn't trigger, trying new tab approach...")
                
    except Exception as e:
        logger.warning(f"Initial download attempt failed: {e}")
    
    # Method 2: Handle new tab/window opening (common for PDF viewers)
    try:
        logger.info("Trying new tab approach...")
        
        # Find the best element to click
        element = page.locator(selector).first
        if not await element.is_visible():
            # Try to find visible PDF link
            for alt_selector in ['a[href$=".pdf"]:visible', 'button:visible:has-text("PDF")', 'a:visible:has-text("PDF")']:
                alt_element = page.locator(alt_selector).first
                if await alt_element.is_visible():
                    element = alt_element
                    break
        
        # Some sites open PDF in new tab
        async with page.context.expect_page(timeout=5000) as new_page_info:
            await element.click(force=True)
        
        new_page = await new_page_info.value
        logger.info(f"New tab opened: {new_page.url}")
        
        # Set up PDF capture
        pdf_content = None
        
        async def capture_pdf(response):
            nonlocal pdf_content
            try:
                if '.pdf' in response.url.lower() or 'pdf' in response.headers.get('content-type', '').lower():
                    body = await response.body()
                    if body and body.startswith(b'%PDF'):
                        pdf_content = body
                        logger.info(f"Captured PDF: {len(body)} bytes")
            except:
                pass
        
        new_page.on('response', capture_pdf)
        
        # Wait for PDF to load
        await new_page.wait_for_load_state('networkidle')
        await asyncio.sleep(2)
        
        if pdf_content:
            with open(save_path, 'wb') as f:
                f.write(pdf_content)
            logger.success(f"✅ Downloaded PDF from new tab: {save_path}")
            await new_page.close()
            return True
        
        await new_page.close()
        
    except asyncio.TimeoutError:
        logger.info("No new tab opened")
    except Exception as e:
        logger.debug(f"New tab approach failed: {e}")
    
    # Method 3: Direct navigation to PDF URL with route interception
    try:
        if url and url != selector:  # Only if we have a URL different from selector
            logger.info(f"Trying direct navigation with route interception: {url}")
            
            new_page = await page.context.new_page()
            
            # Method 3a: Set up route interception to force download
            logger.info("Setting up route interception to force PDF download...")
            
            # Set up download promise before navigation
            download_captured = None
            
            async def handle_download(download):
                nonlocal download_captured
                download_captured = download
                logger.info(f"Download intercepted: {download.suggested_filename}")
            
            new_page.on('download', handle_download)
            
            # Intercept PDF requests and force download
            async def intercept_pdf_route(route, request):
                try:
                    if '.pdf' in request.url.lower():
                        logger.info(f"Intercepting PDF request: {request.url[:100]}...")
                        
                        # Get the response
                        response = await page.context.request.get(request.url)
                        
                        # Modify headers to force download
                        headers = response.headers
                        headers['content-disposition'] = 'attachment'
                        
                        # Fulfill with modified headers
                        await route.fulfill(
                            body=await response.body(),
                            headers=headers,
                            status=response.status
                        )
                        logger.info("Modified headers to force download")
                    else:
                        await route.continue_()
                except Exception as e:
                    logger.debug(f"Route interception error: {e}")
                    await route.continue_()
            
            # Set up the route
            await new_page.route('**/*', intercept_pdf_route)
            
            # Navigate to PDF URL
            await new_page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # Wait for potential download with periodic checks
            max_wait = 10  # seconds
            check_interval = 0.5
            elapsed = 0
            
            while elapsed < max_wait and not download_captured:
                await asyncio.sleep(check_interval)
                elapsed += check_interval
            
            # Check if download was captured
            if download_captured:
                logger.info("Download captured via route interception")
                try:
                    # Save the download
                    await download_captured.save_as(save_path)
                    
                    # Wait for download to complete
                    failure = await download_captured.failure()
                    if failure:
                        logger.warning(f"Download failed: {failure}")
                    else:
                        # Verify it's a PDF
                        if os.path.exists(save_path) and os.path.getsize(save_path) > 10000:
                            with open(save_path, 'rb') as f:
                                if f.read(4) == b'%PDF':
                                    logger.success(f"✅ Downloaded PDF via route interception: {save_path}")
                                    await new_page.close()
                                    return True
                                else:
                                    logger.warning("Downloaded file is not a valid PDF")
                        else:
                            logger.warning("Downloaded file is too small or doesn't exist")
                except Exception as save_error:
                    logger.error(f"Failed to save intercepted download: {save_error}")
            
            # Method 3b: Original response interception as fallback
            # Set up response interception
            pdf_content = None
            
            response_count = 0
            async def intercept_pdf(response):
                nonlocal pdf_content, response_count
                response_count += 1
                
                try:
                    # Log ALL responses to understand what's happening
                    url_lower = response.url.lower()
                    content_type = response.headers.get('content-type', '').lower()
                    
                    # Log every response briefly
                    if response_count <= 20:  # Limit logging
                        logger.debug(f"Response #{response_count}: {response.url[:80]}... [{response.status}] {content_type[:30] if content_type else 'no-content-type'}")
                    
                    # Check if this might be a PDF response
                    if 'pdf' in content_type or '.pdf' in url_lower or 'blob:' in url_lower:
                        logger.info(f"Potential PDF response from: {response.url}")
                        logger.info(f"Response status: {response.status}")
                        logger.info(f"Content-Type: {content_type}")
                        
                        # Try to get the body
                        try:
                            body = await response.body()
                            if body:
                                logger.info(f"Got response body: {len(body)} bytes")
                                if body.startswith(b'%PDF'):
                                    pdf_content = body
                                    logger.success(f"✅ Captured actual PDF content: {len(body)} bytes")
                                else:
                                    # Show what we got instead
                                    preview = body[:100] if len(body) < 1000 else body[:50]
                                    logger.warning(f"Body doesn't start with %PDF. Preview: {preview}")
                            else:
                                logger.warning("Response body is empty")
                        except Exception as body_error:
                            logger.warning(f"Could not get body: {body_error}")
                except Exception as e:
                    logger.error(f"Response interception error: {e}")
            
            # Attach the interceptor
            new_page.on('response', intercept_pdf)
            
            # Navigate to PDF URL
            response = await new_page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Start periodic screenshots in background
            logger.info("Starting periodic screenshots while PDF loads...")
            
            # Get browser manager instance if available (for periodic screenshots)
            browser_manager = None
            if hasattr(page.context, '_browser_manager'):
                browser_manager = page.context._browser_manager
            
            screenshot_task = None
            if browser_manager and hasattr(browser_manager, 'start_periodic_screenshots_async'):
                screenshot_task = await browser_manager.start_periodic_screenshots_async(
                    new_page,
                    prefix=f"pdf_download_{url.split('/')[-1][:20]}",
                    interval_seconds=1,
                    duration_seconds=15,  # Take screenshots for 15 seconds
                    verbose=False
                )
            
            # Wait for PDF to load
            await asyncio.sleep(10)
            
            # Stop screenshots
            if screenshot_task and browser_manager:
                await browser_manager.stop_periodic_screenshots_async(screenshot_task)
            
            # Check if we captured the PDF
            if pdf_content:
                with open(save_path, 'wb') as f:
                    f.write(pdf_content)
                logger.success(f"✅ Saved actual PDF content: {save_path}")
                await new_page.close()
                return True
            
            # If PDF is in viewer but we couldn't capture it, try alternative methods
            logger.info("PDF viewer detected, attempting alternative extraction methods...")
            
            # Method 4: Try Ctrl+S to save the PDF (only in interactive mode)
            if hasattr(page.context, '_browser_manager') and \
               getattr(page.context._browser_manager, 'browser_mode', '') == 'interactive':
                logger.info("Method 4: Attempting Ctrl+S to save PDF (interactive mode)...")
                try:
                    # First, focus on the PDF content area to ensure Ctrl+S works
                    await new_page.click('body')
                    await asyncio.sleep(0.5)
                    
                    # Set up download handler BEFORE pressing Ctrl+S
                    # Use longer timeout for large PDFs
                    download_promise = new_page.wait_for_event("download", timeout=30000)
                    
                    # Press Ctrl+S to trigger save
                    # Use ControlOrMeta for cross-platform compatibility
                    await new_page.keyboard.press("ControlOrMeta+s")
                    logger.info("Pressed Ctrl+S, waiting for download...")
                    
                    # Wait for the download to start
                    try:
                        download = await download_promise
                        logger.info(f"Download started: {download.suggested_filename}")
                        
                        # Save the downloaded file
                        # This will wait for download to complete
                        logger.info("Waiting for download to complete...")
                        
                        # Monitor download progress
                        start_time = asyncio.get_event_loop().time()
                        max_wait = 60  # Maximum 60 seconds for download
                        
                        # Save the file (this blocks until download completes)
                        try:
                            await download.save_as(save_path)
                            download_time = asyncio.get_event_loop().time() - start_time
                            logger.info(f"Download completed in {download_time:.1f} seconds")
                        except Exception as save_error:
                            logger.error(f"Failed to save download: {save_error}")
                            # Try to get the download path and copy manually
                            download_path = await download.path()
                            if download_path and os.path.exists(download_path):
                                import shutil
                                shutil.copy2(download_path, save_path)
                                logger.info(f"Copied from download path: {download_path}")
                        
                        # Check if download succeeded
                        failure = await download.failure()
                        if failure:
                            logger.warning(f"Download failed: {failure}")
                            # Clean up failed download
                            if os.path.exists(save_path):
                                os.remove(save_path)
                        else:
                            # Verify it's a real PDF and has reasonable size
                            if os.path.exists(save_path):
                                file_size = os.path.getsize(save_path)
                                with open(save_path, 'rb') as f:
                                    header = f.read(4)
                                    
                                if header == b'%PDF' and file_size > 10000:  # At least 10KB
                                    logger.success(f"✅ Downloaded actual PDF via Ctrl+S: {save_path}")
                                    logger.info(f"File size: {file_size:,} bytes")
                                    await new_page.close()
                                    return True
                                else:
                                    if header != b'%PDF':
                                        logger.warning("Downloaded file is not a valid PDF")
                                    else:
                                        logger.warning(f"PDF too small ({file_size} bytes), likely incomplete")
                                    os.remove(save_path)
                    except asyncio.TimeoutError:
                        logger.warning("No download triggered by Ctrl+S (may need manual intervention)")
                        
                except Exception as ctrl_s_error:
                    logger.debug(f"Ctrl+S method failed: {ctrl_s_error}")
            else:
                logger.debug("Skipping Ctrl+S method (not in interactive mode)")
            
            # Method 5: Try to get the actual PDF URL from the embed element
            try:
                pdf_src = await new_page.evaluate("""
                    () => {
                        // Look for embed element with PDF
                        const embed = document.querySelector('embed[type="application/pdf"]');
                        if (embed) {
                            return embed.src;
                        }
                        
                        // Check for Chrome PDF viewer plugin
                        const plugin = document.querySelector('embed[type="application/x-google-chrome-pdf"]');
                        if (plugin) {
                            return plugin.src;
                        }
                        
                        return null;
                    }
                """)
                
                if pdf_src and pdf_src.startswith('blob:'):
                    logger.info(f"Found blob URL: {pdf_src}")
                    # Blob URLs can't be downloaded directly, but we can try to get the content
                    try:
                        pdf_blob = await new_page.evaluate("""
                            async (blobUrl) => {
                                try {
                                    const response = await fetch(blobUrl);
                                    const blob = await response.blob();
                                    const buffer = await blob.arrayBuffer();
                                    const bytes = new Uint8Array(buffer);
                                    return Array.from(bytes);
                                } catch (e) {
                                    return null;
                                }
                            }
                        """, pdf_src)
                        
                        if pdf_blob:
                            pdf_bytes = bytes(pdf_blob)
                            if pdf_bytes.startswith(b'%PDF'):
                                with open(save_path, 'wb') as f:
                                    f.write(pdf_bytes)
                                logger.success(f"✅ Extracted actual PDF from blob: {save_path} ({len(pdf_bytes)} bytes)")
                                await new_page.close()
                                return True
                    except Exception as blob_error:
                        logger.debug(f"Blob extraction failed: {blob_error}")
                
            except Exception as embed_error:
                logger.debug(f"Embed extraction failed: {embed_error}")
            
            # Method 5: Use Chrome DevTools to download
            try:
                # Enable Page domain for Chrome DevTools
                client = await new_page.context.new_cdp_session(new_page)
                
                # Try to trigger download through DevTools
                await client.send('Page.setDownloadBehavior', {
                    'behavior': 'allow',
                    'downloadPath': '/tmp'
                })
                
                # Navigate again to trigger download
                logger.info("Attempting DevTools download by reloading...")
                await new_page.reload()
                await asyncio.sleep(3)
                
                # Check if file was downloaded
                import glob
                downloads = glob.glob('/tmp/*.pdf')
                if downloads:
                    latest = max(downloads, key=os.path.getctime)
                    with open(latest, 'rb') as f:
                        pdf_content = f.read()
                    if pdf_content.startswith(b'%PDF'):
                        with open(save_path, 'wb') as f:
                            f.write(pdf_content)
                        logger.success(f"✅ Downloaded via DevTools: {save_path}")
                        os.remove(latest)  # Clean up temp file
                        await new_page.close()
                        return True
                        
            except Exception as cdp_error:
                logger.debug(f"CDP download failed: {cdp_error}")
            
            # Method 6: Last resort - Use print-to-PDF (creates a screenshot-like PDF)
            logger.info("Falling back to print-to-PDF (screenshot mode)...")
            try:
                is_pdf_viewer = '.pdf' in new_page.url
                
                if is_pdf_viewer:
                    logger.warning("Using print-to-PDF - this creates a visual copy, not the original PDF")
                    
                    # Use Playwright's PDF generation
                    pdf_bytes = await new_page.pdf(
                        format='A4',
                        print_background=True,
                        margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'}
                    )
                    
                    if pdf_bytes and pdf_bytes.startswith(b'%PDF'):
                        # This is a rendered PDF, but check if it has actual content
                        if len(pdf_bytes) > 50000:  # At least 50KB (typical paper is much larger)
                            with open(save_path, 'wb') as f:
                                f.write(pdf_bytes)
                            logger.warning(f"⚠️ Saved screenshot-PDF: {save_path} ({len(pdf_bytes)} bytes)")
                            logger.warning("This is a visual capture, not the original PDF. Text may not be selectable.")
                            await new_page.close()
                            return True
                        else:
                            logger.warning(f"Printed PDF too small ({len(pdf_bytes)} bytes), likely not complete")
            except Exception as print_error:
                logger.debug(f"Print-to-PDF failed: {print_error}")
            
            # If we didn't capture it, try getting it from the initial response
            if response:
                try:
                    response_body = await response.body()
                    if response_body and response_body.startswith(b'%PDF'):
                        with open(save_path, 'wb') as f:
                            f.write(response_body)
                        logger.success(f"✅ Saved PDF from navigation response: {save_path}")
                        await new_page.close()
                        return True
                except:
                    pass
            
            # Check for PDF in iframe/embed and try to download the src
            pdf_frame = await new_page.query_selector('iframe[src*=".pdf"], embed[src*=".pdf"]')
            if pdf_frame:
                pdf_src = await pdf_frame.get_attribute('src')
                if pdf_src:
                    logger.info(f"PDF embed detected, source: {pdf_src}")
                    # Try to download the embedded PDF
                    full_url = urljoin(new_page.url, pdf_src)
                    try:
                        async with httpx.AsyncClient() as client:
                            resp = await client.get(full_url, follow_redirects=True, timeout=30.0)
                            if resp.status_code == 200 and resp.content.startswith(b'%PDF'):
                                with open(save_path, 'wb') as f:
                                    f.write(resp.content)
                                logger.success(f"✅ Downloaded embedded PDF: {save_path}")
                                await new_page.close()
                                return True
                    except Exception as e:
                        logger.debug(f"Failed to download embedded PDF: {e}")
            
            logger.warning("Could not capture actual PDF content")
            await new_page.close()
            
    except Exception as e:
        logger.debug(f"Direct navigation failed: {e}")
    
    logger.warning(f"Could not download PDF for '{os.path.basename(save_path)}'")
    return False


async def execute_translator(page: Page, translator_path: str) -> dict:
    logger.info(f"Executing translator: {os.path.basename(translator_path)}")

    zotero_shim = """
    window.Zotero = {
        Utilities: {
            xpath: (doc, xpath, namespaces) => {
                const results = [];
                const snapshot = doc.evaluate(xpath, doc, namespaces, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                for(let ii = 0; ii < snapshot.snapshotLength; ii++) {
                    results.push(snapshot.snapshotItem(ii));
                }
                return results;
            },
            xpathText: (doc, xpath, namespaces, index) => {
                const result = doc.evaluate(xpath, doc, namespaces, XPathResult.STRING_TYPE, null);
                return result.stringValue ? result.stringValue.trim() : '';
            },
            trimInternal: (str) => str ? str.trim().replace(/\\s+/g, ' ') : '',
            cleanAuthor: function(author, type) {
                if (typeof author === 'object') {
                    return {
                        firstName: author.firstName || author.given || '',
                        lastName: author.lastName || author.family || '',
                        creatorType: type || author.creatorType || "author"
                    };
                }
                const parts = author.trim().split(/\\s+/);
                return {
                    firstName: parts.slice(0, -1).join(' '),
                    lastName: parts[parts.length - 1] || '',
                    creatorType: type || "author"
                };
            },
            capitalizeTitle: function(str) {
                return str ? str.charAt(0).toUpperCase() + str.slice(1) : '';
            }
        },
        debug: message => console.log(message),
        loadTranslator: function(type) {
            const translatorObj = {
                handlers: {},
                setTranslator: function(id) { 
                    this.translatorID = id; 
                },
                setDocument: function(doc) {
                    this.document = doc;
                },
                setSearch: function(search) { 
                    this.search = search; 
                },
                setHandler: function(event, handler) {
                    this.handlers[event] = handler;
                },
                translate: function() {
                    // For embedded metadata translator, extract basic metadata
                    if (this.translatorID === "951c027d-74ac-47d4-a107-9c3069ab7b48") {
                        const item = new window.Zotero.Item("journalArticle");
                        
                        // Extract metadata from meta tags
                        const metas = document.getElementsByTagName('meta');
                        for (let meta of metas) {
                            const name = meta.getAttribute('name') || meta.getAttribute('property');
                            const content = meta.getAttribute('content');
                            if (!name || !content) continue;
                            
                            if (name === 'citation_title' || name === 'DC.Title' || name === 'og:title') {
                                item.title = content;
                            } else if (name === 'citation_doi' || name === 'DC.Identifier') {
                                item.DOI = content.replace(/^doi:/, '');
                            } else if (name === 'citation_journal_title' || name === 'citation_journal') {
                                item.publicationTitle = content;
                            } else if (name === 'citation_volume') {
                                item.volume = content;
                            } else if (name === 'citation_issue') {
                                item.issue = content;
                            } else if (name === 'citation_firstpage') {
                                item.pages = content;
                            } else if (name === 'citation_lastpage' && item.pages) {
                                item.pages = item.pages + '-' + content;
                            } else if (name === 'citation_author') {
                                const parts = content.split(', ');
                                item.creators.push({
                                    lastName: parts[0] || '',
                                    firstName: parts[1] || '',
                                    creatorType: 'author'
                                });
                            } else if (name === 'citation_publication_date' || name === 'DC.Date') {
                                item.date = content;
                            } else if (name === 'citation_abstract' || name === 'DC.Description') {
                                item.abstractNote = content;
                            }
                        }
                        
                        // Call itemDone handler if set
                        if (this.handlers.itemDone) {
                            this.handlers.itemDone(this, item);
                        }
                    }
                    
                    if (this.handlers.done) {
                        this.handlers.done();
                    }
                }
            };
            return translatorObj;
        },
        Item: function(type) {
            this.itemType = type || "journalArticle";
            this.creators = [];
            this.tags = [];
            this.attachments = [];
            this.notes = [];
            this.complete = function() {
                window._zoteroItems = window._zoteroItems || [];
                window._zoteroItems.push(this);
            };
        }
    };

    // Global translator object that some translators expect
    window.translator = {
        setDocument: function(doc) { 
            window.doc = doc;
            this.document = doc;
        },
        document: document,
        setTranslator: function(id) { this.translatorID = id; },
        setHandler: function(event, handler) {
            this.handlers = this.handlers || {};
            this.handlers[event] = handler;
        },
        getTranslatorObject: function(callback) {
            // Some translators expect this
            if (callback) callback(this);
            return this;
        }
    };

    window.Z = window.Zotero;
    window.ZU = window.Zotero.Utilities;
    window._zoteroItems = [];
    """

    try:
        with open(translator_path, "r", encoding="utf-8") as f:
            translator_code = f.read()

        js_start_pos = translator_code.find("}")
        executable_code = translator_code[js_start_pos + 1 :]
        full_script = (
            f"{zotero_shim}\n{executable_code}\ndoWeb(document, '{page.url}');"
        )

        result = await page.evaluate(full_script)
        logger.success("✅ Translator executed successfully")
        return result or {}

    except Exception as e:
        logger.error(f"❌ Failed to execute translator: {e}")
        return {}


async def download_article_and_supplements(
    page: Page, translator_path: str
) -> dict | None:
    logger.info(f"--- Starting Download Process for: {page.url} ---")

    article_slug = page.url.strip("/").split("/")[-1]
    article_dir = os.path.join(DOWNLOADS_DIR, _sanitize_filename(article_slug))
    os.makedirs(article_dir, exist_ok=True)
    logger.info(f"📁 Saving files to: {article_dir}")

    downloaded_files = {"main_pdf": None, "supplementary": []}

    # Execute translator first
    translator_result = await execute_translator(page, translator_path)

    # Fallback to hardcoded selectors
    main_pdf_selector = "//a[@data-track-action='download pdf' or normalize-space(.)='Download PDF']"
    try:
        main_pdf_relative_url = await page.locator(
            main_pdf_selector
        ).first.get_attribute("href", timeout=5000)
        if main_pdf_relative_url:
            main_pdf_url = urljoin(page.url, main_pdf_relative_url)
            logger.success(f"Found Main PDF URL: {main_pdf_url}")
            pdf_save_path = os.path.join(article_dir, "main_article.pdf")
            success = await _download_file(
                page, pdf_save_path, main_pdf_url, main_pdf_selector
            )

            if success and os.path.exists(pdf_save_path) and os.path.getsize(pdf_save_path) > 0:
                # Double-check it's actually a PDF
                with open(pdf_save_path, 'rb') as f:
                    if f.read(4) == b'%PDF':
                        downloaded_files["main_pdf"] = pdf_save_path
                    else:
                        logger.warning("Downloaded main file is not a valid PDF")
                        os.remove(pdf_save_path)
    except Exception as e:
        logger.warning(f"⚠️ Could not find main PDF URL. Reason: {e}")

    # Find supplementary files
    supplementary_script = """
    () => {
        const container = document.evaluate(
            "//div[@id='supplementary-information']|//div[./h2[starts-with(normalize-space(.),'Supplementary')]]",
            document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null
        ).singleNodeValue || document;

        const links = Array.from(container.querySelectorAll('a'))
            .map(a => a.href && {text: a.textContent.trim(), href: a.href})
            .filter(Boolean);

        return links;
    }
    """

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

        # Only download if it looks like a PDF
        if '.pdf' in supp_url.lower() or 'pdf' in link['text'].lower():
            success = await _download_file(page, supp_save_path, supp_url, supp_selector)
            
            if success and os.path.exists(supp_save_path) and os.path.getsize(supp_save_path) > 0:
                # Verify it's actually a PDF
                with open(supp_save_path, 'rb') as f:
                    if f.read(4) == b'%PDF':
                        downloaded_files["supplementary"].append(supp_save_path)
                    else:
                        logger.info(f"Supplementary file is not a PDF, skipping")
                        os.remove(supp_save_path)
        else:
            logger.info(f"Skipping non-PDF supplementary file: {supp_url}")

    return downloaded_files


async def download_using_zotero_translator(
    page: Page, url: str
) -> dict | None:
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
