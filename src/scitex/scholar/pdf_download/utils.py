#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utility functions for Scholar download module"""

import os
import tempfile
from pathlib import Path
from typing import Any


def load_uuid_pdf(uuid_file_path: Path) -> Any:
    """Load UUID-named PDF file using scitex.io.load via temporary symlink.

    Chrome downloads PDFs with UUID names (no extension). scitex.io.load
    requires file extensions, so we create a temporary .pdf symlink.

    Args:
        uuid_file_path: Path to UUID-named PDF file

    Returns:
        Parsed PDF content (DotDict with text, tables, etc.)

    Example:
        >>> from scitex.scholar.download.utils import load_uuid_pdf
        >>> uuid_file = Path("~/.scitex/scholar/library/downloads/f2694ccb-1b6f-4994-add8-5111fd4d52f1")
        >>> content = load_uuid_pdf(uuid_file)
        >>> print(content.keys())  # text, tables, metadata, etc.
    """
    import scitex

    uuid_path = Path(uuid_file_path)

    if not uuid_path.exists():
        raise FileNotFoundError(f"UUID PDF file not found: {uuid_path}")

    # Create temporary symlink with .pdf extension
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_pdf = Path(tmpdir) / f"{uuid_path.name}.pdf"

        # Create symlink
        os.symlink(uuid_path, temp_pdf)

        # Load via scitex.io.load
        content = scitex.io.load(str(temp_pdf))

        return content


# EOF
