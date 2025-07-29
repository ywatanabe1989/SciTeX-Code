#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-30 07:27:05 (ywatanabe)"
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
from typing import List

"""OpenURL resolver for finding full-text access through institutional libraries.
Based on University of Melbourne library recommendation."""

import asyncio
import random
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import Page, TimeoutError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from ...errors import ScholarError
from ..browser import BrowserManager
from ._ResolverLinkFinder import ResolverLinkFinder

logger = logging.getLogger(__name__)


class OpenURLResolver:
    """Resolves DOIs to full-text URLs via institutional OpenURL resolver."""

    PUBLISHER_DOMAINS = {
        "sciencedirect.com",
        "linkinghub.elsevier.com",
        "nature.com",
        "springernature.com",
        "springer.com",
        "link.springer.com",
        "wiley.com",
        "onlinelibrary.wiley.com",
        "acs.org",
        "pubs.acs.org",
        "tandfonline.com",
        "sagepub.com",
        "journals.sagepub.com",
        "academic.oup.com",
        "oup.com",
        "science.org",
        "sciencemag.org",
        "pnas.org",
        "bmj.com",
        "cell.com",
        "ieeexplore.ieee.org",
        "ieee.org",
        "journals.plos.org",
        "plos.org",
        "frontiersin.org",
        "mdpi.com",
    }

    AUTH_BLACKLIST = {
        "openathens.net",
        "shibauth",
        "saml",
        "institutionlogin",
        "auth.elsevier.com",
        "go.gale.com",
        "login.",
        "auth.",
        "sso.",
        "iam.atypon.com",
    }

    # Fixme: not working
    # GIVEUP_LIST = {
    # }

    def __init__(self, auth_manager, resolver_url):
        self.auth_manager = auth_manager
        self.resolver_url = resolver_url
        self.browser = BrowserManager(auth_manager)
        self.timeout = 30
        self._link_finder = ResolverLinkFinder()

    def _build_openurl_from_doi(self, doi: str) -> str:
        """Build OpenURL query string from DOI only."""
        params = {
            "ctx_ver": "Z39.88-2004",
            "rft_val_fmt": "info:ofi/fmt:kev:mtx:journal",
            "rft.genre": "article",
            "rft.doi": doi,
        }
        query_string = urlencode(params, safe=":/")
        return f"{self.resolver_url}?{query_string}"

    def _is_publisher_url(self, url: str) -> bool:
        """Check if URL is final publisher destination."""
        if not url:
            return False

        url_lower = url.lower()

        if any(pattern in url_lower for pattern in self.AUTH_BLACKLIST):
            return False

        return any(domain in url_lower for domain in self.PUBLISHER_DOMAINS)

    def _should_give_up(self, url: str) -> bool:
        """Check if URL is in giveup list."""
        url_lower = url.lower()
        return any(pattern in url_lower for pattern in self.GIVEUP_LIST)

    async def _human_delay(self, min_ms: int = 500, max_ms: int = 2000):
        """Add random human-like delay."""
        delay = random.randint(min_ms, max_ms)
        await asyncio.sleep(delay / 1000)

    async def _check_no_access_page(self, page: Page) -> bool:
        """Check if page indicates no access available."""
        content = await page.content()
        no_access_phrases = [
            "No online text available",
            "No full text available",
            "No electronic access",
        ]
        return any(phrase in content for phrase in no_access_phrases)

    async def _handle_javascript_link(
        self, page: Page, link_url: str, openurl: str
    ) -> Dict[str, Any]:
        """Handle JavaScript popup links."""
        try:
            async with page.expect_popup(timeout=30000) as popup_info:
                await page.evaluate(link_url.replace("javascript:", ""))

            popup = await popup_info.value
            await popup.wait_for_load_state("domcontentloaded", timeout=30000)
            final_url = popup.url

            if any(
                domain in final_url
                for domain in ["openathens.net", "saml", "shibauth"]
            ):
                final_url = await self._follow_saml_redirect(popup, final_url)

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

    async def _handle_regular_link(
        self, page: Page, link_url: str, openurl: str, context
    ) -> Dict[str, Any]:
        """Handle regular navigation links."""
        try:
            new_page_promise = None

            def handle_page(new_page):
                nonlocal new_page_promise
                new_page_promise = new_page

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
                await target_page.close()
            else:
                final_url = page.url

            auth_domains = [
                "openathens.net",
                "saml",
                "shibauth",
                "institutionlogin",
            ]
            if any(domain in final_url.lower() for domain in auth_domains):
                final_url = await self._follow_saml_redirect(page, final_url)

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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((TimeoutError, PlaywrightError)),
    )
    async def _follow_saml_redirect(
        self, page: Page, saml_url: str, n_retry=5
    ) -> str:
        """Follow SAML/SSO redirect chain with human-like behavior."""
        logger.info(f"Following SAML redirect chain from: {saml_url}")

        await self._human_delay(1000, 3000)
        await page.goto(saml_url, wait_until="domcontentloaded", timeout=30000)

        for attempt in range(n_retry):
            await self._human_delay()

            current_url = page.url
            logger.debug(f"SAML attempt {attempt + 1}: {current_url}")

            if self._should_give_up(current_url):
                logger.warning(
                    f"Giving up - URL in giveup list: {current_url}"
                )
                return current_url

            if self._is_publisher_url(current_url):
                logger.info(f"Reached publisher URL: {current_url}")
                return current_url

            await page.mouse.move(
                random.randint(100, 800), random.randint(100, 600)
            )

            try:
                form_locator = page.locator("form[method='post']")
                if await form_locator.count() > 0:
                    await form_locator.first.evaluate("form => form.submit()")
                    await page.wait_for_load_state(
                        "domcontentloaded", timeout=20000
                    )
                    continue
            except Exception:
                pass

            try:
                forms = await page.query_selector_all("form")
                for form in forms:
                    if await form.is_visible():
                        await form.evaluate("form => form.submit()")
                        await page.wait_for_load_state(
                            "domcontentloaded", timeout=15000
                        )
                        break
            except:
                pass

            try:
                await page.wait_for_load_state("networkidle", timeout=8000)
            except:
                pass

            if page.url == current_url and attempt > 5:
                break

            await page.wait_for_timeout(2000)

        return page.url

    async def _resolve(self, doi: str) -> Optional[Dict[str, Any]]:
        """Internal resolve method for single DOI."""
        if not self.resolver_url:
            logger.warning("No OpenURL resolver URL configured")
            return None

        if not doi:
            logger.warning("DOI is required")
            return None

        browser, context = await self.browser.get_authenticated_context()
        page = await context.new_page()
        openurl = self._build_openurl_from_doi(doi)

        try:
            await page.goto(
                openurl, wait_until="domcontentloaded", timeout=30000
            )
            await page.wait_for_timeout(2000)

            current_url = page.url
            if self._is_publisher_url(current_url):
                return {
                    "final_url": current_url,
                    "resolver_url": openurl,
                    "access_type": "direct_redirect",
                    "success": True,
                }

            if await self._check_no_access_page(page):
                return {
                    "final_url": None,
                    "resolver_url": current_url,
                    "access_type": "no_access",
                    "success": False,
                }

            link_result = await self._link_finder.find_link(page, doi)
            if not link_result["success"]:
                return {
                    "final_url": None,
                    "resolver_url": current_url,
                    "access_type": "link_not_found",
                    "success": False,
                }

            link_url = link_result["url"]

            if link_url.startswith("javascript:"):
                return await self._handle_javascript_link(
                    page, link_url, openurl
                )
            else:
                return await self._handle_regular_link(
                    page, link_url, openurl, context
                )

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

    async def resolve(
        self, dois: Union[str, List[str]]
    ) -> Union[Optional[Dict[str, Any]], List[Optional[Dict[str, Any]]]]:
        """Resolve DOI(s) to full-text URLs."""
        if isinstance(dois, str):
            return await self._resolve(dois)

        if not dois:
            return []

        logger.info(f"Starting parallel resolution for {len(dois)} DOIs")
        tasks = [self._resolve(doi) for doi in dois]
        results = await asyncio.gather(*tasks)
        logger.info("Parallel resolution completed")
        return results

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
