#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-31 20:48:02 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/open_url/_OpenURLResolver.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/open_url/_OpenURLResolver.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import random
from typing import List, Union

from scitex import logging

"""OpenURL resolver for finding full-text access through institutional libraries.
Based on University of Melbourne library recommendation."""

import asyncio
from typing import Any, Dict, Optional
from urllib.parse import urlencode

from playwright.async_api import Page

from ...errors import ScholarError
from ..browser import BrowserManager
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
        resolver_url,
        zenrows_api_key: Optional[str] = os.getenv(
            "SCITEX_SCHOLAR_ZENROWS_API_KEY"
        ),
        proxy_country: Optional[str] = os.getenv(
            "SCITEX_SCHOLAR_ZENROWS_PROXY_COUNTRY", "us"
        ),
    ):
        """Initialize OpenURL resolver.

        Args:
            auth_manager: Authentication manager for institutional access
            resolver_url: Base URL of institutional OpenURL resolver
                         (Details can be seen at https://www.zotero.org/openurl_resolvers)
            zenrows_api_key: API key for ZenRows (auto-enables stealth browser)
            proxy_country: Country code for ZenRows proxy
        """
        self.auth_manager = auth_manager
        self.resolver_url = resolver_url
        self.zenrows_api_key = zenrows_api_key

        # Prioritize ZenRows stealth when API key present
        if self.zenrows_api_key:
            logger.info(
                "Using ZenRows stealth browser for anti-bot protection"
            )
            from ..browser.local._ZenRowsBrowserManager import (
                ZenRowsBrowserManager,
            )

            self.browser = ZenRowsBrowserManager(
                auth_manager=auth_manager,
                headless=False,  # Show for manual auth
                proxy_username=os.getenv(
                    "SCITEX_SCHOLAR_ZENROWS_PROXY_USERNAME"
                ),
                proxy_password=os.getenv(
                    "SCITEX_SCHOLAR_ZENROWS_PROXY_PASSWORD"
                ),
            )
            self.use_zenrows = True
        else:
            # Standard local browser
            self.browser = BrowserManager(auth_manager, backend="local")
            self.use_zenrows = False

        self.timeout = 30
        self._link_finder = ResolverLinkFinder()

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

    async def _follow_saml_redirect(self, page, saml_url, doi=""):
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

        self.__init__(self.auth_manager, self.resolver_url)

        if not doi:
            logger.warning("DOI is required for reliable resolution")

        # Create fresh context for each resolution
        if self.use_zenrows:
            # Using ZenRowsStealthyLocal - need to pass auth cookies
            browser = await self.browser.get_browser()

            # Get authentication cookies from auth_manager
            cookies = None
            if self.auth_manager:
                try:
                    # Check if authenticated
                    if await self.auth_manager.is_authenticated():
                        cookies = await self.auth_manager.get_auth_cookies()
                        logger.info(
                            f"Retrieved {len(cookies)} authentication cookies"
                        )
                    else:
                        logger.warning(
                            "Not authenticated - no cookies to transfer"
                        )
                except Exception as e:
                    logger.warning(f"Could not retrieve auth cookies: {e}")

            # Create context with cookies
            context = await self.browser.new_context(cookies=cookies)
            page = await context.new_page()
        else:
            # Using standard BrowserManager
            browser, context = await self.browser.get_authenticated_context()
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

            # Apply stealth behaviors if using standard browser
            if not self.use_zenrows and hasattr(
                self.browser, "stealth_manager"
            ):
                await self.browser.stealth_manager.human_delay()
                await self.browser.stealth_manager.human_mouse_move(page)
                await self.browser.stealth_manager.human_scroll(page)

            await page.wait_for_timeout(2000)

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
            link_result = await self._link_finder.find_link(page, doi)

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
                        final_url = await self._follow_saml_redirect(
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

                    def handle_page(new_page):
                        nonlocal new_page_promise
                        new_page_promise = new_page
                        logger.info(f"New page detected: {new_page.url}")

                    context.on("page", handle_page)

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
                        final_url = await self._follow_saml_redirect(
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

        async def worker(doi):
            async with semaphore:
                # Add random delay between requests to appear more human
                await asyncio.sleep(random.uniform(0.5, 2.0))
                return await self._resolve_single_async(doi=doi)

        # Create tasks using the worker function
        tasks = [worker(doi) for doi in dois]
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
        if self.use_zenrows and hasattr(self.browser, "cleanup"):
            await self.browser.cleanup()
        elif hasattr(self.browser, "cleanup_authenticated_context"):
            await self.browser.cleanup_authenticated_context()


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


async def main():
    """Test the resolver with different articles."""
    from scitex import logging

    from ..auth import AuthenticationManager

    logging.basicConfig(level=logging.DEBUG)
    auth_manager = AuthenticationManager()
    resolver_url = "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"

    async with OpenURLResolver(auth_manager, resolver_url) as resolver:
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


if __name__ == "__main__":
    asyncio.run(main())

# EOF
