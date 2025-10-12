#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Publisher-specific PDF extraction rules using central config."""

import re
from typing import Dict, List

from scitex import logging
from scitex.scholar.config import ScholarConfig

logger = logging.getLogger(__name__)


class PublisherRules:
    """Access publisher-specific PDF extraction rules from config."""

    def __init__(self, config: ScholarConfig = None):
        self.name = self.__class__.__name__
        self.config = config or ScholarConfig()

    def get_config_for_url(self, url: str) -> Dict:
        """Get publisher-specific config for a URL."""
        url_lower = url.lower()
        publisher_rules = self.config.get("publisher_pdf_rules") or {}

        for publisher_name, rules in publisher_rules.items():
            domain_patterns = rules.get("domain_patterns", [])
            for pattern in domain_patterns:
                if pattern in url_lower:
                    return rules

        return {}

    def merge_with_config(
        self,
        url: str,
        base_deny_selectors: List[str] = None,
        base_deny_classes: List[str] = None,
        base_deny_text_patterns: List[str] = None,
    ) -> Dict:
        """Merge publisher-specific config with base deny patterns."""
        publisher_config = self.get_config_for_url(url)

        merged = {
            "deny_selectors": list(base_deny_selectors or []),
            "deny_classes": list(base_deny_classes or []),
            "deny_text_patterns": list(base_deny_text_patterns or []),
            "download_selectors": publisher_config.get("download_selectors", []),
            "allowed_pdf_patterns": publisher_config.get("allowed_pdf_patterns", []),
        }

        merged["deny_selectors"].extend(publisher_config.get("deny_selectors", []))
        merged["deny_classes"].extend(publisher_config.get("deny_classes", []))
        merged["deny_text_patterns"].extend(
            publisher_config.get("deny_text_patterns", [])
        )

        # Remove duplicates while preserving order
        for key in ["deny_selectors", "deny_classes", "deny_text_patterns"]:
            seen = set()
            unique = []
            for item in merged[key]:
                if item not in seen:
                    seen.add(item)
                    unique.append(item)
            merged[key] = unique

        return merged

    def is_valid_pdf_url(self, page_url: str, pdf_url: str) -> bool:
        """Check if PDF URL is valid based on publisher rules."""
        config = self.get_config_for_url(page_url)
        allowed_patterns = config.get("allowed_pdf_patterns", [])

        if not allowed_patterns:
            return pdf_url.endswith(".pdf") or "/pdf/" in pdf_url

        for pattern in allowed_patterns:
            if re.search(pattern, pdf_url):
                return True

        return False

    def filter_pdf_urls(self, page_url: str, pdf_urls: List[str]) -> List[str]:
        """Filter PDF URLs based on publisher-specific rules."""
        config = self.get_config_for_url(page_url)

        # ScienceDirect-specific: extract current article's PII
        current_pii = None
        if any(
            domain in page_url.lower()
            for domain in ["sciencedirect.com", "cell.com", "elsevier.com"]
        ):
            pii_match = re.search(r"/pii/([A-Z0-9]+)", page_url)
            if pii_match:
                current_pii = pii_match.group(1)

        filtered_urls = []
        for pdf_url in pdf_urls:
            should_deny = False

            # Check deny text patterns
            for pattern in config.get("deny_text_patterns", []):
                if pattern.lower() in pdf_url.lower():
                    should_deny = True
                    break

            # ScienceDirect: only allow PDFs matching current PII
            if current_pii:
                if current_pii not in pdf_url:
                    should_deny = True
                pdf_pii_match = re.search(r"pid=1-s2\.0-([A-Z0-9]+)-", pdf_url)
                if pdf_pii_match:
                    pdf_pii = pdf_pii_match.group(1)
                    if pdf_pii != current_pii:
                        should_deny = True

            if not should_deny and self.is_valid_pdf_url(page_url, pdf_url):
                filtered_urls.append(pdf_url)

        # Remove duplicates
        seen = set()
        unique_urls = []
        for url in filtered_urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)

        return unique_urls


# EOF
