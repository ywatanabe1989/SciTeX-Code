#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-03 02:13:54 (ywatanabe)"
# File: ./scitex_repo/src/scitex/gen/_paste.py
def paste():
    import textwrap

    import pyperclip

    try:
        clipboard_content = pyperclip.paste()
        clipboard_content = textwrap.dedent(clipboard_content)
        exec(clipboard_content)
    except Exception as e:
        print(f"Could not execute clipboard content: {e}")


# EOF
