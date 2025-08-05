#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-03 21:59:52 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/open_url/_OpenURLResolver.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/open_url/_OpenURLResolver.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
import random
from typing import List, Union

from scitex import logging

"""OpenURL resolver for finding full-text access through institutional libraries."""


from typing import Any, Dict, Optional
from urllib.parse import urlencode

from playwright.async_api import Page

from ...errors import ScholarError
from ..browser import BrowserManager
from ..config import ScholarConfig
from ._ResolverLinkFinder import ResolverLinkFinder

logger = logging.getLogger(__name__)


class OpenURLResolver:
    """Resolves DOIs/metadata to full-text URLs via institutional OpenURL resolver.

    OpenURL is a standardized format for encoding bibliographic information
    that libraries use to link to full-text resources."""

    AUTH_PATTERNS = [
        "openathens.net",
        "shibauth",
        "saml",
        "institutionlogin",
        "iam.atypon.com",
        "auth.elsevier.com",
        "go.gale.com/ps/headerQuickSearch",
    ]

    PUBLISHER_DOMAINS = [
        "sciencedirect.com",
        "nature.com",
        "springer.com",
        "wiley.com",
        "onlinelibrary.wiley.com",
        "acs.org",
        "tandfonline.com",
        "sagepub.com",
        "academic.oup.com",
        "science.org",
        "pnas.org",
        "bmj.com",
        "cell.com",
    ]

    def __init__(
        self,
        auth_manager,
        resolver_url: Optional[str] = None,
        browser_mode: str = "stealth",
        config: Optional[ScholarConfig] = None,
    ):
        """Initialize OpenURL resolver.

        Args:
            auth_manager: Authentication manager for institutional access
            resolver_url: Base URL of institutional OpenURL resolver
                         (Details can be seen at https://www.zotero.org/openurl_resolvers)
            browser_mode: Browser mode ("stealth" or "interactive")
            config: ScholarConfig instance (creates new if None)
        """
        self.auth_manager = auth_manager
        
        # Initialize config
        if config is None:
            config = ScholarConfig()
        self.config = config
        
        # Resolve resolver URL from config
        self.resolver_url = self.config.resolve(
            "openurl_resolver_url", resolver_url, None, str
        )
        
        # Create BrowserManager with simplified configuration
        self.browser = BrowserManager(
            auth_manager=auth_manager, 
            browser_mode=browser_mode,
            config=self.config
        )

        self.timeout = 30
        self._link_finder = ResolverLinkFinder()
        
        # Screenshot capture setup (optional, controlled by config)
        self.capture_screenshots = self.config.resolve("capture_screenshots", None, False, bool)
        if self.capture_screenshots:
            from datetime import datetime
            
            self.screenshot_dir = self.config.paths.get_screenshots_dir() / "openurl"
            self.screenshot_dir.mkdir(parents=True, exist_ok=True)
            self.session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    async def _capture_checkpoint_screenshot_async(
        self, page, stage: str, doi: str = ""
    ) -> Optional[str]:
        """Capture screenshot at checkpoint for debugging."""
        if not self.capture_screenshots:
            return None

        try:
            from datetime import datetime

            timestamp = datetime.now().strftime("%H%M%S")
            doi_safe = (
                doi.replace("/", "-").replace(".", "_") if doi else "unknown"
            )
            screenshot_name = f"openurl_{stage}_{doi_safe}_{timestamp}.png"
            screenshot_path = self.screenshot_dir / screenshot_name

            await page.screenshot(path=str(screenshot_path), full_page=True)
            logger.info(
                f"📸 Screenshot captured: {stage} -> {screenshot_name}"
            )
            return str(screenshot_path)
        except Exception as e:
            logger.warning(f"📸 Screenshot capture failed at {stage}: {e}")
            return None

    def build_openurl(
        self,
        title: str = "",
        authors: Optional[list] = None,
        journal: str = "",
        year: Optional[int] = None,
        volume: Optional[int] = None,
        issue: Optional[int] = None,
        pages: str = "",
        doi: str = "",
        pmid: str = "",
    ) -> str:
        """Build OpenURL query string from paper metadata."""
        params = {
            "ctx_ver": "Z39.88-2004",
            "rft_val_fmt": "info:ofi/fmt:kev:mtx:journal",
            "rft.genre": "article",
        }

        if title:
            params["rft.atitle"] = title
        if journal:
            params["rft.jtitle"] = journal
        if year:
            params["rft.date"] = str(year)
        if volume:
            params["rft.volume"] = str(volume)
        if issue:
            params["rft.issue"] = str(issue)
        if pages:
            if "-" in str(pages):
                spage, epage = pages.split("-", 1)
                params["rft.spage"] = spage.strip()
                params["rft.epage"] = epage.strip()
            else:
                params["rft.spage"] = str(pages)
        if doi:
            params["rft.doi"] = doi
        if pmid:
            params["rft.pmid"] = str(pmid)

        if authors:
            first_author = authors[0]
            if "," in first_author:
                last, first = first_author.split(",", 1)
                params["rft.aulast"] = last.strip()
                params["rft.aufirst"] = first.strip()
                params["rft.au"] = first_author

        query_string = urlencode(params, safe=":/")
        return f"{self.resolver_url}?{query_string}"

    def _is_publisher_url(self, url: str, doi: str = "") -> bool:
        """Check if URL is from expected publisher domain."""
        if not url:
            return False
        if any(pattern in url.lower() for pattern in self.AUTH_PATTERNS):
            return False
        if any(domain in url.lower() for domain in self.PUBLISHER_DOMAINS):
            return True
        else:
            return False

    async def _follow_saml_redirect_async(self, page, saml_url, doi=""):
        """Follow SAML/SSO redirect chain until publisher URL is reached."""
        logger.info(f"Following SAML redirect chain starting from: {saml_url}")

        if self._is_publisher_url(saml_url, doi):
            return saml_url

        await page.goto(
            saml_url,
            wait_until="domcontentloaded",
            timeout=15000,  # Increased from 1.5-3s to 15s
        )
        last_url = ""

        for attempt in range(8):
            current_url = page.url
            logger.debug(f"SAML redirect attempt {attempt + 1}: {current_url}")

            if self._is_publisher_url(current_url, doi):
                logger.info(
                    f"Successfully navigated to publisher URL: {current_url}"
                )
                return current_url

            # If URL hasn't changed in 2 attempts, we're stuck
            if current_url == last_url and attempt > 1:
                logger.warning(f"SAML redirect stuck at: {current_url}")
                return current_url

            last_url = current_url

            # Only try form submission first few attempts
            if attempt < 3:
                try:
                    forms = await page.query_selector_all("form")
                    for form in forms:
                        if await form.is_visible():
                            logger.debug("Submitting visible form...")
                            await form.evaluate("form => form.submit()")
                            await page.wait_for_load_state(
                                "domcontentloaded", timeout=10000
                            )
                            break
                except:
                    pass

            await page.wait_for_timeout(1000)

        final_url = page.url
        logger.info(f"SAML redirect completed at: {final_url}")
        return final_url

    async def _find_and_click_publisher_go_button_async(self, page, doi=""):
        """Find and click the appropriate publisher GO button on the OpenURL resolver page.

        This method implements our proven GO button detection and clicking logic
        that successfully worked for Science.org and Nature.com access.
        """
        try:
            logger.info("Looking for publisher GO buttons on resolver page...")

            # Get all GO buttons with context information
            go_buttons = await page.evaluate(
                """() => {
                const goButtons = Array.from(document.querySelectorAll('input[value="Go"], button[value="Go"], input[value="GO"], button[value="GO"]'));
                return goButtons.map((btn, index) => {
                    const parentRow = btn.closest('tr') || btn.parentElement;
                    const rowText = parentRow ? parentRow.textContent.trim() : '';

                    // Check for publisher indicators in the row text
                    const isScience = rowText.toLowerCase().includes('american association') ||
                                    rowText.toLowerCase().includes('aaas') ||
                                    rowText.toLowerCase().includes('science');
                    const isNature = rowText.toLowerCase().includes('nature') ||
                                   rowText.toLowerCase().includes('springer');
                    const isWiley = rowText.toLowerCase().includes('wiley');
                    const isElsevier = rowText.toLowerCase().includes('elsevier') ||
                                     rowText.toLowerCase().includes('sciencedirect');

                    return {
                        index: index,
                        globalIndex: Array.from(document.querySelectorAll('input, button, a, [onclick]')).indexOf(btn),
                        value: btn.value,
                        rowText: rowText,
                        isScience: isScience,
                        isNature: isNature,
                        isWiley: isWiley,
                        isElsevier: isElsevier,
                        isPublisher: isScience || isNature || isWiley || isElsevier
                    };
                });
            }"""
            )

            if not go_buttons:
                logger.warning("No GO buttons found on resolver page")
                return {"success": False, "reason": "no_go_buttons"}

            logger.info(f"Found {len(go_buttons)} GO buttons")
            for btn in go_buttons:
                logger.debug(
                    f"GO button {btn['index']}: {btn['rowText'][:50]}... (Publisher: {btn['isPublisher']})"
                )

            # Find the most appropriate publisher button
            target_button = None

            # Priority order: Science > Nature > Other publishers
            for btn in go_buttons:
                if btn["isScience"]:
                    target_button = btn
                    logger.info(
                        f"Selected Science/AAAS GO button: {btn['rowText'][:50]}..."
                    )
                    break
                elif btn["isNature"]:
                    target_button = btn
                    logger.info(
                        f"Selected Nature GO button: {btn['rowText'][:50]}..."
                    )
                    break
                elif btn["isPublisher"]:
                    target_button = btn
                    logger.info(
                        f"Selected publisher GO button: {btn['rowText'][:50]}..."
                    )
                    break

            # Fallback: if no publisher buttons, try the first few GO buttons (might be direct access)
            if not target_button and go_buttons:
                target_button = go_buttons[0]
                logger.info(
                    f"Using fallback GO button: {target_button['rowText'][:50]}..."
                )

            if not target_button:
                logger.warning("No suitable GO button found")
                return {"success": False, "reason": "no_suitable_button"}

            # Click the selected GO button and handle popup
            logger.info("Clicking GO button and waiting for popup...")

            try:
                # Set up popup listener before clicking
                popup_promise = page.wait_for_event("popup", timeout=30000)

                # Click the button using its global index for reliability
                click_result = await page.evaluate(
                    f"""() => {{
                    const allElements = Array.from(document.querySelectorAll('input, button, a, [onclick]'));
                    const targetButton = allElements[{target_button['globalIndex']}];
                    if (targetButton && (targetButton.value === 'Go' || targetButton.value === 'GO')) {{
                        console.log('Clicking GO button:', targetButton);
                        targetButton.click();
                        return 'clicked';
                    }}
                    return 'not-found';
                }}"""
                )

                if click_result != "clicked":
                    logger.warning("Failed to click GO button")
                    return {"success": False, "reason": "click_failed"}

                # Wait for popup
                popup = await popup_promise
                logger.info("Publisher popup opened successfully")

                # Wait for popup to load
                await popup.wait_for_load_state(
                    "domcontentloaded", timeout=30000
                )
                await popup.wait_for_timeout(5000)  # Allow time for redirects

                final_url = popup.url
                popup_title = await popup.title()

                logger.info(f"Successfully accessed: {popup_title}")
                logger.info(f"Final URL: {final_url}")

                # Verify we reached a publisher URL
                if self._is_publisher_url(final_url, doi):
                    logger.success(
                        f"Successfully reached publisher: {final_url}"
                    )

                    result = {
                        "final_url": final_url,
                        "resolver_url": page.url,
                        "access_type": "publisher_go_button",
                        "success": True,
                        "publisher_detected": True,
                        "popup_page": popup,  # Keep popup open for potential PDF download_async
                    }

                    # Don't close popup immediately - let caller decide
                    # await popup.close()
                    return result
                else:
                    logger.info(f"Reached non-publisher URL: {final_url}")

                    result = {
                        "final_url": final_url,
                        "resolver_url": page.url,
                        "access_type": "go_button_redirect",
                        "success": True,
                        "publisher_detected": False,
                        "popup_page": popup,  # Keep popup open for potential PDF download_async
                    }

                    # Don't close popup immediately - let caller decide
                    # await popup.close()
                    return result

            except Exception as popup_error:
                logger.warning(f"Popup handling failed: {popup_error}")
                return {
                    "success": False,
                    "reason": f"popup_error: {popup_error}",
                }

        except Exception as e:
            logger.error(f"GO button detection failed: {e}")
            return {"success": False, "reason": f"detection_error: {e}"}

    async def _download_async_pdf_async_from_publisher_page(
        self, popup, filename, download_async_dir="download_asyncs"
    ):
        """Download PDF from publisher page after successful GO button access.

        This method implements our proven PDF download_async logic that works
        with various publisher sites including Science.org and Nature.com.
        """
        from pathlib import Path

        try:
            download_async_path = Path(download_async_dir)
            download_async_path.mkdir(exist_ok=True)

            logger.info("Looking for PDF download_async links on publisher page...")

            # Find PDF download_async links
            pdf_links = await popup.evaluate(
                """() => {
                const allLinks = Array.from(document.querySelectorAll('a, button, input'));
                return allLinks.filter(el =>
                    el.textContent.toLowerCase().includes('pdf') ||
                    el.textContent.toLowerCase().includes('download_async') ||
                    el.href?.includes('pdf') ||
                    el.getAttribute('data-track-action')?.includes('pdf')
                ).map(el => ({
                    tag: el.tagName,
                    text: el.textContent.trim(),
                    href: el.href || el.value || 'no-href',
                    className: el.className,
                    id: el.id,
                    trackAction: el.getAttribute('data-track-action') || 'none'
                }));
            }"""
            )

            if not pdf_links:
                logger.warning("No PDF links found on publisher page")
                return {"success": False, "reason": "no_pdf_links"}

            logger.info(f"Found {len(pdf_links)} potential PDF links")
            for i, link in enumerate(pdf_links):
                logger.debug(
                    f"PDF link {i}: {link['text'][:30]}... | {link['href'][:50]}..."
                )

            # Find the best PDF download_async link
            main_pdf_link = None

            # Priority order: direct download_async > PDF with download_async > PDF view
            for link in pdf_links:
                if "download_async pdf" in link["text"].lower():
                    main_pdf_link = link
                    break
                elif link["href"] != "no-href" and link["href"].endswith(
                    ".pdf"
                ):
                    main_pdf_link = link
                    break
                elif (
                    "pdf" in link["text"].lower()
                    and "view" not in link["text"].lower()
                ):
                    main_pdf_link = link
                    break

            if not main_pdf_link:
                main_pdf_link = pdf_links[
                    0
                ]  # Fallback to first PDF-related link

            logger.info(f"Selected PDF link: {main_pdf_link['text'][:40]}...")

            # Set up download_async path
            file_path = download_async_path / filename

            # Configure download_async headers
            await popup.set_extra_http_headers(
                {"Accept": "application/pdf,application/octet-stream,*/*"}
            )

            # Try download_async methods
            pdf_download_asynced = False

            # Method 1: Direct URL navigation
            if (
                main_pdf_link["href"] != "no-href"
                and "pdf" in main_pdf_link["href"].lower()
            ):
                try:
                    logger.info("Attempting direct PDF URL download_async...")
                    download_async_promise = popup.wait_for_event(
                        "download_async", timeout=30000
                    )
                    await popup.goto(main_pdf_link["href"])

                    download_async = await download_async_promise
                    await download_async.save_as(str(file_path))

                    if file_path.exists():
                        size_mb = file_path.stat().st_size / (1024 * 1024)
                        logger.success(
                            f"PDF download_asynced successfully: {filename} ({size_mb:.1f} MB)"
                        )
                        pdf_download_asynced = True

                except Exception as e:
                    logger.debug(f"Direct download_async failed: {e}")

            # Method 2: Click-based download_async
            if not pdf_download_asynced:
                try:
                    logger.info("Attempting click-based PDF download_async...")
                    download_async_promise = popup.wait_for_event(
                        "download_async", timeout=30000
                    )

                    # Click the first PDF link
                    await popup.evaluate(
                        """() => {
                        const allLinks = Array.from(document.querySelectorAll('a, button, input'));
                        const pdfLinks = allLinks.filter(el =>
                            el.textContent.toLowerCase().includes('pdf') ||
                            el.textContent.toLowerCase().includes('download_async') ||
                            el.href?.includes('pdf')
                        );
                        if (pdfLinks.length > 0) {
                            pdfLinks[0].click();
                            return 'clicked';
                        }
                        return 'no-link';
                    }"""
                    )

                    download_async = await download_async_promise
                    await download_async.save_as(str(file_path))

                    if file_path.exists():
                        size_mb = file_path.stat().st_size / (1024 * 1024)
                        logger.success(
                            f"PDF download_asynced successfully: {filename} ({size_mb:.1f} MB)"
                        )
                        pdf_download_asynced = True

                except Exception as e:
                    logger.debug(f"Click-based download_async failed: {e}")

            if pdf_download_asynced:
                return {
                    "success": True,
                    "filename": filename,
                    "path": str(file_path),
                    "size_mb": (
                        file_path.stat().st_size / (1024 * 1024)
                        if file_path.exists()
                        else 0
                    ),
                }
            else:
                logger.warning("All PDF download_async methods failed")
                # Take screenshot for debugging
                screenshot_path = (
                    download_async_path
                    / f"pdf_download_async_failed_{filename.replace('.pdf', '.png')}"
                )
                await popup.screenshot(
                    path=str(screenshot_path), full_page=True
                )
                logger.info(
                    f"Screenshot saved for debugging: {screenshot_path}"
                )

                return {
                    "success": False,
                    "reason": "download_async_failed",
                    "screenshot": str(screenshot_path),
                    "available_links": [link["text"] for link in pdf_links],
                }

        except Exception as e:
            logger.error(f"PDF download_async failed: {e}")
            return {"success": False, "reason": f"error: {e}"}

    async def resolve_and_download_async_pdf_async(
        self,
        title: str = "",
        authors: Optional[list] = None,
        journal: str = "",
        year: Optional[int] = None,
        volume: Optional[int] = None,
        issue: Optional[int] = None,
        pages: str = "",
        doi: str = "",
        pmid: str = "",
        filename: str = None,
        download_async_dir: str = "download_asyncs",
    ) -> Dict[str, Any]:
        """Resolve paper access and download_async PDF in one operation.

        This method combines our GO button resolution with PDF download_async
        to provide a complete paper acquisition workflow.
        """
        if not filename:
            # Generate filename from metadata
            first_author = (
                authors[0].split(",")[0].strip() if authors else "Unknown"
            )
            filename = f"{first_author}-{year}-{journal.replace(' ', '')}-{title[:30].replace(' ', '_')}.pdf"
            # Clean filename
            filename = "".join(
                c for c in filename if c.isalnum() or c in ".-_"
            ).strip()

        logger.info(f"Starting resolve and download_async for: {filename}")

        # Create fresh context for this operation
        browser, context = await self.browser.get_authenticate_async_context()
        page = await context.new_page()

        try:
            # Build OpenURL
            openurl = self.build_openurl(
                title, authors, journal, year, volume, issue, pages, doi, pmid
            )
            logger.info(f"Resolving and download_asyncing via OpenURL: {openurl}")

            # Navigate to OpenURL resolver
            await page.goto(
                openurl, wait_until="domcontentloaded", timeout=30000
            )
            await page.wait_for_timeout(2000)

            # Try GO button method
            go_button_result = await self._find_and_click_publisher_go_button_async(
                page, doi
            )

            if (
                go_button_result["success"]
                and "popup_page" in go_button_result
            ):
                popup = go_button_result["popup_page"]

                logger.info(
                    "Successfully accessed publisher page, attempting PDF download_async..."
                )

                # Try to download_async PDF
                download_async_result = await self._download_async_pdf_async_from_publisher_page(
                    popup, filename, download_async_dir
                )

                # Close popup
                try:
                    await popup.close()
                except:
                    pass

                # Combine results
                final_result = {
                    **go_button_result,
                    "pdf_download_async": download_async_result,
                    "filename": filename,
                }

                # Remove popup reference
                if "popup_page" in final_result:
                    del final_result["popup_page"]

                if download_async_result["success"]:
                    logger.success(f"Successfully download_asynced PDF: {filename}")
                else:
                    logger.warning(
                        f"Paper accessed but PDF download_async failed: {download_async_result.get('reason', 'unknown')}"
                    )

                return final_result

            else:
                logger.warning("Could not access publisher page via GO button")
                return {
                    "success": False,
                    "reason": "go_button_failed",
                    "go_button_result": go_button_result,
                    "filename": filename,
                }

        except Exception as e:
            logger.error(f"Resolve and download_async failed: {e}")
            return {
                "success": False,
                "reason": f"error: {e}",
                "filename": filename,
            }
        finally:
            await context.close()

    async def _resolve_single_async(
        self,
        title: str = "",
        authors: Optional[list] = None,
        journal: str = "",
        year: Optional[int] = None,
        volume: Optional[int] = None,
        issue: Optional[int] = None,
        pages: str = "",
        doi: str = "",
        pmid: str = "",
    ) -> Optional[Dict[str, Any]]:

        # Note: Removed self.__init__ call that was creating second BrowserManager
        # This was causing configuration inconsistency - the resolver is already initialized

        if not doi:
            logger.warning("DOI is required for reliable resolution")

        # Create fresh context for each resolution
        browser, context = await self.browser.get_authenticate_async_context()
        page = await context.new_page()

        openurl = self.build_openurl(
            title, authors, journal, year, volume, issue, pages, doi, pmid
        )
        logger.info(f"Resolving via OpenURL: {openurl}")

        try:
            logger.info("Navigating to OpenURL resolver...")

            # Clear any existing navigation state
            await page.wait_for_timeout(1000)

            await page.goto(
                openurl, wait_until="domcontentloaded", timeout=30000
            )

            # Checkpoint 1: After loading OpenURL resolver page
            await self._capture_checkpoint_screenshot_async(
                page, "01_openurl_loaded", doi
            )

            # Apply stealth behaviors if using standard browser
            if hasattr(self.browser, "stealth_manager"):
                await self.browser.stealth_manager.human_delay_async()
                await self.browser.stealth_manager.human_mouse_move_async(page)
                await self.browser.stealth_manager.human_scroll_async(page)

            await page.wait_for_timeout(2000)

            # Checkpoint 2: After stealth behaviors applied
            await self._capture_checkpoint_screenshot_async(
                page, "02_stealth_applied", doi
            )

            current_url = page.url
            if self._is_publisher_url(current_url, doi):
                logger.info(
                    f"Resolver redirected directly to publisher: {current_url}"
                )
                return {
                    "final_url": current_url,
                    "resolver_url": openurl,
                    "access_type": "direct_redirect",
                    "success": True,
                }

            content = await page.content()
            if any(
                phrase in content
                for phrase in [
                    "No online text available",
                    "No full text available",
                    "No electronic access",
                ]
            ):
                logger.warn("Resolver indicates no access available")
                return {
                    "final_url": None,
                    "resolver_url": current_url,
                    "access_type": "no_access",
                    "success": False,
                }

            logger.info("Looking for full-text link on resolver page...")

            # First try our GO button method
            go_button_result = await self._find_and_click_publisher_go_button_async(
                page, doi
            )
            if go_button_result["success"]:
                # Clean up popup if it exists
                if "popup_page" in go_button_result:
                    popup = go_button_result["popup_page"]
                    try:
                        await popup.close()
                    except:
                        pass
                    # Remove popup reference from result
                    del go_button_result["popup_page"]
                return go_button_result

            # Fallback to original link finder method
            link_result = await self._link_finder.find_link_async(page, doi)

            if not link_result["success"]:
                logger.warning(
                    "Could not find full-text link on resolver page"
                )
                return {
                    "final_url": None,
                    "resolver_url": current_url,
                    "access_type": "link_not_found",
                    "success": False,
                }

            link_url = link_result["url"]

            if link_url.startswith("javascript:"):
                logger.info("Handling JavaScript link...")
                try:
                    async with page.expect_popup(timeout=30000) as popup_info:
                        await page.evaluate(
                            link_url.replace("javascript:", "")
                        )

                    popup = await popup_info.value
                    await popup.wait_for_load_state(
                        "domcontentloaded", timeout=30000
                    )
                    final_url = popup.url

                    if any(
                        domain in final_url
                        for domain in ["openathens.net", "saml", "shibauth"]
                    ):
                        final_url = await self._follow_saml_redirect_async(
                            popup, final_url, doi
                        )

                    logger.info(f"Successfully resolved to popup: {final_url}")
                    await popup.close()

                    return {
                        "final_url": final_url,
                        "resolver_url": openurl,
                        "access_type": "institutional",
                        "success": True,
                    }

                except Exception as popup_error:
                    logger.warning(f"Popup handling failed: {popup_error}")
                    return {
                        "final_url": None,
                        "resolver_url": openurl,
                        "access_type": "popup_error",
                        "success": False,
                    }
            else:
                try:
                    new_page_promise = None

                    def handle_page_async(new_page):
                        nonlocal new_page_promise
                        new_page_promise = new_page
                        logger.info(f"New page detected: {new_page.url}")

                    context.on("page", handle_page_async)

                    await page.goto(
                        link_url, wait_until="domcontentloaded", timeout=30000
                    )
                    await page.wait_for_timeout(3000)

                    if new_page_promise:
                        target_page = new_page_promise
                        await target_page.wait_for_load_state(
                            "domcontentloaded", timeout=30000
                        )
                        final_url = target_page.url
                        logger.info(f"Using new window: {final_url}")
                        await target_page.close()
                    else:
                        final_url = page.url

                    if any(
                        domain in final_url.lower()
                        for domain in [
                            "openathens.net",
                            "saml",
                            "shibauth",
                            "institutionlogin",
                        ]
                    ):
                        final_url = await self._follow_saml_redirect_async(
                            page, final_url, doi
                        )

                    return {
                        "final_url": final_url,
                        "resolver_url": openurl,
                        "access_type": "institutional",
                        "success": True,
                    }

                except Exception as nav_error:
                    logger.error(f"Navigation failed: {nav_error}")
                    return {
                        "final_url": None,
                        "resolver_url": openurl,
                        "access_type": "navigation_error",
                        "success": False,
                    }

        except Exception as e:
            logger.error(f"OpenURL resolution failed: {e}")
            return {
                "final_url": None,
                "resolver_url": openurl,
                "access_type": "error",
                "success": False,
            }
        finally:
            await context.close()
            # await page.close()

    def _resolve_single(self, **kwargs) -> str:
        """Synchronous wrapper for _resolve_single_async."""
        import asyncio

        try:
            # Try to get existing loop
            loop = asyncio.get_running_loop()
            # If we're in Jupyter/IPython, use nest_asyncio
            import nest_asyncio

            nest_asyncio.apply()
            result = asyncio.run(self._resolve_single_async(**kwargs))
        except RuntimeError:
            # No running loop, create new one
            result = asyncio.run(self._resolve_single_async(**kwargs))

        self._validate_final_url(kwargs.get("doi", ""), result)
        return result.get("resolved_url") if result else None

    async def _resolve_parallel_async(
        self, dois: Union[str, List[str]], concurrency: int = 2
    ) -> List[Optional[Dict[str, Any]]]:
        """Resolves a list of DOIs in parallel with controlled concurrency.

        Args:
            dois: A list of DOI strings to resolve.
            concurrency: Maximum number of concurrent tasks (default: 2)

        Returns:
            A list of result dictionaries, in the same order as the input DOIs.
        """
        if not dois:
            return []

        is_single = False
        if isinstance(dois, str):
            dois = [dois]
            is_single = True

        logger.info(
            f"--- Starting parallel resolution for {len(dois)} DOIs (concurrency: {concurrency}) ---"
        )

        # Create semaphore to limit concurrency
        semaphore = asyncio.Semaphore(concurrency)

        async def worker_async(doi):
            async with semaphore:
                # Add random delay between requests to appear more human
                await asyncio.sleep(random.uniform(0.5, 2.0))
                return await self._resolve_single_async(doi=doi)

        # Create tasks using the worker_async function
        tasks = [worker_async(doi) for doi in dois]
        results = await asyncio.gather(*tasks)

        logger.info("--- Parallel resolution finished ---")
        return results[0] if is_single else results

    def resolve(
        self, dois: Union[str, List[str]], concurrency: int = 5
    ) -> Union[str, List[str]]:
        """Synchronous wrapper for _resolve_parallel_async."""
        try:
            loop = asyncio.get_running_loop()
            import nest_asyncio

            nest_asyncio.apply()
            results = asyncio.run(
                self._resolve_parallel_async(dois, concurrency)
            )
        except RuntimeError:
            results = asyncio.run(
                self._resolve_parallel_async(dois, concurrency)
            )

        # Validate results
        dois_list = [dois] if isinstance(dois, str) else dois
        results_list = [results] if not isinstance(results, list) else results
        for doi, result in zip(dois_list, results_list):
            self._validate_final_url(doi, result)

        return results

    def _validate_final_url(self, doi, result):
        if result and result.get("success"):
            final_url = result.get("final_url", "")

            # Check if we reached a publisher URL
            if self._is_publisher_url(final_url, doi=doi):
                logger.success(f"{doi}: {final_url}")
                result["resolved_url"] = final_url
                return True

            # Also accept Elsevier linking hub as success
            elif "linkinghub.elsevier.com" in final_url:
                logger.success(f"{doi}: {final_url} (Elsevier linking hub)")
                result["resolved_url"] = final_url
                return True

            # If we have a URL but it's not a publisher, still mark as partial success
            elif (
                final_url
                and "chrome-error" not in final_url
                and "openathens" not in final_url.lower()
            ):
                logger.info(f"{doi}: Reached {final_url}")
                result["resolved_url"] = final_url
                return True

        # Only mark as failed if no URL or error/auth page
        final_url = result.get("final_url") if result else "N/A"
        logger.fail(f"{doi}: Failed - {final_url}")
        if result:
            result["resolved_url"] = None
        return False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self.browser, "cleanup_authenticate_async_context"):
            await self.browser.cleanup_authenticate_async_context()


async def try_openurl_resolver_async(
    title: str = "",
    authors: Optional[list] = None,
    journal: str = "",
    year: Optional[int] = None,
    volume: Optional[int] = None,
    issue: Optional[int] = None,
    pages: str = "",
    doi: str = "",
    pmid: str = "",
    resolver_url: Optional[str] = None,
    auth_manager=None,
) -> Optional[str]:
    """Try to find full-text URL via OpenURL resolver."""
    async with OpenURLResolver(auth_manager, resolver_url) as resolver:
        result = await resolver._resolve_single_async(
            title, authors, journal, year, volume, issue, pages, doi, pmid
        )
        if result and result.get("success") and result.get("final_url"):
            return result["final_url"]
    return None


if __name__ == "__main__":
    import asyncio

    async def main():
        """Test the resolver with different articles."""
        # from scitex import logging
        # logging.basicConfig(level=logging.DEBUG)
        from ..auth import AuthenticationManager

        auth_manager = AuthenticationManager()
        # resolver_url = "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"

        async with OpenURLResolver(auth_manager) as resolver:
            print("\n=== Test 1: Article with access ===")
            result = await resolver._resolve_single_async(
                doi="10.1002/hipo.22488",
                title="Hippocampal sharp wave-ripple: A cognitive biomarker for episodic memory and planning",
                authors=["Buzsáki, György"],
                journal="Hippocampus",
                year=2015,
                volume=25,
                issue=10,
                pages="1073-1188",
            )
            print(f"Result: {result}")

            print("\n=== Test 2: Article without access ===")
            result = await resolver._resolve_single_async(
                doi="10.1038/s41593-025-01990-7",
                title="Addressing artifactual bias in large, automated MRI analyses of brain development",
                journal="Nature Neuroscience",
                year=2025,
            )
            print(f"Result: {result}")

    asyncio.run(main())


# python -m scitex.scholar.open_url._OpenURLResolver

# EOF
