#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-02 19:45:32 (ywatanabe)"
# File: ./scitex_repo/src/scitex/path/_increment_version.py

import os
import re
from glob import glob


def increment_version(dirname, fname, ext, version_prefix="_v"):
    """
    Generate the next version of a filename based on existing versioned files.

    This function searches for files in the given directory that match the pattern:
    {fname}{version_prefix}{number}{ext} and returns the path for the next version.

    Parameters:
    -----------
    dirname : str
        The directory to search in and where the new file will be created.
    fname : str
        The base filename without version number or extension.
    ext : str
        The file extension, including the dot (e.g., '.txt').
    version_prefix : str, optional
        The prefix used before the version number. Default is '_v'.

    Returns:
    --------
    str
        The full path for the next version of the file.

    Example:
    --------
    >>> increment_version('/path/to/dir', 'myfile', '.txt')
    '/path/to/dir/myfile_v004.txt'

    Notes:
    ------
    - If no existing versioned files are found, it starts with version 001.
    - The version number is always formatted with at least 3 digits.
    """
    # Create a regex pattern to match the version number in the filename
    version_pattern = re.compile(
        rf"({re.escape(fname)}{re.escape(version_prefix)})(\d+)({re.escape(ext)})$"
    )

    # Construct the glob pattern to find all files that match the pattern
    glob_pattern = os.path.join(dirname, f"{fname}{version_prefix}*{ext}")

    # Use glob to find all files that match the pattern
    files = glob(glob_pattern)

    # Initialize the highest version number
    highest_version = 0
    base, suffix = None, None

    # Loop through the files to find the highest version number
    for file in files:
        filename = os.path.basename(file)
        match = version_pattern.search(filename)
        if match:
            base, version_str, suffix = match.groups()
            version_num = int(version_str)
            if version_num > highest_version:
                highest_version = version_num

    # If no versioned files were found, use the provided filename and extension
    if base is None or suffix is None:
        base = f"{fname}{version_prefix}"
        suffix = ext
        highest_version = 0  # No previous versions

    # Increment the highest version number
    next_version_number = highest_version + 1

    # Format the next version number with the same number of digits as the original
    next_version_str = f"{base}{next_version_number:03d}{suffix}"

    # Combine the directory and new filename to create the full path
    next_filepath = os.path.join(dirname, next_version_str)

    return next_filepath


# EOF
