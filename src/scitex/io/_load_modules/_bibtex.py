#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-01-19 14:20:00 (ywatanabe)"
# File: ./src/scitex/io/_load_modules/_bibtex.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/io/_load_modules/_bibtex.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
BibTeX file loading module for SciTeX IO.

This module provides functionality to load and parse .bib files,
returning structured data that can be used by other SciTeX modules.
"""

import re
from scitex import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


def _load_bibtex(lpath: str, **kwargs) -> List[Dict[str, Any]]:
    """
    Load BibTeX file and parse entries.
    
    Args:
        lpath: Path to the .bib file
        **kwargs: Additional arguments
            - parse_mode: 'full' (default) or 'basic'
            - encoding: File encoding (default: utf-8)
    
    Returns:
        List of dictionaries, each representing a BibTeX entry
    """
    parse_mode = kwargs.get('parse_mode', 'full')
    encoding = kwargs.get('encoding', 'utf-8')
    
    try:
        # Read file content
        with open(lpath, 'r', encoding=encoding) as f:
            content = f.read()
        
        # Parse BibTeX entries
        entries = _parse_bibtex_content(content, parse_mode)
        
        logger.info(f"Loaded {len(entries)} BibTeX entries from {lpath}")
        return entries
        
    except Exception as e:
        raise ValueError(f"Error loading BibTeX file {lpath}: {str(e)}")


def _parse_bibtex_content(content: str, parse_mode: str = 'full') -> List[Dict[str, Any]]:
    """
    Parse BibTeX content into structured entries.
    
    Args:
        content: BibTeX file content
        parse_mode: 'full' for complete parsing, 'basic' for minimal parsing
    
    Returns:
        List of parsed entries
    """
    entries = []
    
    # Pattern to match BibTeX entries
    entry_pattern = r'@(\w+)\s*\{\s*([^,]+)\s*,(.*?)\n\s*\}'
    matches = re.finditer(entry_pattern, content, re.DOTALL | re.IGNORECASE)
    
    for match in matches:
        entry_type = match.group(1).lower()
        entry_key = match.group(2).strip()
        entry_body = match.group(3)
        
        # Parse entry fields
        entry = {
            'entry_type': entry_type,
            'key': entry_key,
            'fields': {}
        }
        
        if parse_mode == 'full':
            entry['fields'] = _parse_bibtex_fields(entry_body)
        else:
            # Basic parsing - just extract key-value pairs
            entry['fields'] = _parse_bibtex_fields_basic(entry_body)
        
        entries.append(entry)
    
    return entries


def _parse_bibtex_fields(body: str) -> Dict[str, str]:
    """
    Parse BibTeX entry fields with proper handling of nested braces.
    
    Args:
        body: The body of a BibTeX entry
    
    Returns:
        Dictionary of field names to values
    """
    fields = {}
    
    # Pattern to match field = value pairs
    # Handles both {braced} and "quoted" values
    field_pattern = r'(\w+)\s*=\s*(?:\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}|"([^"]*)")'
    
    for match in re.finditer(field_pattern, body):
        field_name = match.group(1).lower()
        # Get value from either braced or quoted group
        field_value = match.group(2) if match.group(2) is not None else match.group(3)
        
        # Clean up the value
        field_value = field_value.strip()
        
        # Handle special characters
        field_value = _unescape_bibtex(field_value)
        
        fields[field_name] = field_value
    
    return fields


def _parse_bibtex_fields_basic(body: str) -> Dict[str, str]:
    """
    Basic parsing of BibTeX fields without special character handling.
    
    Args:
        body: The body of a BibTeX entry
    
    Returns:
        Dictionary of field names to values
    """
    fields = {}
    
    # Simple pattern for basic parsing
    lines = body.strip().split(',')
    
    for line in lines:
        if '=' in line:
            parts = line.split('=', 1)
            if len(parts) == 2:
                field_name = parts[0].strip().lower()
                field_value = parts[1].strip()
                
                # Remove surrounding braces or quotes
                if field_value.startswith('{') and field_value.endswith('}'):
                    field_value = field_value[1:-1]
                elif field_value.startswith('"') and field_value.endswith('"'):
                    field_value = field_value[1:-1]
                
                fields[field_name] = field_value.strip()
    
    return fields


def _unescape_bibtex(text: str) -> str:
    """
    Unescape BibTeX special characters.
    
    Args:
        text: BibTeX text with escaped characters
    
    Returns:
        Unescaped text
    """
    # Common BibTeX escapes
    replacements = {
        r'\&': '&',
        r'\%': '%',
        r'\$': '$',
        r'\#': '#',
        r'\_': '_',
        r'\{': '{',
        r'\}': '}',
        r'~': ' ',  # Non-breaking space
        r'--': '–',  # En dash
        r'---': '—',  # Em dash
    }
    
    for escaped, unescaped in replacements.items():
        text = text.replace(escaped, unescaped)
    
    return text


# Convenience function for loading BibTeX
def load_bibtex(filepath: str, **kwargs) -> List[Dict[str, Any]]:
    """
    Load and parse a BibTeX file.
    
    Args:
        filepath: Path to the .bib file
        **kwargs: Additional arguments passed to _load_bibtex
    
    Returns:
        List of parsed BibTeX entries
    """
    return _load_bibtex(filepath, **kwargs)


# EOF