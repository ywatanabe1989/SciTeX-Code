#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-22 17:05:52 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/gen/_deprecated_close.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Deprecated wrapper for the old scitex.gen.close function.

This module provides backward compatibility by forwarding calls to the new
scitex.session.close function while showing deprecation warnings.
"""

from ..decorators._deprecated import deprecated


@deprecated(
    "Use scitex.session.close instead. The old interface will be removed in a future version."
)
def close(*args, **kwargs):
    """Deprecated close function - use scitex.session.close instead.

    This function provides backward compatibility for existing code that uses
    scitex.gen.close(). It forwards all calls to the new scitex.session.close()
    function while displaying a deprecation warning.

    Parameters
    ----------
    *args : tuple
        Positional arguments passed to scitex.session.close()
    **kwargs : dict
        Keyword arguments passed to scitex.session.close()

    Returns
    -------
    Any
        Same return value as scitex.session.close()
    """
    # Import here to avoid circular dependencies
    from ..session import close as session_close

    return session_close(*args, **kwargs)


@deprecated(
    "Use scitex.session.running2finished instead. The old interface will be removed in a future version."
)
def running2finished(*args, **kwargs):
    """Deprecated running2finished function - use scitex.session.running2finished instead.

    This function provides backward compatibility for existing code that uses
    scitex.gen.running2finished(). It forwards all calls to the new
    scitex.session.running2finished() function while displaying a deprecation warning.

    Parameters
    ----------
    *args : tuple
        Positional arguments passed to scitex.session.running2finished()
    **kwargs : dict
        Keyword arguments passed to scitex.session.running2finished()

    Returns
    -------
    Any
        Same return value as scitex.session.running2finished()
    """
    # Import here to avoid circular dependencies
    from ..session import running2finished as session_running2finished

    return session_running2finished(*args, **kwargs)


__all__ = ["close", "running2finished"]

# EOF
