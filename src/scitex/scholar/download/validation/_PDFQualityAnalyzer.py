#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-08-01 14:05:00"
# Author: Claude
# File: _PDFQualityAnalyzer.py

"""
Analyze PDF quality and extract structured content.

This module provides advanced PDF analysis including section extraction,
quality scoring, and content structure analysis.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

try:
    import fitz  # PyMuPDF
except ImportError:
    import pymupdf as fitz

import numpy as np
from scitex import log

logger = log.getLogger(__name__)


@dataclass
class PDFSection:
    """Represents a section in a PDF."""
    title: str
    page_start: int
    page_end: int
    text: str
    level: int = 1
    word_count: int = 0


class PDFQualityAnalyzer:
    """Advanced PDF quality analysis and content extraction."""
    
    def __init__(self):
        """Initialize PDF quality analyzer."""
        # Quality scoring weights
        self.quality_weights = {
            'readable_text': 0.3,
            'proper_structure': 0.2,
            'metadata_present': 0.1,
            'reasonable_length': 0.2,
            'contains_figures': 0.1,
            'contains_references': 0.1
        }
        
        # Section patterns (regex)
        self.section_patterns = [
            # Numbered sections
            (r'^\s*(\d+\.?)\s+([A-Z][A-Za-z\s]+)$', 1),
            (r'^\s*(\d+\.\d+\.?)\s+([A-Za-z\s]+)$', 2),
            (r'^\s*(\d+\.\d+\.\d+\.?)\s+([A-Za-z\s]+)$', 3),
            # Lettered sections
            (r'^\s*([A-Z]\.?)\s+([A-Z][A-Za-z\s]+)$', 1),
            # Roman numerals
            (r'^\s*(I{1,3}|IV|V|VI{0,3}|IX|X)\.\s+([A-Z][A-Za-z\s]+)$', 1),
            # Keywords
            (r'^(Abstract|Introduction|Methods?|Results?|Discussion|Conclusion|References):?$', 1),
            # All caps headers
            (r'^([A-Z\s]{4,50})$', 1)
        ]
        
    def analyze_pdf_quality(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Perform comprehensive PDF quality analysis.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dict with quality analysis results
        """
        try:
            doc = fitz.open(str(pdf_path))
            
            # Extract sections
            sections = self._extract_sections(doc)
            
            # Analyze text quality
            text_quality = self._analyze_text_quality(doc)
            
            # Check for figures/tables
            media_analysis = self._analyze_media_content(doc)
            
            # Analyze metadata
            metadata_quality = self._analyze_metadata(doc)
            
            # Check references
            has_references = self._check_references(sections)
            
            # Calculate quality score
            quality_score = self._calculate_quality_score({
                'readable_text': text_quality['readable_ratio'] > 0.8,
                'proper_structure': len(sections) >= 4,
                'metadata_present': metadata_quality['has_essential'],
                'reasonable_length': doc.page_count >= 4 and text_quality['total_words'] > 2000,
                'contains_figures': media_analysis['figure_count'] > 0,
                'contains_references': has_references
            })
            
            # Compile results
            results = {
                'quality_score': quality_score,
                'page_count': doc.page_count,
                'sections': [self._section_to_dict(s) for s in sections],
                'text_quality': text_quality,
                'media_analysis': media_analysis,
                'metadata_quality': metadata_quality,
                'has_references': has_references,
                'file_size_mb': pdf_path.stat().st_size / (1024 * 1024),
                'recommendations': self._generate_recommendations(quality_score, sections, text_quality)
            }
            
            doc.close()
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing PDF quality: {e}")
            return {
                'error': str(e),
                'quality_score': 0.0
            }
            
    def _extract_sections(self, doc: fitz.Document) -> List[PDFSection]:
        """Extract sections from PDF document."""
        sections = []
        current_section = None
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            lines = text.split('\n')
            
            for line in lines:
                line_stripped = line.strip()
                
                # Check if line matches section pattern
                for pattern, level in self.section_patterns:
                    match = re.match(pattern, line_stripped, re.IGNORECASE)
                    if match:
                        # Save previous section
                        if current_section:
                            current_section.page_end = page_num
                            current_section.word_count = len(current_section.text.split())
                            sections.append(current_section)
                        
                        # Start new section
                        title = match.group(2) if match.lastindex >= 2 else match.group(1)
                        current_section = PDFSection(
                            title=title.strip(),
                            page_start=page_num,
                            page_end=page_num,
                            text="",
                            level=level
                        )
                        break
                
                # Add text to current section
                if current_section and line_stripped:
                    current_section.text += line + "\n"
        
        # Save last section
        if current_section:
            current_section.page_end = len(doc) - 1
            current_section.word_count = len(current_section.text.split())
            sections.append(current_section)
        
        return sections
        
    def _analyze_text_quality(self, doc: fitz.Document) -> Dict[str, Any]:
        """Analyze text quality and readability."""
        total_chars = 0
        total_words = 0
        readable_chars = 0
        
        # Characters that indicate readable text
        readable_pattern = re.compile(r'[a-zA-Z0-9\s\.,;:\'\"\-\(\)]')
        
        for page in doc:
            text = page.get_text()
            total_chars += len(text)
            total_words += len(text.split())
            readable_chars += len(readable_pattern.findall(text))
        
        return {
            'total_chars': total_chars,
            'total_words': total_words,
            'readable_chars': readable_chars,
            'readable_ratio': readable_chars / total_chars if total_chars > 0 else 0,
            'avg_words_per_page': total_words / len(doc) if len(doc) > 0 else 0
        }
        
    def _analyze_media_content(self, doc: fitz.Document) -> Dict[str, Any]:
        """Analyze figures, tables, and other media."""
        figure_count = 0
        table_indicators = 0
        image_count = 0
        
        for page_num, page in enumerate(doc):
            # Count images
            image_list = page.get_images()
            image_count += len(image_list)
            
            # Look for figure/table captions
            text = page.get_text()
            figure_count += len(re.findall(r'Figure\s+\d+|Fig\.\s*\d+', text, re.IGNORECASE))
            table_indicators += len(re.findall(r'Table\s+\d+', text, re.IGNORECASE))
        
        return {
            'figure_count': figure_count,
            'table_count': table_indicators,
            'image_count': image_count,
            'has_visual_content': (figure_count + table_indicators + image_count) > 0
        }
        
    def _analyze_metadata(self, doc: fitz.Document) -> Dict[str, Any]:
        """Analyze PDF metadata quality."""
        metadata = doc.metadata
        
        essential_fields = ['title', 'author', 'subject', 'keywords']
        present_fields = [field for field in essential_fields if metadata.get(field)]
        
        return {
            'metadata': metadata,
            'has_essential': len(present_fields) >= 2,
            'present_fields': present_fields,
            'missing_fields': [f for f in essential_fields if f not in present_fields]
        }
        
    def _check_references(self, sections: List[PDFSection]) -> bool:
        """Check if document contains references section."""
        reference_titles = ['references', 'bibliography', 'works cited', 'literature']
        
        for section in sections:
            if any(ref in section.title.lower() for ref in reference_titles):
                # Additional check: references usually have many numbers/years
                year_count = len(re.findall(r'\b(19|20)\d{2}\b', section.text))
                return year_count > 5  # Arbitrary threshold
                
        return False
        
    def _calculate_quality_score(self, criteria: Dict[str, bool]) -> float:
        """Calculate overall quality score."""
        score = 0.0
        
        for criterion, met in criteria.items():
            if criterion in self.quality_weights:
                if met:
                    score += self.quality_weights[criterion]
                    
        return round(score, 2)
        
    def _section_to_dict(self, section: PDFSection) -> Dict[str, Any]:
        """Convert PDFSection to dictionary."""
        return {
            'title': section.title,
            'page_start': section.page_start,
            'page_end': section.page_end,
            'level': section.level,
            'word_count': section.word_count,
            'preview': section.text[:200] + '...' if len(section.text) > 200 else section.text
        }
        
    def _generate_recommendations(
        self,
        quality_score: float,
        sections: List[PDFSection],
        text_quality: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        if quality_score < 0.5:
            recommendations.append("Low quality score - verify this is the correct paper")
            
        if not sections:
            recommendations.append("No clear sections found - may be poorly formatted")
            
        if text_quality['readable_ratio'] < 0.7:
            recommendations.append("Low text readability - may be scanned or corrupted")
            
        if text_quality['total_words'] < 1000:
            recommendations.append("Very short document - may be abstract only")
            
        if quality_score >= 0.8:
            recommendations.append("High quality PDF - appears to be complete paper")
            
        return recommendations
        
    def extract_structured_content(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Extract structured content from PDF.
        
        Args:
            pdf_path: Path to PDF
            
        Returns:
            Dict with structured content
        """
        try:
            doc = fitz.open(str(pdf_path))
            sections = self._extract_sections(doc)
            
            # Organize content by section type
            structured = {
                'title': self._extract_title(doc),
                'abstract': None,
                'introduction': None,
                'methods': None,
                'results': None,
                'discussion': None,
                'conclusion': None,
                'references': None,
                'other_sections': []
            }
            
            # Map sections to structure
            for section in sections:
                title_lower = section.title.lower()
                
                if 'abstract' in title_lower:
                    structured['abstract'] = section.text
                elif 'introduction' in title_lower:
                    structured['introduction'] = section.text
                elif 'method' in title_lower:
                    structured['methods'] = section.text
                elif 'result' in title_lower:
                    structured['results'] = section.text
                elif 'discussion' in title_lower:
                    structured['discussion'] = section.text
                elif 'conclusion' in title_lower:
                    structured['conclusion'] = section.text
                elif any(ref in title_lower for ref in ['reference', 'bibliography']):
                    structured['references'] = section.text
                else:
                    structured['other_sections'].append({
                        'title': section.title,
                        'content': section.text[:500]  # Preview
                    })
                    
            doc.close()
            return structured
            
        except Exception as e:
            logger.error(f"Error extracting structured content: {e}")
            return {}
            
    def _extract_title(self, doc: fitz.Document) -> Optional[str]:
        """Extract paper title from first page."""
        if len(doc) == 0:
            return None
            
        first_page = doc[0]
        text = first_page.get_text()
        lines = text.split('\n')
        
        # Title is usually in the first few non-empty lines
        for line in lines[:10]:
            line = line.strip()
            if len(line) > 20 and len(line) < 200:  # Reasonable title length
                # Check if it looks like a title (mixed case, no weird chars)
                if re.match(r'^[A-Z][A-Za-z0-9\s\-:,]+$', line):
                    return line
                    
        return None


def analyze_pdf_batch(pdf_paths: List[Path], detailed: bool = False) -> Dict[Path, Dict[str, Any]]:
    """
    Analyze multiple PDFs for quality.
    
    Args:
        pdf_paths: List of PDF paths
        detailed: Whether to include detailed analysis
        
    Returns:
        Dict mapping paths to analysis results
    """
    analyzer = PDFQualityAnalyzer()
    results = {}
    
    for pdf_path in pdf_paths:
        if detailed:
            results[pdf_path] = analyzer.analyze_pdf_quality(pdf_path)
        else:
            # Quick analysis
            analysis = analyzer.analyze_pdf_quality(pdf_path)
            results[pdf_path] = {
                'quality_score': analysis.get('quality_score', 0),
                'page_count': analysis.get('page_count', 0),
                'has_references': analysis.get('has_references', False),
                'recommendations': analysis.get('recommendations', [])
            }
            
    return results