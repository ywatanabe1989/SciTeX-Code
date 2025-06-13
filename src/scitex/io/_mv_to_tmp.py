#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-02 21:25:50 (ywatanabe)"
# File: ./scitex_repo/src/scitex/io/_mv_to_tmp.py

from shutil import move


def _mv_to_tmp(fpath, L=2):
    try:
        tgt_fname = "-".join(fpath.split("/")[-L:])
        tgt_fpath = "/tmp/{}".format(tgt_fname)
        move(fpath, tgt_fpath)
        print("Moved to: {}".format(tgt_fpath))
    except:
        pass


# EOF
