#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""URL utilities for Scholar.

Provides URL validation, normalization, and standardization functions.
"""

from typing import Optional
from urllib.parse import urlparse, urlunparse


def is_valid_url(url: Optional[str]) -> bool:
    """Check if URL is valid.

    Args:
        url: URL string to validate

    Returns:
        True if URL is valid and starts with http:// or https://

    Examples:
        >>> is_valid_url("https://doi.org/10.1038/nature12373")
        True
        >>> is_valid_url("10.1038/nature12373")
        False
        >>> is_valid_url(None)
        False
    """
    if not url:
        return False

    url_str = str(url).strip()

    # Must start with http:// or https://
    if not (url_str.startswith("https://") or url_str.startswith("http://")):
        return False

    # Basic URL parsing validation
    try:
        result = urlparse(url_str)
        # Must have scheme and netloc (domain)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def standardize_url(url: Optional[str]) -> Optional[str]:
    """Standardize URL format.

    - Ensures https:// scheme (upgrades http://)
    - Strips whitespace
    - Returns None for invalid URLs

    Args:
        url: URL string to standardize

    Returns:
        Standardized URL or None if invalid

    Examples:
        >>> standardize_url("http://doi.org/10.1038/nature12373")
        'https://doi.org/10.1038/nature12373'
        >>> standardize_url("  https://example.com  ")
        'https://example.com'
        >>> standardize_url("10.1038/nature12373")
        None
    """
    if not url:
        return None

    url_str = str(url).strip()

    # If no scheme, it's invalid
    if not (url_str.startswith("https://") or url_str.startswith("http://")):
        return None

    # Validate before standardizing
    if not is_valid_url(url_str):
        return None

    # Upgrade http:// to https://
    if url_str.startswith("http://"):
        url_str = "https://" + url_str[7:]

    return url_str


def standardize_doi_to_url(doi: Optional[str]) -> Optional[str]:
    """Convert DOI to standardized URL.

    Args:
        doi: DOI string (with or without https://doi.org/ prefix)

    Returns:
        Standardized DOI URL or None if invalid

    Examples:
        >>> standardize_doi_to_url("10.1038/nature12373")
        'https://doi.org/10.1038/nature12373'
        >>> standardize_doi_to_url("https://doi.org/10.1038/nature12373")
        'https://doi.org/10.1038/nature12373'
        >>> standardize_doi_to_url("http://dx.doi.org/10.1038/nature12373")
        'https://doi.org/10.1038/nature12373'
    """
    if not doi:
        return None

    doi_str = str(doi).strip()

    # If already a URL, validate and standardize
    if doi_str.startswith("http"):
        # Extract DOI from URL
        if "doi.org/" in doi_str or "dx.doi.org/" in doi_str:
            # Get the part after doi.org/
            doi_part = doi_str.split("doi.org/")[-1]
            return f"https://doi.org/{doi_part}"
        return standardize_url(doi_str)

    # If bare DOI (starts with 10.), add prefix
    if doi_str.startswith("10."):
        return f"https://doi.org/{doi_str}"

    return None


def get_best_url(
    openurl_resolved: Optional[list] = None,
    url_publisher: Optional[str] = None,
    url_doi: Optional[str] = None,
    doi: Optional[str] = None
) -> Optional[str]:
    """Get the best available URL from multiple sources.

    Priority:
    1. OpenURL resolved (institutional access)
    2. Publisher URL
    3. DOI URL
    4. DOI converted to URL

    All URLs are validated and standardized.

    Args:
        openurl_resolved: List of resolved OpenURL links
        url_publisher: Publisher URL
        url_doi: DOI URL
        doi: Bare DOI string

    Returns:
        Best available standardized URL or None

    Examples:
        >>> get_best_url(openurl_resolved=["https://example.edu/paper.pdf"])
        'https://example.edu/paper.pdf'
        >>> get_best_url(doi="10.1038/nature12373")
        'https://doi.org/10.1038/nature12373'
    """
    # Try OpenURL resolved first (institutional access)
    if openurl_resolved and len(openurl_resolved) > 0:
        for candidate in openurl_resolved:
            url = standardize_url(candidate)
            if url:
                return url

    # Try publisher URL
    if url_publisher:
        url = standardize_url(url_publisher)
        if url:
            return url

    # Try DOI URL
    if url_doi:
        url = standardize_url(url_doi)
        if url:
            return url

    # Try converting bare DOI to URL
    if doi:
        url = standardize_doi_to_url(doi)
        if url:
            return url

    return None


def extract_doi_from_url(url: Optional[str]) -> Optional[str]:
    """Extract bare DOI from URL.

    Args:
        url: URL that may contain a DOI

    Returns:
        Bare DOI string (e.g., "10.1038/nature12373") or None

    Examples:
        >>> extract_doi_from_url("https://doi.org/10.1038/nature12373")
        '10.1038/nature12373'
        >>> extract_doi_from_url("http://dx.doi.org/10.1038/nature12373")
        '10.1038/nature12373'
        >>> extract_doi_from_url("https://example.com")
        None
    """
    if not url:
        return None

    url_str = str(url).strip()

    # Check if URL contains doi.org
    if "doi.org/" in url_str:
        # Extract the part after doi.org/
        doi_part = url_str.split("doi.org/")[-1]

        # Remove any URL fragments or query parameters
        doi_part = doi_part.split("#")[0].split("?")[0]

        # Validate DOI format (starts with 10.)
        if doi_part.startswith("10."):
            return doi_part

    return None
