#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-05 07:35:30 (ywatanabe)"
# File: ./scitex_repo/src/scitex/pd/_ignore_.py

import warnings
from contextlib import contextmanager


@contextmanager
def ignore_setting_with_copy_warning():
    """
    Context manager to temporarily ignore pandas SettingWithCopyWarning.

    Example
    -------
    >>> with ignore_SettingWithCopyWarning():
    ...     df['column'] = new_values  # No warning will be shown
    """
    try:
        from pandas.errors import SettingWithCopyWarning
    except ImportError:
        from pandas.core.common import SettingWithCopyWarning

    # Save current warning filters
    with warnings.catch_warnings():
        warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)
        yield


# Backward compatibility
ignore_SettingWithCopyWarning = ignore_setting_with_copy_warning  # Deprecated

# EOF
