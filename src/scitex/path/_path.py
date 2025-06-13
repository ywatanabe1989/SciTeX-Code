#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-02 20:46:35 (ywatanabe)"
# File: ./scitex_repo/src/scitex/path/_path.py

import inspect


def this_path(when_ipython="/tmp/fake.py"):
    THIS_FILE = inspect.stack()[1].filename
    if "ipython" in __file__:
        THIS_FILE = when_ipython
    return __file__


get_this_path = this_path


# EOF
