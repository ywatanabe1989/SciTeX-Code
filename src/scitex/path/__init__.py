#!/usr/bin/env python3
"""Scitex path module."""

from ._clean import clean
from ._find import find_dir, find_file, find_git_root
from ._get_module_path import get_data_path_from_a_package
from ._get_spath import get_spath
from ._getsize import getsize
from ._increment_version import increment_version
from ._mk_spath import mk_spath
from ._path import get_this_path, this_path
from ._split import split
from ._symlink import (
    symlink,
    is_symlink,
    readlink,
    resolve_symlinks,
    create_relative_symlink,
    unlink_symlink,
    list_symlinks,
    fix_broken_symlinks,
)
from ._this_path import get_this_path, this_path
from ._version import find_latest, increment_version

__all__ = [
    "clean",
    "create_relative_symlink",
    "find_dir",
    "find_file",
    "find_git_root",
    "find_latest",
    "fix_broken_symlinks",
    "get_data_path_from_a_package",
    "get_spath",
    "get_this_path",
    "get_this_path",
    "getsize",
    "increment_version",
    "increment_version",
    "is_symlink",
    "list_symlinks",
    "mk_spath",
    "readlink",
    "resolve_symlinks",
    "split",
    "symlink",
    "this_path",
    "this_path",
    "unlink_symlink",
]
