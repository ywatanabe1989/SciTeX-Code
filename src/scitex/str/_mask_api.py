#!./env/bin/python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-06-10 20:48:53 (ywatanabe)"
# /home/ywatanabe/proj/scitex/src/scitex/gen/_mask_api_key.py


def mask_api(api_key, n=4):
    """Mask an API key for secure display.

    Replaces the middle portion of an API key with asterisks, keeping only
    the first and last few characters visible. Useful for logging or displaying
    API keys without exposing the full key.

    Parameters
    ----------
    api_key : str
        The API key to mask.
    n : int, optional
        Number of characters to show at the beginning and end. Default is 4.

    Returns
    -------
    str
        Masked API key with format "{first_n}****{last_n}"

    Examples
    --------
    >>> key = "sk-1234567890abcdefghijklmnop"
    >>> print(mask_api(key))
    'sk-1****mnop'

    >>> print(mask_api(key, n=6))
    'sk-123****lmnop'

    >>> # Safe for logging
    >>> print(f"Using API key: {mask_api(api_key)}")
    'Using API key: sk-p****5678'
    """
    return f"{api_key[:n]}****{api_key[-n:]}"
