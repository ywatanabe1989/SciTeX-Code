#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/auth/gateway/__init__.py
# ----------------------------------------
"""
Authentication Gateway Module

This module contains authentication gateway components that handle
authentication mechanisms to access content behind paywalls and SSO systems.

Components:
- OpenURLResolver: Resolves DOIs through OpenURL resolvers
- OpenURLLinkFinder: Finds publisher links on resolver pages
- resolve_functions: Utility functions for URL resolution

These were moved from url/helpers/resolvers as they are authentication
mechanisms rather than URL discovery mechanisms.
"""

from ._OpenURLResolver import OpenURLResolver
from ._OpenURLLinkFinder import OpenURLLinkFinder
from ._resolve_functions import (
    normalize_doi_as_http,
    resolve_publisher_url_by_navigating_to_doi_page,
    extract_doi_from_url,
    resolve_openurl,
)

__all__ = [
    "OpenURLResolver",
    "OpenURLLinkFinder",
    "normalize_doi_as_http",
    "resolve_publisher_url_by_navigating_to_doi_page",
    "extract_doi_from_url",
    "resolve_openurl",
]

# EOF
