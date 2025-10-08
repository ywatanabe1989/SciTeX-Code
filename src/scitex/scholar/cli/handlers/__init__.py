#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: ./src/scitex/scholar/cli/handlers/__init__.py

"""CLI command handlers for Scholar.

Separation of concerns:
- Handlers contain business logic
- Handlers receive parsed args and Scholar instance
- No argument parsing logic in handlers
"""

from .bibtex_handler import handle_bibtex_operations
from .doi_handler import handle_doi_operations
from .project_handler import handle_project_operations

__all__ = [
    "handle_bibtex_operations",
    "handle_doi_operations",
    "handle_project_operations",
]

# EOF
