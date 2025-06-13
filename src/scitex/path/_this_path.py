#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-02 16:22:21 (ywatanabe)"
# File: ./scitex_repo/src/scitex/path/_this_path.py
#!/usr/bin/env python3

import inspect


def this_path(ipython_fake_path="/tmp/fake.py"):
    THIS_FILE = inspect.stack()[1].filename
    if "ipython" in __file__:
        THIS_FILE = ipython_fake_path
    return __file__


get_this_path = this_path

# EOF
