#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-15 00:55:30 (ywatanabe)"
# File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/path/_clean.py

import os

def clean(path_string):
    """Cleans and normalizes a file system path string.

    Example
    -------
    >>> clean('/home/user/./folder/../file.txt')
    '/home/user/file.txt'
    >>> clean('path/./to//file.txt')
    'path/to/file.txt'
    >>> clean('path with spaces')
    'path_with_spaces'

    Parameters
    ----------
    path_string : str
        File path to clean

    Returns
    -------
    str
        Normalized path string
    """
    if not path_string:
        return ""
    
    # Remember if path ends with a slash (indicating a directory)
    is_directory = path_string.endswith("/")
    
    # Replace spaces with underscores
    path_string = path_string.replace(" ", "_")
    
    # Use normpath to handle ../ and ./ references
    cleaned_path = os.path.normpath(path_string)
    
    # Replace multiple slashes with single slash
    while "//" in cleaned_path:
        cleaned_path = cleaned_path.replace("//", "/")
        
    # Restore trailing slash if it was a directory
    if is_directory and not cleaned_path.endswith("/"):
        cleaned_path += "/"
        
    return cleaned_path

# EOF
