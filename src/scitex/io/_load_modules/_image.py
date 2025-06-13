#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-14 07:55:38 (ywatanabe)"
# File: ./scitex_repo/src/scitex/io/_load_modules/_image.py

from typing import Any

from PIL import Image


def _load_image(lpath: str, **kwargs) -> Any:
    """Load image file."""
    supported_exts = [".jpg", ".jpeg", ".png", ".tiff", ".tif"]
    if not any(lpath.lower().endswith(ext) for ext in supported_exts):
        raise ValueError("Unsupported image format")
    return Image.open(lpath, **kwargs)


# EOF
