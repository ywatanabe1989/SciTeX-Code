#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 20:36:45 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/session/__init__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/session/__init__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Experiment session management for SciTeX.

This module provides session lifecycle management functionality that was previously
in scitex.session.start and scitex.session.close, now as a dedicated session management system.

Usage:
    # Session management (replaces scitex.session.start/close)
    import sys
    import matplotlib.pyplot as plt
    from scitex import session
    
    # Start a session
    CONFIG, sys.stdout, sys.stderr, plt, CC = session.start(sys, plt)
    
    # Your experiment code here
    
    # Close the session  
    session.close(CONFIG)

    # Session manager for advanced use cases
    manager = session.SessionManager()
    active_sessions = manager.get_active_sessions()
"""

# Import session management functionality
from ._manager import SessionManager
from ._lifecycle import start, close, running2finished

# Export public API
__all__ = [
    # Session lifecycle (main functions)
    'start',
    'close', 
    'running2finished',
    
    # Advanced session management
    'SessionManager',
]

# EOF