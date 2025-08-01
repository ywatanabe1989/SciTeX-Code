#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-31 00:53:24 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/open_url/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/open_url/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from ._OpenURLResolver import OpenURLResolver
from ._OpenURLResolverWithZenRows import OpenURLResolverWithZenRows
from ._ZenRowsOpenURLResolver import ZenRowsOpenURLResolver
from ._ResumableOpenURLResolver import ResumableOpenURLResolver
from ._MultiInstitutionalResolver import MultiInstitutionalResolver, create_resolver
from ._DOIToURLResolver import DOIToURLResolver
from .KNOWN_RESOLVERS import (
    KNOWN_RESOLVERS,
    get_resolver_by_institution,
    get_resolvers_by_country,
    get_resolvers_by_vendor,
    validate_resolver_url,
    TEST_DOIS
)

__all__ = [
    "OpenURLResolver",
    "OpenURLResolverWithZenRows",  # API-based ZenRows integration
    "ZenRowsOpenURLResolver",       # Browser-based ZenRows integration
    "ResumableOpenURLResolver",     # Resumable resolver with progress tracking
    "MultiInstitutionalResolver",   # Multi-institutional support
    "DOIToURLResolver",             # DOI to URL resolver (Task #5)
    "create_resolver",              # Convenience function
    "KNOWN_RESOLVERS",              # Known resolver database
    "get_resolver_by_institution",  # Lookup functions
    "get_resolvers_by_country",
    "get_resolvers_by_vendor",
    "validate_resolver_url",
    "TEST_DOIS",
]

# EOF
