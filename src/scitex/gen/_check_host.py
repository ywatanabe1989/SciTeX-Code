#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-02 13:43:36 (ywatanabe)"
# File: ./scitex_repo/src/scitex/gen/_check_host.py


from .._sh import sh
import sys


def check_host(keyword):
    return keyword in sh("echo $(hostname)", verbose=False)


is_host = check_host


def verify_host(keyword):
    if is_host(keyword):
        print(f"Host verification successed for keyword: {keyword}")
        return
    else:
        print(f"Host verification failed for keyword: {keyword}")
        sys.exit(1)


if __name__ == "__main__":
    # check_host("ywata")
    verify_host("titan")
    verify_host("ywata")
    verify_host("crest")


# EOF
