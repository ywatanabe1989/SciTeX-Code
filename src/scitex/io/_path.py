#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-05 23:18:40 (ywatanabe)"
# File: ./scitex_repo/src/scitex/io/_path.py

import fnmatch
import os
import re
from glob import glob as _glob

from ..path._split import split
from ..path._this_path import this_path

################################################################################
## PATH
################################################################################
# def get_this_fpath(when_ipython="/tmp/fake.py"):
#     """
#     Get the file path of the calling script, with special handling for IPython environments.

#     Parameters:
#     -----------
#     when_ipython : str, optional
#         The file path to return when running in an IPython environment. Default is "/tmp/fake.py".

#     Returns:
#     --------
#     str
#         The file path of the calling script or the specified path for IPython environments.

#     Example:
#     --------
#     >>> import scitex.io._path as path
#     >>> fpath = path.get_this_fpath()
#     >>> print(fpath)
#     '/path/to/current/script.py'
#     """
#     THIS_FILE = inspect.stack()[1].filename
#     if "ipython" in __file__:  # for ipython
#         THIS_FILE = when_ipython  # "/tmp/fake.py"
#     return __file__


# def mk_spath(sfname, makedirs=False):
#     """
#     Create a save path based on the calling script's location.

#     Parameters:
#     -----------
#     sfname : str
#         The name of the file to be saved.
#     makedirs : bool, optional
#         If True, create the directory structure for the save path. Default is False.

#     Returns:
#     --------
#     str
#         The full save path for the file.

#     Example:
#     --------
#     >>> import scitex.io._path as path
#     >>> spath = path.mk_spath('output.txt', makedirs=True)
#     >>> print(spath)
#     '/path/to/current/script/output.txt'
#     """
#     THIS_FILE = inspect.stack()[1].filename
#     if "ipython" in __file__:  # for ipython
#         THIS_FILE = f'/tmp/fake-{os.getenv("USER")}.py'

#     ## spath
#     fpath = __file__
#     fdir, fname, _ = split_fpath(fpath)
#     sdir = fdir + fname + "/"
#     spath = sdir + sfname

#     if makedirs:
#         os.makedirs(split(spath)[0], exist_ok=True)

#     return spath


def find_the_git_root_dir():
    """
    Find the root directory of the current Git repository.

    Returns:
    --------
    str
        The path to the root directory of the current Git repository.

    Raises:
    -------
    git.exc.InvalidGitRepositoryError
        If the current directory is not part of a Git repository.

    Example:
    --------
    >>> import scitex.io._path as path
    >>> git_root = path.find_the_git_root_dir()
    >>> print(git_root)
    '/path/to/git/repository'
    """
    import git

    repo = git.Repo(".", search_parent_directories=True)
    return repo.working_tree_dir


def split_fpath(fpath):
    """
    Split a file path into directory path, file name, and file extension.

    Parameters:
    -----------
    fpath : str
        The full file path to split.

    Returns:
    --------
    tuple
        A tuple containing (dirname, fname, ext), where:
        - dirname: str, the directory path
        - fname: str, the file name without extension
        - ext: str, the file extension

    Example:
    --------
    >>> dirname, fname, ext = split_fpath('../data/01/day1/split_octave/2kHz_mat/tt8-2.mat')
    >>> print(dirname)
    '../data/01/day1/split_octave/2kHz_mat/'
    >>> print(fname)
    'tt8-2'
    >>> print(ext)
    '.mat'
    """
    dirname = os.path.dirname(fpath) + "/"
    base = os.path.basename(fpath)
    fname, ext = os.path.splitext(base)
    return dirname, fname, ext


def touch(fpath):
    """
    Create a file or update its modification time.

    This function mimics the Unix 'touch' command.

    Parameters:
    -----------
    fpath : str
        The path to the file to be touched.

    Returns:
    --------
    None

    Side Effects:
    -------------
    Creates a new file if it doesn't exist, or updates the modification time
    of an existing file.

    Example:
    --------
    >>> import scitex.io._path as path
    >>> import os
    >>> test_file = '/tmp/test_file.txt'
    >>> path.touch(test_file)
    >>> assert os.path.exists(test_file)
    >>> print(f"File created: {test_file}")
    File created: /tmp/test_file.txt
    """
    import pathlib

    return pathlib.Path(fpath).touch()


def find(rootdir, type="f", exp=["*"]):
    """
    Mimic the Unix find command to search for files or directories.

    Parameters:
    -----------
    rootdir : str
        The root directory to start the search from.
    type : str, optional
        The type of entries to search for. 'f' for files, 'd' for directories,
        or None for both. Default is 'f'.
    exp : str or list of str, optional
        Pattern(s) to match against file or directory names. Default is ["*"].

    Returns:
    --------
    list
        A list of paths that match the search criteria.

    Example:
    --------
    >>> find('/path/to/search', "f", "*.txt")
    ['/path/to/search/file1.txt', '/path/to/search/subdir/file2.txt']
    """
    if isinstance(exp, str):
        exp = [exp]

    matches = []
    for _exp in exp:
        for root, dirs, files in os.walk(rootdir):
            # Depending on the type, choose the list to iterate over
            if type == "f":  # Files only
                names = files
            elif type == "d":  # Directories only
                names = dirs
            else:  # All entries
                names = files + dirs

            for name in names:
                # Construct the full path
                path = os.path.join(root, name)

                # If an _exp is provided, use fnmatch to filter names
                if _exp and not fnmatch.fnmatch(name, _exp):
                    continue

                # If type is set, ensure the type matches
                if type == "f" and not os.path.isfile(path):
                    continue
                if type == "d" and not os.path.isdir(path):
                    continue

                # Add the matching path to the results
                matches.append(path)

    return matches


def find_latest(dirname, fname, ext, version_prefix="_v"):
    """
    Find the latest version of a file with a specific naming pattern.

    This function searches for files in the given directory that match the pattern:
    {fname}{version_prefix}{number}{ext} and returns the path of the file with the highest version number.

    Parameters:
    -----------
    dirname : str
        The directory to search in.
    fname : str
        The base filename without version number or extension.
    ext : str
        The file extension, including the dot (e.g., '.txt').
    version_prefix : str, optional
        The prefix used before the version number. Default is '_v'.

    Returns:
    --------
    str or None
        The full path of the latest version file if found, None otherwise.

    Example:
    --------
    >>> find_latest('/path/to/dir', 'myfile', '.txt')
    '/path/to/dir/myfile_v3.txt'
    """
    version_pattern = re.compile(
        rf"({re.escape(fname)}{re.escape(version_prefix)})(\d+)({re.escape(ext)})$"
    )

    glob_pattern = os.path.join(dirname, f"{fname}{version_prefix}*{ext}")
    files = _glob(glob_pattern)

    highest_version = 0
    latest_file = None

    for file in files:
        filename = os.path.basename(file)
        match = version_pattern.search(filename)
        if match:
            version_num = int(match.group(2))
            if version_num > highest_version:
                highest_version = version_num
                latest_file = file

    return latest_file


# EOF
