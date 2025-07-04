#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-02 19:53:58 (ywatanabe)"
# File: ./scitex_repo/src/scitex/path/_find.py
#!./env/bin/python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-04-17 09:34:43"
# Author: Yusuke Watanabe (ywata1989@gmail.com)

"""
This script does XYZ.
"""

import fnmatch
import os
import sys

import scitex


# Functions
def find_git_root():
    import git

    repo = git.Repo(".", search_parent_directories=True)
    return repo.working_tree_dir


def find_dir(root_dir, exp):
    return _find(root_dir, type="d", exp=exp)


def find_file(root_dir, exp):
    return _find(root_dir, type="f", exp=exp)


def _find(rootdir, type="f", exp=["*"]):
    """
    Mimicks the Unix find command.

    Example:
        # rootdir =
        # type = 'f'  # 'f' for files, 'd' for directories, None for both
        # exp = '*.txt'  # Pattern to match, or None to match all
        find('/path/to/search', "f", "*.txt")
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

                exclude_keys = ["/lib/", "/env/", "/build/"]
                if not any(ek in path for ek in exclude_keys):
                    matches.append(path)

                # for ek in exclude_keys:
                #     if ek in path:
                #         path = None
                #         break

                # if path is not None:
                #     # Add the matching path to the results
                #     matches.append(path)

    return matches


if __name__ == "__main__":
    # Import matplotlib only when running as script
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        plt = None
    
    # Start
    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt)

    # (YOUR AWESOME CODE)

    # Close
    scitex.gen.close(CONFIG)

# EOF

"""
/ssh:ywatanabe@444:/home/ywatanabe/proj/entrance/scitex/path/_find.py
"""


# EOF
