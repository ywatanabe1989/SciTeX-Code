#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-15 09:27:36 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/io/_load_modules/_txt.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/io/_load_modules/_txt.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import warnings

# # UnicodeDecodeError: 'utf-8' codec can't decode byte 0x8a in position 30173: invalid start byte
# def _load_txt(lpath, **kwargs):
#     """Load text file and return non-empty lines."""
#     SUPPORTED_EXTENSIONS = (".txt", ".log", ".event", ".py", ".sh", "")
#     try:
#         if not lpath.endswith(SUPPORTED_EXTENSIONS):
#             warnings.warn(
#                 f"File must have supported extensions: {SUPPORTED_EXTENSIONS}"
#             )

#         # Try UTF-8 first (most common)
#         try:
#             with open(lpath, "r", encoding="utf-8") as f:
#                 return [
#                     line.strip()
#                     for line in f.read().splitlines()
#                     if line.strip()
#                 ]
#         except UnicodeDecodeError:
#             # Fallback to system default encoding
#             with open(lpath, "r") as f:
#                 return [
#                     line.strip()
#                     for line in f.read().splitlines()
#                     if line.strip()
#                 ]


#     except (ValueError, FileNotFoundError) as e:
#         raise ValueError(f"Error loading file {lpath}: {str(e)}")
# Removed duplicate function - see main _load_txt below


# def _load_txt(lpath, strip=False, as_lines=False):
#     """
#     Load text file and return its content.
#     - Warn if extension is unexpected.
#     - Try UTF-8 first, then default encoding.
#     - If strip=True, strip whitespace.
#     - If as_lines=True, return list of lines (backward compatibility).
#     """
#     if not lpath.endswith((".txt", ".log", ".event", ".py", ".sh")):
#         warnings.warn(f"Unexpected extension for file: {lpath}")

#     try:
#         with open(lpath, "r", encoding="utf-8") as file:
#             content = file.read()
#     except UnicodeDecodeError:
#         # Fallback: try to detect correct encoding
#         encoding = _check_encoding(lpath)
#         with open(lpath, "r", encoding=encoding) as file:
#             content = file.read()

#     # For backward compatibility, check if as_lines parameter or legacy behavior needed
#     if as_lines:
#         raw_lines = content.splitlines()
#         if strip:
#             return [line.strip() for line in raw_lines if line.strip()]
#         return [line for line in raw_lines if line.strip()]

#     # Default: return full content (possibly stripped)
#     if strip:
#         return content.strip()

#     return content


def _load_txt(lpath, strip=True, as_lines=True):
    """
    Load text file and return its content.
    - Warn if extension is unexpected.
    - Try UTF-8 first, then default encoding.
    - If strip=True, strip whitespace from each line.
    - If as_lines=True, return list of lines.
    """
    if not lpath.endswith((".txt", ".log", ".event", ".py", ".sh")):
        warnings.warn(f"Unexpected extension for file: {lpath}")

    try:
        with open(lpath, "r", encoding="utf-8") as file:
            content = file.read()
    except UnicodeDecodeError:
        encoding = _check_encoding(lpath)
        with open(lpath, "r", encoding=encoding) as file:
            content = file.read()

    if as_lines:
        raw_lines = content.splitlines()
        if strip:
            return [line.strip() for line in raw_lines if line.strip()]
        return [line for line in raw_lines if line]

    if strip:
        return content.strip()
    return content


def _check_encoding(file_path):
    """Check file encoding by trying common encodings."""
    encodings = ["utf-8", "latin1", "cp1252", "iso-8859-1", "ascii"]

    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                f.read()
            return encoding
        except UnicodeDecodeError:
            continue

    raise ValueError(f"Unable to determine encoding for {file_path}")


# def _check_encoding(file_path):
#     """
#     Check the encoding of a given file.

#     This function attempts to read the file with different encodings
#     to determine the correct one.

#     Parameters:
#     -----------
#     file_path : str
#         The path to the file to check.

#     Returns:
#     --------
#     str
#         The detected encoding of the file.

#     Raises:
#     -------
#     IOError
#         If the file cannot be read or the encoding cannot be determined.
#     """
#     import chardet

#     with open(file_path, "rb") as file:
#         raw_data = file.read()

#     result = chardet.detect(raw_data)
#     return result["encoding"]

# EOF
