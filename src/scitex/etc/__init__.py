#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-09 08:45:00 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/scitex_repo/src/scitex/etc/__init__.py

"""
Utility functions for miscellaneous tasks.

This module provides utility functions that don't fit into other categories,
such as keyboard input handling for interactive programs.
"""

from .wait_key import wait_key, count

__all__ = ["wait_key", "count"]