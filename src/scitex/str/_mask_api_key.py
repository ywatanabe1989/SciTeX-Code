#!./env/bin/python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-06-10 20:48:30 (ywatanabe)"
# /home/ywatanabe/proj/scitex/src/scitex/gen/_mask_api_key.py


def mask_api(api_key):
    return f"{api_key[:4]}****{api_key[-4:]}"
