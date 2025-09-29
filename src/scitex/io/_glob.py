#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-25 00:31:08 (ywatanabe)"
# File: ./scitex_repo/src/scitex/io/_glob.py

THIS_FILE = "/home/ywatanabe/proj/scitex_repo/src/scitex/io/_glob.py"

import re as _re
from glob import glob as _glob
from pathlib import Path
from typing import Union
from ..str._parse import parse as _parse
from natsort import natsorted as _natsorted


def glob(expression: Union[str, Path], parse=False, ensure_one=False):
    """
    Perform a glob operation with natural sorting and extended pattern support.

    This function extends the standard glob functionality by adding natural sorting
    and support for curly brace expansion in the glob pattern.

    Parameters:
    -----------
    expression : Union[str, Path]
        The glob pattern to match against file paths. Can be a string or pathlib.Path object. 
        Supports standard glob syntax and curly brace expansion (e.g., 'dir/{a,b}/*.txt').
    parse : bool, optional
        Whether to parse the matched paths. Default is False.
    ensure_one : bool, optional
        Ensure exactly one match is found. Default is False.

    Returns:
    --------
    Union[List[str], Tuple[List[str], List[dict]]]
        If parse=False: A naturally sorted list of file paths
        If parse=True: Tuple of (paths, parsed results)

    Examples:
    ---------
    >>> glob('data/*.txt')
    ['data/file1.txt', 'data/file2.txt', 'data/file10.txt']

    >>> glob('data/{a,b}/*.txt')
    ['data/a/file1.txt', 'data/a/file2.txt', 'data/b/file1.txt']

    >>> paths, parsed = glob('data/subj_{id}/run_{run}.txt', parse=True)
    >>> paths
    ['data/subj_001/run_01.txt', 'data/subj_001/run_02.txt']
    >>> parsed
    [{'id': '001', 'run': '01'}, {'id': '001', 'run': '02'}]

    >>> paths, parsed = glob('data/subj_{id}/run_{run}.txt', parse=True, ensure_one=True)
    AssertionError  # if more than one file matches
    """
    # Convert Path objects to strings for consistency
    if isinstance(expression, Path):
        expression = str(expression)
        
    glob_pattern = _re.sub(r"{[^}]*}", "*", expression)
    # Enable recursive globbing for ** patterns
    recursive = "**" in glob_pattern
    try:
        found_paths = _natsorted(_glob(eval(glob_pattern), recursive=recursive))
    except:
        found_paths = _natsorted(_glob(glob_pattern, recursive=recursive))

    if ensure_one:
        assert len(found_paths) == 1

    if parse:
        parsed = [_parse(found_path, expression) for found_path in found_paths]
        return found_paths, parsed

    else:
        return found_paths


def parse_glob(expression: Union[str, Path], ensure_one=False):
    """
    Convenience function for glob with parsing enabled.

    Parameters:
    -----------
    expression : Union[str, Path]
        The glob pattern to match against file paths. Can be a string or pathlib.Path object.
    ensure_one : bool, optional
        Ensure exactly one match is found. Default is False.

    Returns:
    --------
    Tuple[List[str], List[dict]]
        Matched paths and parsed results.

    Examples:
    ---------
    >>> paths, parsed = pglob('data/subj_{id}/run_{run}.txt')
    >>> paths
    ['data/subj_001/run_01.txt', 'data/subj_001/run_02.txt']
    >>> parsed
    [{'id': '001', 'run': '01'}, {'id': '001', 'run': '02'}]

    >>> paths, parsed = pglob('data/subj_{id}/run_{run}.txt', ensure_one=True)
    AssertionError  # if more than one file matches
    """
    return glob(expression, parse=True, ensure_one=ensure_one)


# EOF
