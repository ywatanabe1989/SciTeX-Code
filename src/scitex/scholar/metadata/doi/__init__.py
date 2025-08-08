#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-05 17:00:26 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/doi/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/doi/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""DOI resolution module for Scholar.

The primary interface is the unified DOIResolver which automatically
handles different input types (single DOI, DOI list, BibTeX file/content).

For advanced use cases, specific resolvers are also available:
- BatchDOIResolver: For batch processing with advanced configuration
- BibTeXDOIResolver: For specialized BibTeX handling
"""

# Primary unified interface (recommended for most users)
from ._DOIResolver import DOIResolver

# # Specific resolvers for advanced use cases
# from ._BatchDOIResolver import BatchDOIResolver
# from ._BibTeXDOIResolver import BibTeXDOIResolver

__all__ = [
    "DOIResolver",         # Unified resolver (primary interface)
    # "BatchDOIResolver",    # Advanced batch processing
    # "BibTeXDOIResolver",   # Specialized BibTeX handling
]

# EOF

# BatchDOIResolver -> BatchBatchDOIResolver
# DOIResolver -> BatchDOIResolver
