#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-03 11:20:00 (ywatanabe)"
# File: ./mcp_servers/scitex-project-validator/__init__.py
# ----------------------------------------

"""SciTeX Project Validator MCP Server

This package provides MCP tools for validating SciTeX project structures
for both individual scientific projects and pip packages.
"""

from .server import ScitexProjectValidatorServer

__version__ = "1.0.0"
__all__ = ["ScitexProjectValidatorServer"]

# EOF