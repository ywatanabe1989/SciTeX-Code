#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-14 07:55:46 (ywatanabe)"
# File: ./scitex_repo/src/scitex/io/_load_modules/_pdf.py

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None


def _load_pdf(lpath, **kwargs):
    """Load PDF file and return extracted text."""
    if PyPDF2 is None:
        raise ImportError("PyPDF2 is required for PDF loading. Install with: pip install PyPDF2")
        
    try:
        if not lpath.endswith(".pdf"):
            raise ValueError("File must have .pdf extension")

        reader = PyPDF2.PdfReader(lpath)
        full_text = []
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            full_text.append(page.extract_text())
        return "\n".join(full_text)
    except (ValueError, FileNotFoundError, PyPDF2.PdfReadError) as e:
        raise ValueError(f"Error loading PDF {lpath}: {str(e)}")


# EOF
