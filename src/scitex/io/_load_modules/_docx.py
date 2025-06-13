#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-14 07:55:35 (ywatanabe)"
# File: ./scitex_repo/src/scitex/io/_load_modules/_docx.py

from typing import Any


def _load_docx(lpath: str, **kwargs) -> Any:
    """
    Load and extract text content from a .docx file.

    Parameters:
    -----------
    lpath : str
        The path to the .docx file.

    Returns:
    --------
    str
        The extracted text content from the .docx file.

    Raises:
    -------
    FileNotFoundError
        If the specified file does not exist.
    docx.opc.exceptions.PackageNotFoundError
        If the file is not a valid .docx file.
    """
    if not lpath.endswith(".docx"):
        raise ValueError("File must have .docx extension")

    from docx import Document

    doc = Document(lpath)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "".join(full_text)


# EOF
