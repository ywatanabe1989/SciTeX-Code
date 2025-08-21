#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 14:11:48 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/url/helpers/_ResolverLinkFinder.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/url/helpers/_ResolverLinkFinder.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Robust resolver link finder using a prioritized, multi-layered approach.

Priority order:
1. Link Target (domain matching) - Most reliable
2. Page Structure (CSS selectors) - Very reliable
3. Text Patterns - Good fallback
"""

import logging
import re
from typing import List, Optional
from urllib.parse import urlparse

from playwright.async_api import ElementHandle, Page

from scitex.scholar import ScholarConfig

logger = log.getLogger(__name__)


class ResolverLinkFinder:
    """
    Finds full-text links on resolver pages using multiple strategies.
    """

    # DOI prefix to publisher domain mapping
    DOI_TO_DOMAIN = {
        "10.1038": [
            "nature.com",
            "springernature.com",
        ],  # Nature Publishing Group
        "10.1016": ["sciencedirect.com", "elsevier.com"],  # Elsevier
        "10.1002": ["wiley.com", "onlinelibrary.wiley.com"],  # Wiley
        "10.1007": ["springer.com", "link.springer.com"],  # Springer
        "10.1126": ["science.org", "sciencemag.org"],  # Science/AAAS
        "10.1021": ["acs.org", "pubs.acs.org"],  # ACS Publications
        "10.1111": [
            "wiley.com",
            "onlinelibrary.wiley.com",
        ],  # Wiley (alternative)
        "10.1080": ["tandfonline.com"],  # Taylor & Francis
        "10.1177": ["sagepub.com", "journals.sagepub.com"],  # SAGE
        "10.1093": ["oup.com", "academic.oup.com"],  # Oxford
        "10.1109": ["ieee.org", "ieeexplore.ieee.org"],  # IEEE
        "10.1371": ["plos.org", "journals.plos.org"],  # PLOS
        "10.1073": ["pnas.org"],  # PNAS
        "10.1136": ["bmj.com"],  # BMJ
        "10.3389": ["frontiersin.org"],  # Frontiers
        "10.3390": ["mdpi.com"],  # MDPI
    }

    def __init__(
        self,
        structure_selectors: List[str] = None,
        text_patterns: List[str] = None,
        negative_keywords: List[str] = None,
        config: ScholarConfig = None,
    ):
        self.config = config or ScholarConfig()
        self.structure_selectors = self.config.resolve(
            "structure_selectors", structure_selectors
        )
        self.text_patterns = self.config.resolve(
            "text_patterns", text_patterns
        )
        self.negative_keywords = self.config.resolve(
            "negative_keywords", negative_keywords
        )
        self._doi_pattern = re.compile(r"10\.\d{4,}/[-._;()/:\w]+")

    def get_expected_domains(self, doi: str) -> List[str]:
        """Get expected publisher domains for a DOI."""
        # Extract DOI prefix
        match = re.match(r"(10\.\d{4,})", doi)
        if not match:
            return []

        prefix = match.group(1)
        return self.DOI_TO_DOMAIN.get(prefix, [])

    async def find_link(self, page: Page, doi: str) -> Optional[ElementHandle]:
        """
        Find the best full-text link using prioritized strategies.

        Args:
            page: Playwright page object
            doi: Target DOI

        Returns:
            ElementHandle of the best link, or None
        """
        logger.info(f"Finding resolver link for DOI: {doi}")

        # Strategy 1: Link Target (Most Reliable)
        link = await self._find_by_domain(page, doi)
        if link:
            logger.success("Found link using domain matching (Strategy 1)")
            return link
        else:
            logger.info(
                "Could not find resolver link with domain matching strategy"
            )

        # Strategy 2: Page Structure (Very Reliable)
        link = await self._find_by_structure(page)
        if link:
            logger.success("Found link using page structure (Strategy 2)")
            return link
        else:
            logger.info(
                "Could not find resolver link with page structure strategy"
            )

        # Strategy 3: Text Patterns (Fallback)
        link = await self._find_by_text(page)
        if link:
            logger.success("Found link using text patterns (Strategy 3)")
            return link
        else:
            logger.info(
                "Could not find resolver link with text pattern strategy"
            )

        return None

    async def _find_by_domain(
        self, page: Page, doi: str
    ) -> Optional[ElementHandle]:
        """Strategy 1: Find link by expected publisher domain."""
        expected_domains = self.get_expected_domains(doi)
        if not expected_domains:
            logger.debug(f"No known publisher domains for DOI prefix: {doi}")
            return None

        logger.debug(f"Looking for links to domains: {expected_domains}")

        # Get all links (including JavaScript links)
        all_links = await page.query_selector_all("a")

        for link in all_links:
            href = await link.get_attribute("href")
            text = await link.inner_text() or ""

            # Check for SFX JavaScript links that mention publisher names
            if href and href.startswith("javascript:"):
                # Check text for publisher names
                text_lower = text.lower()
                if "10.1038" in doi and (
                    "nature" in text_lower or "springer" in text_lower
                ):
                    if (
                        "nature.com" in text_lower
                        or "fully open" in text_lower
                    ):
                        logger.info(f"Found SFX Nature link: {text[:50]}")
                        return link
                elif "10.1016" in doi and (
                    "elsevier" in text_lower or "sciencedirect" in text_lower
                ):
                    logger.info(f"Found SFX Elsevier link: {text[:50]}")
                    return link
            elif href:
                # Parse domain from regular href
                try:
                    parsed = urlparse(href)
                    domain = parsed.netloc.lower()

                    # Check if domain matches any expected domain
                    for expected in expected_domains:
                        if expected in domain:
                            logger.info(
                                f"Found domain match: {domain} (text: '{text[:50]}')"
                            )

                            # Verify it's not an abstract/preview link
                            if not any(
                                bad in text.lower()
                                for bad in ["abstract", "preview", "summary"]
                            ):
                                return link
                            else:
                                logger.debug(
                                    f"Skipping abstract/preview link: {text}"
                                )

                except Exception as e:
                    logger.debug(f"Error parsing URL {href}: {e}")

        return None

    async def _find_by_structure(self, page: Page) -> Optional[ElementHandle]:
        """Strategy 2: Find link by page structure."""
        structure_selectors = self.config.resolve(
            "structure_selectors",
            default=[
                "div#fulltext a",
                "div.sfx-fulltext a",
                "div.results-title > a",
            ],
        )

        for selector in structure_selectors:
            try:
                elements = await page.query_selector_all(selector)
                if elements:
                    for element in elements:
                        if await element.is_visible():
                            href = await element.get_attribute("href")
                            if href and href.strip():
                                return element
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
        return None

    async def _find_by_text(self, page: Page) -> Optional[ElementHandle]:
        """Strategy 3: Find link by text patterns."""
        text_patterns = self.config.resolve(
            "text_patterns", default=["View full text at", "Full Text", "PDF"]
        )

        for pattern in text_patterns:
            try:
                selector = f'a:has-text("{pattern}")'
                link = await page.query_selector(selector)
                if link and await link.is_visible():
                    href = await link.get_attribute("href")
                    if href and href.strip():
                        return link
            except Exception as e:
                logger.debug(f"Error with text pattern '{pattern}': {e}")
        return None

    async def click_and_wait(self, page: Page, link: ElementHandle) -> bool:
        """
        Click link and wait for navigation.

        Returns True if navigation succeeded.
        """
        initial_url = page.url

        try:
            # Get link info for logging
            href = await link.get_attribute("href") or ""
            text = await link.inner_text() or ""
            logger.info(f"Clicking link: '{text[:50]}' -> {href[:100]}")

            # Click and wait for navigation
            await link.click()

            # Wait for either navigation or network idle
            try:
                await page.wait_for_load_state("networkidle", timeout=30000)
            except:
                # Fallback to domcontentloaded if network doesn't settle
                await page.wait_for_load_state(
                    "domcontentloaded", timeout=30000
                )

            # Additional wait for JavaScript redirects
            await page.wait_for_timeout(3000)

            # Check if we navigated
            final_url = page.url
            if final_url != initial_url:
                logger.info(
                    f"Successfully navigated: {initial_url} -> {final_url}"
                )
                return True
            else:
                logger.warning("No navigation occurred after click")
                return False

        except Exception as e:
            logger.error(f"Error during click and navigation: {e}")
            return False


# Convenience function for integration
async def find_and_click_resolver_link(page: Page, doi: str) -> Optional[str]:
    """
    Find and click the best resolver link.

    Args:
        page: Playwright page object
        doi: Target DOI

    Returns:
        Final URL after navigation, or None if failed
    """
    finder = ResolverLinkFinder()

    # Find link
    link = await finder.find_link(page, doi)
    if not link:
        return None

    # Click and navigate
    success = await finder.click_and_wait(page, link)
    if success:
        return page.url
    else:
        return None

# EOF
