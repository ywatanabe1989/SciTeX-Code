#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-06 10:27:52 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/io/_load_modules/_pdf.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = __file__
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Enhanced PDF loading module with comprehensive extraction capabilities.

This module provides advanced PDF extraction for scientific papers, including:
- Text extraction with formatting preservation
- Table extraction as pandas DataFrames
- Image extraction with metadata
- Section-aware text parsing
- Multiple extraction modes for different use cases
"""

import hashlib
import re
import tempfile
from typing import Any, Dict, List

from scitex import logging
from scitex.dict import DotDict

logger = logging.getLogger(__name__)

# Try to import PDF libraries in order of preference
try:
    import fitz  # PyMuPDF - preferred for text and images

    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False

try:
    import pdfplumber  # Best for table extraction

    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import PyPDF2  # Fallback option

    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


def _load_pdf(lpath: str, mode: str = "full", **kwargs) -> Any:
    """
    Load PDF file with comprehensive extraction capabilities.

    Args:
        lpath: Path to PDF file
        mode: Extraction mode (default: 'full')
            - 'full': Complete extraction including text, sections, metadata, pages, tables, and images
            - 'scientific': Optimized for scientific papers (text + sections + tables + images + stats)
            - 'text': Plain text extraction only
            - 'sections': Section-aware text extraction
            - 'tables': Extract tables as DataFrames
            - 'images': Extract images with metadata
            - 'metadata': PDF metadata only
            - 'pages': Page-by-page extraction
        **kwargs: Additional arguments
            - backend: 'auto' (default), 'fitz', 'pdfplumber', or 'pypdf2'
            - clean_text: Clean extracted text (default: True)
            - extract_images: Extract images to files (default: False for 'full' mode, True for 'scientific')
            - output_dir: Directory for extracted images/tables (default: temp dir)
            - save_as_jpg: Convert all extracted images to JPG format (default: True)
            - table_settings: Dict of pdfplumber table extraction settings

    Returns:
        Extracted content based on mode:
        - 'text': str
        - 'sections': Dict[str, str]
        - 'tables': Dict[int, List[pd.DataFrame]]
        - 'images': List[Dict] with image metadata
        - 'metadata': Dict with PDF metadata
        - 'pages': List[Dict] with page content
        - 'full': Dict with comprehensive extraction (text, sections, metadata, pages, tables, images, stats)
        - 'scientific': Dict with scientific paper extraction (text, sections, metadata, tables, images, stats)

    Examples:
        >>> import scitex.io as stx

        >>> # Full extraction (default) - everything included
        >>> data = stx.load("paper.pdf")
        >>> print(data['full_text'])      # Complete text
        >>> print(data['sections'])       # Parsed sections
        >>> print(data['tables'])         # All tables as DataFrames
        >>> print(data['metadata'])       # PDF metadata
        >>> print(data['pages'])          # Page-by-page content
        >>> print(data['stats'])          # Statistics

        >>> # Scientific mode (recommended for papers) - optimized for research
        >>> paper = stx.load("paper.pdf", mode="scientific")
        >>> print(paper['text'])          # Full text
        >>> print(paper['sections'])      # Sections (Abstract, Methods, etc.)
        >>> print(paper['tables'])        # All tables as DataFrames
        >>> print(paper['images'])        # Image metadata
        >>> print(paper['stats'])         # Content statistics

        >>> # Simple text extraction only
        >>> text = stx.load("paper.pdf", mode="text")

        >>> # Extract tables only
        >>> tables = stx.load("paper.pdf", mode="tables")
    """
    mode = kwargs.get("mode", mode)
    backend = kwargs.get("backend", "auto")
    clean_text = kwargs.get("clean_text", True)
    extract_images = kwargs.get("extract_images", False)
    output_dir = kwargs.get("output_dir", None)
    table_settings = kwargs.get("table_settings", {})

    # Validate file
    if not lpath.endswith(".pdf"):
        raise ValueError("File must have .pdf extension")

    if not os.path.exists(lpath):
        raise FileNotFoundError(f"PDF file not found: {lpath}")

    # Select backend based on mode and availability
    backend = _select_backend(mode, backend)

    # Create output directory if needed
    if output_dir is None and (
        extract_images or mode in ["images", "scientific", "full"]
    ):
        output_dir = tempfile.mkdtemp(prefix="pdf_extract_")
        logger.debug(f"Using temporary directory: {output_dir}")

    # Extract based on mode
    if mode == "text":
        return _extract_text(lpath, backend, clean_text)
    elif mode == "sections":
        return _extract_sections(lpath, backend, clean_text)
    elif mode == "tables":
        return _extract_tables(lpath, table_settings)
    elif mode == "images":
        save_as_jpg = kwargs.get("save_as_jpg", True)
        return _extract_images(lpath, output_dir, save_as_jpg)
    elif mode == "metadata":
        return _extract_metadata(lpath, backend)
    elif mode == "pages":
        return _extract_pages(lpath, backend, clean_text)
    elif mode == "scientific":
        save_as_jpg = kwargs.get("save_as_jpg", True)
        return _extract_scientific(
            lpath, clean_text, output_dir, table_settings, save_as_jpg
        )
    elif mode == "full":
        save_as_jpg = kwargs.get("save_as_jpg", True)
        return _extract_full(
            lpath,
            backend,
            clean_text,
            extract_images,
            output_dir,
            table_settings,
            save_as_jpg,
        )
    else:
        raise ValueError(f"Unknown extraction mode: {mode}")


def _select_backend(mode: str, requested: str) -> str:
    """Select appropriate backend based on mode and availability."""
    if requested != "auto":
        return requested

    # Mode-specific backend selection
    if mode in ["tables"]:
        if PDFPLUMBER_AVAILABLE:
            return "pdfplumber"
        else:
            logger.warning(
                "pdfplumber not available for table extraction. Install with: pip install pdfplumber"
            )
            return "fitz" if FITZ_AVAILABLE else "pypdf2"

    elif mode in ["images", "scientific", "full"]:
        if FITZ_AVAILABLE:
            return "fitz"
        else:
            logger.warning(
                "PyMuPDF (fitz) recommended for image extraction. Install with: pip install PyMuPDF"
            )
            return "pdfplumber" if PDFPLUMBER_AVAILABLE else "pypdf2"

    else:  # text, sections, metadata, pages
        if FITZ_AVAILABLE:
            return "fitz"
        elif PDFPLUMBER_AVAILABLE:
            return "pdfplumber"
        elif PYPDF2_AVAILABLE:
            return "pypdf2"
        else:
            raise ImportError(
                "No PDF library available. Install one of:\n"
                "  pip install PyMuPDF     # Recommended\n"
                "  pip install pdfplumber  # Best for tables\n"
                "  pip install PyPDF2      # Basic fallback"
            )


def _extract_text(lpath: str, backend: str, clean: bool) -> str:
    """Extract plain text from PDF."""
    if backend == "fitz":
        return _extract_text_fitz(lpath, clean)
    elif backend == "pdfplumber":
        return _extract_text_pdfplumber(lpath, clean)
    else:
        return _extract_text_pypdf2(lpath, clean)


def _extract_text_fitz(lpath: str, clean: bool) -> str:
    """Extract text using PyMuPDF."""
    if not FITZ_AVAILABLE:
        raise ImportError("PyMuPDF (fitz) not available")

    try:
        doc = fitz.open(lpath)
        text_parts = []

        for page_num, page in enumerate(doc):
            text = page.get_text()
            if text.strip():
                text_parts.append(text)

        doc.close()

        full_text = "\n".join(text_parts)

        if clean:
            full_text = _clean_pdf_text(full_text)

        return full_text

    except Exception as e:
        logger.error(f"Error extracting text with fitz from {lpath}: {e}")
        raise


def _extract_text_pdfplumber(lpath: str, clean: bool) -> str:
    """Extract text using pdfplumber."""
    if not PDFPLUMBER_AVAILABLE:
        raise ImportError("pdfplumber not available")

    try:
        import pdfplumber

        text_parts = []
        with pdfplumber.open(lpath) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

        full_text = "\n".join(text_parts)

        if clean:
            full_text = _clean_pdf_text(full_text)

        return full_text

    except Exception as e:
        logger.error(
            f"Error extracting text with pdfplumber from {lpath}: {e}"
        )
        raise


def _extract_text_pypdf2(lpath: str, clean: bool) -> str:
    """Extract text using PyPDF2."""
    if not PYPDF2_AVAILABLE:
        raise ImportError("PyPDF2 not available")

    try:
        reader = PyPDF2.PdfReader(lpath)
        text_parts = []

        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text()
            if text.strip():
                text_parts.append(text)

        full_text = "\n".join(text_parts)

        if clean:
            full_text = _clean_pdf_text(full_text)

        return full_text

    except Exception as e:
        logger.error(f"Error extracting text with PyPDF2 from {lpath}: {e}")
        raise


def _extract_tables(
    lpath: str, table_settings: Dict = None
) -> Dict[int, List["pd.DataFrame"]]:
    """
    Extract tables from PDF as pandas DataFrames.

    Returns:
        Dict mapping page numbers to list of DataFrames
    """
    if not PDFPLUMBER_AVAILABLE:
        raise ImportError(
            "pdfplumber required for table extraction. Install with:\n"
            "  pip install pdfplumber pandas"
        )

    if not PANDAS_AVAILABLE:
        raise ImportError("pandas required for table extraction")

    import pandas as pd
    import pdfplumber

    tables_dict = {}
    table_settings = table_settings or {}

    try:
        with pdfplumber.open(lpath) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Extract tables from page
                tables = page.extract_tables(**table_settings)

                if tables:
                    # Convert to DataFrames
                    dfs = []
                    for table in tables:
                        if table and len(table) > 0:
                            # First row as header if it looks like headers
                            if len(table) > 1 and all(
                                isinstance(cell, str)
                                for cell in table[0]
                                if cell
                            ):
                                df = pd.DataFrame(table[1:], columns=table[0])
                            else:
                                df = pd.DataFrame(table)

                            # Clean up DataFrame
                            df = (
                                df.replace("", None)
                                .dropna(how="all", axis=1)
                                .dropna(how="all", axis=0)
                            )

                            if not df.empty:
                                dfs.append(df)

                    if dfs:
                        tables_dict[page_num] = dfs

        logger.info(f"Extracted tables from {len(tables_dict)} pages")
        return tables_dict

    except Exception as e:
        logger.error(f"Error extracting tables: {e}")
        raise


def _extract_images(
    lpath: str, output_dir: str = None, save_as_jpg: bool = True
) -> List[Dict[str, Any]]:
    """
    Extract images from PDF with metadata.

    Args:
        lpath: Path to PDF file
        output_dir: Directory to save images (optional)
        save_as_jpg: If True, convert all images to JPG format (default: True)

    Returns:
        List of dicts containing image metadata and paths
    """
    if not FITZ_AVAILABLE:
        raise ImportError(
            "PyMuPDF (fitz) required for image extraction. Install with:\n"
            "  pip install PyMuPDF"
        )

    images_info = []

    try:
        doc = fitz.open(lpath)

        for page_num, page in enumerate(doc):
            image_list = page.get_images()

            for img_index, img in enumerate(image_list):
                xref = img[0]

                # Extract image data
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                original_ext = base_image["ext"]

                image_info = {
                    "page": page_num + 1,
                    "index": img_index,
                    "width": base_image["width"],
                    "height": base_image["height"],
                    "colorspace": base_image["colorspace"],
                    "bpc": base_image["bpc"],  # bits per component
                    "original_ext": original_ext,
                    "size_bytes": len(image_bytes),
                }

                # Save image if output directory provided
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)

                    if save_as_jpg and original_ext not in ["jpg", "jpeg"]:
                        # Convert to JPG using PIL
                        try:
                            from PIL import Image
                            import io

                            # Open image from bytes
                            img_pil = Image.open(io.BytesIO(image_bytes))

                            # Convert RGBA to RGB if necessary
                            if img_pil.mode in ('RGBA', 'LA', 'P'):
                                # Create a white background
                                background = Image.new('RGB', img_pil.size, (255, 255, 255))
                                if img_pil.mode == 'P':
                                    img_pil = img_pil.convert('RGBA')
                                background.paste(img_pil, mask=img_pil.split()[-1] if img_pil.mode == 'RGBA' else None)
                                img_pil = background
                            elif img_pil.mode != 'RGB':
                                img_pil = img_pil.convert('RGB')

                            # Save as JPG
                            filename = f"page_{page_num + 1}_img_{img_index}.jpg"
                            filepath = os.path.join(output_dir, filename)
                            img_pil.save(filepath, 'JPEG', quality=95)

                            image_info["ext"] = "jpg"
                        except ImportError:
                            logger.warning("PIL not available for image conversion. Install with: pip install Pillow")
                            # Fall back to original format
                            filename = f"page_{page_num + 1}_img_{img_index}.{original_ext}"
                            filepath = os.path.join(output_dir, filename)
                            with open(filepath, "wb") as img_file:
                                img_file.write(image_bytes)
                            image_info["ext"] = original_ext
                    else:
                        # Save with original format
                        ext = "jpg" if original_ext == "jpeg" else original_ext
                        filename = f"page_{page_num + 1}_img_{img_index}.{ext}"
                        filepath = os.path.join(output_dir, filename)
                        with open(filepath, "wb") as img_file:
                            img_file.write(image_bytes)
                        image_info["ext"] = ext

                    image_info["filepath"] = filepath
                    image_info["filename"] = filename

                images_info.append(image_info)

        doc.close()

        logger.info(f"Extracted {len(images_info)} images from PDF")
        return images_info

    except Exception as e:
        logger.error(f"Error extracting images: {e}")
        raise


def _extract_sections(lpath: str, backend: str, clean: bool) -> Dict[str, str]:
    """Extract text organized by sections."""
    # Get full text first
    text = _extract_text(lpath, backend, clean=False)

    # Parse into sections
    sections = _parse_sections(text)

    # Clean section text if requested
    if clean:
        for section, content in sections.items():
            sections[section] = _clean_pdf_text(content)

    return sections


def _parse_sections(text: str) -> Dict[str, str]:
    """
    Parse text into sections based on IMRaD structure.

    Follows the standard scientific paper structure:
    - frontpage: Title, authors, affiliations, keywords
    - abstract: Paper summary
    - introduction: Background and motivation
    - methods: Methodology (materials and methods, experimental design)
    - results: Findings
    - discussion: Interpretation and implications
    - references: Citations
    """
    sections = {}
    current_section = "frontpage"
    current_text = []

    # Simplified section patterns - IMRaD + frontpage only
    # Only match standalone section headers (exact matches)
    section_patterns = [
        r"^abstract\s*$",
        r"^summary\s*$",
        r"^introduction\s*$",
        r"^background\s*$",
        r"^methods?\s*$",
        r"^materials?\s+and\s+methods?\s*$",
        r"^methodology\s*$",
        r"^results?\s*$",
        r"^discussion\s*$",
        r"^references?\s*$",
    ]

    lines = text.split("\n")

    for line in lines:
        line_lower = line.lower().strip()
        line_stripped = line.strip()

        # Check if this line is a section header
        is_header = False
        for pattern in section_patterns:
            if re.match(pattern, line_lower):
                # Additional validation: header lines should be short (< 50 chars)
                # and not contain numbers/punctuation (except spaces)
                if len(line_stripped) < 50:
                    # Save previous section
                    if current_text:
                        sections[current_section] = "\n".join(current_text).strip()

                    # Start new section
                    current_section = line_lower.strip()
                    current_text = []
                    is_header = True
                    break

        if not is_header:
            current_text.append(line)

    # Save last section
    if current_text:
        sections[current_section] = "\n".join(current_text).strip()

    return sections


def _extract_metadata(lpath: str, backend: str) -> Dict[str, Any]:
    """Extract PDF metadata."""
    metadata = {
        "file_path": lpath,
        "file_name": os.path.basename(lpath),
        "file_size": os.path.getsize(lpath),
        "backend": backend,
    }

    if backend == "fitz" and FITZ_AVAILABLE:
        try:
            doc = fitz.open(lpath)
            pdf_metadata = doc.metadata

            metadata.update(
                {
                    "title": pdf_metadata.get("title", ""),
                    "author": pdf_metadata.get("author", ""),
                    "subject": pdf_metadata.get("subject", ""),
                    "keywords": pdf_metadata.get("keywords", ""),
                    "creator": pdf_metadata.get("creator", ""),
                    "producer": pdf_metadata.get("producer", ""),
                    "creation_date": str(pdf_metadata.get("creationDate", "")),
                    "modification_date": str(pdf_metadata.get("modDate", "")),
                    "pages": len(doc),
                    "encrypted": doc.is_encrypted,
                }
            )

            doc.close()

        except Exception as e:
            logger.error(f"Error extracting metadata with fitz: {e}")

    elif backend == "pdfplumber" and PDFPLUMBER_AVAILABLE:
        try:
            import pdfplumber

            with pdfplumber.open(lpath) as pdf:
                metadata["pages"] = len(pdf.pages)
                if hasattr(pdf, "metadata"):
                    metadata.update(pdf.metadata)
        except Exception as e:
            logger.error(f"Error extracting metadata with pdfplumber: {e}")

    elif backend == "pypdf2" and PYPDF2_AVAILABLE:
        try:
            reader = PyPDF2.PdfReader(lpath)

            if reader.metadata:
                metadata.update(
                    {
                        "title": reader.metadata.get("/Title", ""),
                        "author": reader.metadata.get("/Author", ""),
                        "subject": reader.metadata.get("/Subject", ""),
                        "creator": reader.metadata.get("/Creator", ""),
                        "producer": reader.metadata.get("/Producer", ""),
                        "creation_date": str(
                            reader.metadata.get("/CreationDate", "")
                        ),
                        "modification_date": str(
                            reader.metadata.get("/ModDate", "")
                        ),
                    }
                )

            metadata["pages"] = len(reader.pages)
            metadata["encrypted"] = reader.is_encrypted

        except Exception as e:
            logger.error(f"Error extracting metadata with PyPDF2: {e}")

    # Generate file hash
    metadata["md5_hash"] = _calculate_file_hash(lpath)

    return metadata


def _extract_pages(
    lpath: str, backend: str, clean: bool
) -> List[Dict[str, Any]]:
    """Extract content page by page."""
    pages = []

    if backend == "fitz" and FITZ_AVAILABLE:
        doc = fitz.open(lpath)

        for page_num, page in enumerate(doc):
            text = page.get_text()
            if clean:
                text = _clean_pdf_text(text)

            pages.append(
                {
                    "page_number": page_num + 1,
                    "text": text,
                    "char_count": len(text),
                    "word_count": len(text.split()),
                }
            )

        doc.close()

    elif backend == "pdfplumber" and PDFPLUMBER_AVAILABLE:
        import pdfplumber

        with pdfplumber.open(lpath) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                if clean:
                    text = _clean_pdf_text(text)

                pages.append(
                    {
                        "page_number": page_num + 1,
                        "text": text,
                        "char_count": len(text),
                        "word_count": len(text.split()),
                    }
                )

    elif backend == "pypdf2" and PYPDF2_AVAILABLE:
        reader = PyPDF2.PdfReader(lpath)

        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text()
            if clean:
                text = _clean_pdf_text(text)

            pages.append(
                {
                    "page_number": page_num + 1,
                    "text": text,
                    "char_count": len(text),
                    "word_count": len(text.split()),
                }
            )

    return pages


def _extract_scientific(
    lpath: str, clean_text: bool, output_dir: str, table_settings: Dict, save_as_jpg: bool = True
) -> DotDict:
    """
    Optimized extraction for scientific papers.
    Extracts text, tables, images, and sections in a structured format.
    """
    result = {
        "pdf_path": lpath,
        "filename": os.path.basename(lpath),
        "extraction_mode": "scientific",
    }

    try:
        # Extract text and sections
        backend = _select_backend("text", "auto")
        result["text"] = _extract_text(lpath, backend, clean_text)
        result["sections"] = _extract_sections(lpath, backend, clean_text)

        # Extract metadata
        result["metadata"] = _extract_metadata(lpath, backend)

        # Extract tables if pdfplumber available
        if PDFPLUMBER_AVAILABLE and PANDAS_AVAILABLE:
            try:
                result["tables"] = _extract_tables(lpath, table_settings)
            except Exception as e:
                logger.warning(f"Could not extract tables: {e}")
                result["tables"] = {}
        else:
            result["tables"] = {}
            logger.info("Table extraction requires pdfplumber and pandas")

        # Extract images if fitz available
        if FITZ_AVAILABLE:
            try:
                result["images"] = _extract_images(lpath, output_dir, save_as_jpg)
            except Exception as e:
                logger.warning(f"Could not extract images: {e}")
                result["images"] = []
        else:
            result["images"] = []
            logger.info("Image extraction requires PyMuPDF (fitz)")

        # Calculate statistics
        result["stats"] = {
            "total_chars": len(result["text"]),
            "total_words": len(result["text"].split()),
            "total_pages": result["metadata"].get("pages", 0),
            "num_sections": len(result["sections"]),
            "num_tables": sum(
                len(tables) for tables in result["tables"].values()
            ),
            "num_images": len(result["images"]),
        }

        logger.info(
            f"Scientific extraction complete: "
            f"{result['stats']['total_pages']} pages, "
            f"{result['stats']['num_sections']} sections, "
            f"{result['stats']['num_tables']} tables, "
            f"{result['stats']['num_images']} images"
        )

    except Exception as e:
        logger.error(f"Error in scientific extraction: {e}")
        result["error"] = str(e)

    return DotDict(result)


def _extract_full(
    lpath: str,
    backend: str,
    clean: bool,
    extract_images: bool,
    output_dir: str,
    table_settings: Dict,
    save_as_jpg: bool = True,
) -> DotDict:
    """Extract comprehensive data from PDF."""
    result = {
        "pdf_path": lpath,
        "filename": os.path.basename(lpath),
        "backend": backend,
        "extraction_params": {
            "clean_text": clean,
            "extract_images": extract_images,
        },
    }

    # Extract all components
    try:
        result["full_text"] = _extract_text(lpath, backend, clean)
        result["sections"] = _extract_sections(lpath, backend, clean)
        result["metadata"] = _extract_metadata(lpath, backend)
        result["pages"] = _extract_pages(lpath, backend, clean)

        # Extract tables if available
        if PDFPLUMBER_AVAILABLE and PANDAS_AVAILABLE:
            try:
                result["tables"] = _extract_tables(lpath, table_settings)
            except Exception as e:
                logger.warning(f"Could not extract tables: {e}")
                result["tables"] = {}

        # Extract images if requested and available
        if extract_images and FITZ_AVAILABLE:
            try:
                result["images"] = _extract_images(lpath, output_dir, save_as_jpg)
            except Exception as e:
                logger.warning(f"Could not extract images: {e}")
                result["images"] = []

        # Calculate statistics
        result["stats"] = {
            "total_chars": len(result["full_text"]),
            "total_words": len(result["full_text"].split()),
            "total_pages": len(result["pages"]),
            "num_sections": len(result["sections"]),
            "num_tables": sum(
                len(tables) for tables in result.get("tables", {}).values()
            ),
            "num_images": len(result.get("images", [])),
            "avg_words_per_page": (
                len(result["full_text"].split()) / len(result["pages"])
                if result["pages"]
                else 0
            ),
        }

    except Exception as e:
        logger.error(f"Error in full extraction: {e}")
        result["error"] = str(e)

    return DotDict(result)


def _clean_pdf_text(text: str) -> str:
    """Clean extracted PDF text."""
    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)

    # Fix hyphenated words at line breaks
    text = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1\2", text)

    # Remove page numbers (common patterns)
    text = re.sub(r"\n\s*\d+\s*\n", "\n", text)
    text = re.sub(r"Page\s+\d+\s+of\s+\d+", "", text, flags=re.IGNORECASE)

    # Clean up common PDF artifacts
    text = text.replace("\x00", "")  # Null bytes
    text = re.sub(r"[\x01-\x1f\x7f-\x9f]", "", text)  # Control characters

    # Normalize quotes and dashes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(""", "'").replace(""", "'")
    text = text.replace("–", "-").replace("—", "-")

    # Remove multiple consecutive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def _calculate_file_hash(lpath: str) -> str:
    """Calculate MD5 hash of file."""
    hash_md5 = hashlib.md5()
    with open(lpath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# EOF
