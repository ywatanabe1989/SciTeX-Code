#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-23 13:54:54 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/_PDFExtractor.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/_PDFExtractor.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
PDF text extraction functionality for downstream AI integration.

This module provides clean text extraction from scientific PDFs,
with section awareness and format handling.
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class PDFExtractor:
    """Extract text and structure from scientific PDFs."""

    # Common section headers in scientific papers
    SECTION_PATTERNS = [
        r"^\s*abstract\s*$",
        r"^\s*introduction\s*$",
        r"^\s*background\s*$",
        r"^\s*methods?\s*$",
        r"^\s*materials?\s+and\s+methods?\s*$",
        r"^\s*results?\s*$",
        r"^\s*discussion\s*$",
        r"^\s*conclusions?\s*$",
        r"^\s*references?\s*$",
        r"^\s*acknowledgments?\s*$",
        r"^\s*supplementary\s*",
        r"^\s*\d+\.?\s+\w+",  # Numbered sections like "1. Introduction"
    ]

    def __init__(self):
        self._fitz_available = self._check_fitz()
        if not self._fitz_available:
            logger.warning(
                "PyMuPDF (fitz) not installed. PDF text extraction will be limited. "
                "Install with: pip install PyMuPDF"
            )

    def _check_fitz(self) -> bool:
        """Check if PyMuPDF is available."""
        try:
            import fitz

            return True
        except ImportError:
            return False

    def _extract_text(self, pdf_path: Path) -> str:
        """
        Extract all text from PDF.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text as string
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        if self._fitz_available:
            return self._extract_with_fitz(pdf_path)
        else:
            return self._extract_fallback(pdf_path)

    def _extract_sections(self, pdf_path: Path) -> Dict[str, str]:
        """
        Extract text organized by sections.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary mapping section names to text
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        if self._fitz_available:
            return self._extract_sections_with_fitz(pdf_path)
        else:
            # Fallback: return all text as "content"
            text = self._extract_fallback(pdf_path)
            return {"content": text}

    def _extract_with_fitz(self, pdf_path: Path) -> str:
        """Extract text using PyMuPDF."""
        import fitz

        try:
            doc = fitz.open(pdf_path)
            text_parts = []

            for page_num, page in enumerate(doc):
                text = page.get_text()
                if text.strip():
                    text_parts.append(text)

            doc.close()
            return "\n".join(text_parts)

        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            return ""

    def _extract_sections_with_fitz(self, pdf_path: Path) -> Dict[str, str]:
        """Extract text by sections using PyMuPDF."""
        import fitz

        try:
            doc = fitz.open(pdf_path)

            # Extract all text with page numbers
            pages_text = []
            for page_num, page in enumerate(doc):
                text = page.get_text()
                if text.strip():
                    pages_text.append((page_num, text))

            doc.close()

            # Parse sections
            sections = self._parse_sections(pages_text)
            return sections

        except Exception as e:
            logger.error(f"Error extracting sections from {pdf_path}: {e}")
            return {"error": str(e)}

    def _parse_sections(
        self, pages_text: List[Tuple[int, str]]
    ) -> Dict[str, str]:
        """Parse text into sections based on headers."""
        sections = {}
        current_section = "header"
        current_text = []

        for page_num, page_text in pages_text:
            lines = page_text.split("\n")

            for line in lines:
                line_lower = line.lower().strip()

                # Check if this line is a section header
                is_header = False
                for pattern in self.SECTION_PATTERNS:
                    if re.match(pattern, line_lower, re.IGNORECASE):
                        # Save previous section
                        if current_text:
                            sections[current_section] = "\n".join(current_text)

                        # Start new section
                        current_section = line_lower.replace(".", "").strip()
                        current_text = []
                        is_header = True
                        break

                if not is_header:
                    current_text.append(line)

        # Save last section
        if current_text:
            sections[current_section] = "\n".join(current_text)

        return sections

    def _extract_fallback(self, pdf_path: Path) -> str:
        """Fallback text extraction without PyMuPDF."""
        # This is a placeholder - in production you might use:
        # - pdfplumber
        # - PyPDF2
        # - subprocess call to pdftotext
        logger.warning(f"Using fallback extraction for {pdf_path}")
        return f"[PDF text extraction requires PyMuPDF: {pdf_path}]"

    def extract_metadata(self, pdf_path: Path) -> Dict[str, any]:
        """
        Extract PDF metadata.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with metadata (title, author, subject, etc.)
        """
        if not self._fitz_available:
            return {}

        import fitz

        try:
            doc = fitz.open(pdf_path)
            metadata = doc.metadata
            doc.close()
            return metadata
        except Exception as e:
            logger.error(f"Error extracting metadata from {pdf_path}: {e}")
            return {}

    def _extract_for_ai(self, pdf_path: Path) -> Dict[str, any]:
        """
        Extract comprehensive data for AI processing.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with:
            - full_text: Complete text
            - sections: Text by section
            - metadata: PDF metadata
            - stats: Word count, page count, etc.
        """
        result = {
            "pdf_path": str(pdf_path),
            "filename": pdf_path.name,
            "full_text": "",
            "sections": {},
            "metadata": {},
            "stats": {},
        }

        try:
            # Extract text
            result["full_text"] = self._extract_text(pdf_path)

            # Extract sections
            result["sections"] = self._extract_sections(pdf_path)

            # Extract metadata
            result["metadata"] = self.extract_metadata(pdf_path)

            # Calculate stats
            result["stats"] = {
                "total_chars": len(result["full_text"]),
                "total_words": len(result["full_text"].split()),
                "num_sections": len(result["sections"]),
            }

            # Add page count if available
            if self._fitz_available:
                import fitz

                doc = fitz.open(pdf_path)
                result["stats"]["num_pages"] = len(doc)
                doc.close()

        except Exception as e:
            logger.error(f"Error in _extract_for_ai: {e}")
            result["error"] = str(e)

        return result


# Convenience function
def _extract_text(pdf_path: Path) -> str:
    """Extract text from PDF file."""
    extractor = PDFExtractor()
    return extractor._extract_text(pdf_path)


def _extract_for_ai(pdf_path: Path) -> Dict[str, any]:
    """Extract comprehensive PDF data for AI processing."""
    extractor = PDFExtractor()
    return extractor._extract_for_ai(pdf_path)

# EOF
