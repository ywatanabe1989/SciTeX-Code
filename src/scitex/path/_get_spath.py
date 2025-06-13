#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-02 20:51:29 (ywatanabe)"
# File: ./scitex_repo/src/scitex/path/_get_spath.py

import inspect
import os

from ._split import split


def get_spath(sfname=".", makedirs=False):

    # if __IPYTHON__:
    #     THIS_FILE = f'/tmp/{os.getenv("USER")}.py'
    # else:
    #     THIS_FILE = inspect.stack()[1].filename

    THIS_FILE = inspect.stack()[1].filename
    if "ipython" in __file__:  # for ipython
        THIS_FILE = f'/tmp/{os.getenv("USER")}.py'

    ## spath
    fpath = __file__
    fdir, fname, _ = split(fpath)
    sdir = fdir + fname + "/"
    spath = sdir + sfname

    if makedirs:
        os.makedirs(split(spath)[0], exist_ok=True)

    return spath


# EOF
