#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-29 03:07:16 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/open_url/_OpenURLResolver.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/open_url/_OpenURLResolver.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import logging

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

    def __init__(self, auth_manager, resolver_url):
        """Initialize OpenURL resolver.

        Args:
            auth_manager: Authentication manager for institutional access
            resolver_url: Base URL of institutional OpenURL resolver
                         (Details can be seen at https://www.zotero.org/openurl_resolvers)
        """
        self.auth_manager = auth_manager
        self.resolver_url = resolver_url
        self.browser = BrowserManager(auth_manager)
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

        # Exclude intermediate authentication URLs
        auth_patterns = [
            "openathens.net",
            "shibauth",
            "saml",
            "institutionlogin",
            "iam.atypon.com",
            "auth.elsevier.com",
            "go.gale.com/ps/headerQuickSearch",
        ]

        if any(pattern in url.lower() for pattern in auth_patterns):
            return False

        # Check for publisher domains
        publisher_domains = [
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

        return any(domain in url.lower() for domain in publisher_domains)

    async def _follow_saml_redirect(self, page, saml_url, doi=""):
        """Follow SAML/SSO redirect chain until publisher URL is reached."""
        logger.info(f"Following SAML redirect chain starting from: {saml_url}")

        await page.goto(saml_url, wait_until="domcontentloaded", timeout=30000)

        for attempt in range(15):
            current_url = page.url
            logger.debug(f"SAML redirect attempt {attempt + 1}: {current_url}")

            # Check if we've reached publisher destination
            if self._is_publisher_url(current_url, doi):
                logger.info(
                    f"Successfully navigated to publisher URL: {current_url}"
                )
                return current_url

            # Handle SAML POST forms
            try:
                form_locator = page.locator("form[method='post']")
                if await form_locator.count() > 0:
                    logger.debug("Found POST form, submitting...")
                    await form_locator.first.evaluate("form => form.submit()")
                    await page.wait_for_load_state(
                        "domcontentloaded", timeout=20000
                    )
                    continue
            except Exception as form_error:
                logger.debug(f"Form submission failed: {form_error}")

            # Handle any visible forms
            try:
                forms = await page.query_selector_all("form")
                for form in forms:
                    if await form.is_visible():
                        logger.debug("Submitting visible form...")
                        await form.evaluate("form => form.submit()")
                        await page.wait_for_load_state(
                            "domcontentloaded", timeout=15000
                        )
                        break
            except:
                pass

            # Wait for network to settle
            try:
                await page.wait_for_load_state("networkidle", timeout=5000)
            except:
                logger.debug("Network did not settle, proceeding")

            # Check if URL changed, break if stuck
            if page.url == current_url:
                logger.warning(
                    f"URL unchanged, may be stuck at: {current_url}"
                )
                break

            await page.wait_for_timeout(2000)

        final_url = page.url
        logger.info(f"SAML redirect completed at: {final_url}")
        return final_url

    async def resolve_async(
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

        if not self.resolver_url:
            logger.warning("No OpenURL resolver URL configured")
            return None
        if not doi:
            logger.warning("DOI is required for reliable resolution")

        browser, context = await self.browser.get_authenticated_context()
        page = await context.new_page()

        openurl = self.build_openurl(
            title, authors, journal, year, volume, issue, pages, doi, pmid
        )
        logger.info(f"Resolving via OpenURL: {openurl}")

        try:
            logger.info("Navigating to OpenURL resolver...")
            await page.goto(
                openurl, wait_until="domcontentloaded", timeout=30000
            )
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
                logger.info("Resolver indicates no access available")
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
            await page.close()

    def resolve(
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
        """Synchronous wrapper for resolve_async."""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(
                self.resolve_async(
                    title,
                    authors,
                    journal,
                    year,
                    volume,
                    issue,
                    pages,
                    doi,
                    pmid,
                )
            )
        finally:
            loop.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
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
        result = await resolver.resolve_async(
            title, authors, journal, year, volume, issue, pages, doi, pmid
        )
        if result and result.get("success") and result.get("final_url"):
            return result["final_url"]
    return None


async def main():
    """Test the resolver with different articles."""
    import logging

    from ..auth import AuthenticationManager

    logging.basicConfig(level=logging.DEBUG)
    auth_manager = AuthenticationManager()
    resolver_url = "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"

    async with OpenURLResolver(auth_manager, resolver_url) as resolver:
        print("\n=== Test 1: Article with access ===")
        result = await resolver.resolve_async(
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
        result = await resolver.resolve_async(
            doi="10.1038/s41593-025-01990-7",
            title="Addressing artifactual bias in large, automated MRI analyses of brain development",
            journal="Nature Neuroscience",
            year=2025,
        )
        print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())

# EOF
