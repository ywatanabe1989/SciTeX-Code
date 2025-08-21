#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-07 15:13:41 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/sso_automations/_SSOAutomator.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/auth/sso_automations/_SSOAutomator.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Factory for creating SSO automators."""

from typing import Dict, Optional

from scitex import log

from scitex.scholar.config import ScholarConfig
from ._BaseSSOAutomator import BaseSSOAutomator

logger = log.getLogger(__name__)


class SSOAutomator:
    """Factory for creating institution-specific SSO automators."""

    # Email domain mappings
    EMAIL_DOMAIN_MAP = {
        "@unimelb.edu.au": "UniversityOfMelbourne",
        "@student.unimelb.edu.au": "UniversityOfMelbourne",
    }

    # URL pattern mappings
    URL_PATTERN_MAP = {
        "unimelb": "UniversityOfMelbourne",
        "melbourne.edu.au": "UniversityOfMelbourne",
        "exlibrisgroup.com/sfxlcl41": "UniversityOfMelbourne",
    }

    # Institution name mappings
    INSTITUTION_NAME_MAP = {
        "unimelb": "UniversityOfMelbourne",
        "university of melbourne": "UniversityOfMelbourne",
        "melbourne": "UniversityOfMelbourne",
        "melbourne university": "UniversityOfMelbourne",
    }

    # Automator class mappings
    AUTOMATOR_CLASS_MAP = {
        "UniversityOfMelbourne": "_UniversityOfMelbourneSSOAutomator.UniversityOfMelbourneSSOAutomator",
    }

    def __new__(cls, institution=None, email=None, url=None, **kwargs):
        if institution:
            return cls.create_by_name(institution, **kwargs)
        elif email:
            return cls.create_from_email(email, **kwargs)
        elif url:
            return cls.create_from_url(url, **kwargs)
        else:
            return None

    @classmethod
    def create_from_email(
        cls, email: str, **kwargs
    ) -> Optional[BaseSSOAutomator]:
        """Create SSO automator based on email domain."""
        if not email:
            return None

        email_lower = email.lower()

        for domain, automator_name in cls.EMAIL_DOMAIN_MAP.items():
            if email_lower.endswith(domain):
                return cls._create_automator(automator_name, **kwargs)

        logger.debug(f"No SSO automator found for email: {email}")
        return None

    @classmethod
    def create_from_url(cls, url: str, **kwargs) -> Optional[BaseSSOAutomator]:
        """Auto-detect institution from URL and create appropriate automator."""
        url_lower = url.lower()

        for pattern, automator_name in cls.URL_PATTERN_MAP.items():
            if pattern in url_lower:
                logger.info(
                    f"Detected {automator_name.replace('Of', ' of ')} from URL"
                )
                return cls._create_automator(automator_name, **kwargs)

        logger.debug(f"No SSO automator found for URL: {url}")
        return None

    @classmethod
    def create_by_name(
        cls, institution_name: str, **kwargs
    ) -> Optional[BaseSSOAutomator]:
        """Create SSO automator by institution name."""
        name_lower = institution_name.lower()

        for key, automator_name in cls.INSTITUTION_NAME_MAP.items():
            if key in name_lower:
                return cls._create_automator(automator_name, **kwargs)

        logger.warn(
            f"No SSO automator found for institution: {institution_name}"
        )
        return None

    @classmethod
    def _create_automator(
        cls, automator_name: str, **kwargs
    ) -> Optional[BaseSSOAutomator]:
        """Create automator instance by name."""
        if automator_name not in cls.AUTOMATOR_CLASS_MAP:
            logger.error(f"Unknown automator: {automator_name}")
            return None

        try:
            module_path, class_name = cls.AUTOMATOR_CLASS_MAP[
                automator_name
            ].rsplit(".", 1)
            from importlib import import_module

            module = import_module(f".{module_path}", package=__package__)
            automator_class = getattr(module, class_name)
            return automator_class(**kwargs)
        except ImportError as e:
            logger.error(f"Failed to import automator {automator_name}: {e}")
            return None

    @classmethod
    def list_supported_institutions(cls) -> Dict[str, str]:
        """Get list of supported institutions."""
        return {
            "unimelb": "University of Melbourne",
        }


if __name__ == "__main__":
    import asyncio

    def main():
        """Test UniMelb SSO automator."""
        from playwright.async_api import async_playwright

        from scitex.scholar.auth.sso_automation._SSOAutomator import (
            SSOAutomator,
        )

        automator = SSOAutomator(email=os.getenv("SCITEX_SCHOLAR_SSO_EMAIL"))

        async def test_automator():
            # automator = UniversityOfMelbourneSSOAutomator()
            automator = SSOAutomator(
                email=os.getenv("SCITEX_SCHOLAR_SSO_EMAIL")
            )

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                page = await browser.new_page()

                try:
                    await page.goto("https://sso.unimelb.edu.au/")
                    success = await automator.perform_login_async(page)
                    print(f"Login success: {success}")

                    await page.wait_for_timeout(5000)
                except Exception as e:
                    print(f"Error: {e}")
                finally:
                    await browser.close()

        asyncio.run(test_automator())

    main()


# python -m scitex.scholar.auth.sso_automation._SSOAutomator

# EOF
