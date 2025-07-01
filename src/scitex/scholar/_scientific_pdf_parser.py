#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-06 03:00:00 (ywatanabe)"
# File: src/scitex_scholar/scientific_pdf_parser.py

"""
Scientific PDF parser for research papers.

This module provides specialized parsing for scientific PDF documents,
extracting structured information including sections, citations, figures,
tables, and mathematical content.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
import pdfplumber
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ScientificPaper:
    """Data structure for parsed scientific paper."""
    title: str
    authors: List[str]
    abstract: str
    sections: Dict[str, str]
    keywords: List[str]
    references: List[Dict[str, str]]
    figures: List[Dict[str, str]]
    tables: List[Dict[str, str]]
    equations: List[str]
    metadata: Dict[str, Any]
    citations_in_text: List[str]
    methods_mentioned: List[str]
    datasets_mentioned: List[str]
    metrics_reported: Dict[str, float]


class ScientificPDFParser:
    """Parser optimized for scientific PDF papers."""
    
    def __init__(self):
        """Initialize parser with scientific paper patterns."""
        self._compile_patterns()
        
    def _compile_patterns(self):
        """Compile regex patterns for scientific content."""
        # Section headers
        self.section_patterns = {
            'abstract': re.compile(r'^abstract\s*$', re.IGNORECASE | re.MULTILINE),
            'introduction': re.compile(r'^(?:1\.?\s*)?introduction\s*$', re.IGNORECASE | re.MULTILINE),
            'related_work': re.compile(r'^(?:2\.?\s*)?(?:related work|literature review|background)\s*$', re.IGNORECASE | re.MULTILINE),
            'methods': re.compile(r'^(?:3\.?\s*)?(?:method|methodology|methods|approach)\s*$', re.IGNORECASE | re.MULTILINE),
            'experiments': re.compile(r'^(?:4\.?\s*)?(?:experiments?|experimental setup|evaluation)\s*$', re.IGNORECASE | re.MULTILINE),
            'results': re.compile(r'^(?:5\.?\s*)?results?\s*$', re.IGNORECASE | re.MULTILINE),
            'discussion': re.compile(r'^(?:6\.?\s*)?discussion\s*$', re.IGNORECASE | re.MULTILINE),
            'conclusion': re.compile(r'^(?:7\.?\s*)?conclusions?\s*$', re.IGNORECASE | re.MULTILINE),
            'references': re.compile(r'^references?\s*$', re.IGNORECASE | re.MULTILINE),
        }
        
        # Citation patterns
        self.citation_pattern = re.compile(r'\[(\d+(?:,\s*\d+)*)\]|\(([A-Za-z]+(?:\s+et\s+al\.?)?,?\s*\d{4}[a-z]?)\)')
        
        # Figure/Table references
        self.figure_pattern = re.compile(r'(?:Figure|Fig\.?)\s*(\d+)', re.IGNORECASE)
        self.table_pattern = re.compile(r'Table\s*(\d+)', re.IGNORECASE)
        
        # Common ML/AI methods
        self.method_patterns = [
            re.compile(r'\b(?:CNN|Convolutional Neural Network)\b', re.IGNORECASE),
            re.compile(r'\b(?:RNN|Recurrent Neural Network)\b', re.IGNORECASE),
            re.compile(r'\b(?:LSTM|Long Short-Term Memory)\b', re.IGNORECASE),
            re.compile(r'\b(?:Transformer|BERT|GPT)\b', re.IGNORECASE),
            re.compile(r'\b(?:ResNet|VGG|AlexNet|EfficientNet)\b', re.IGNORECASE),
            re.compile(r'\b(?:SVM|Support Vector Machine)\b', re.IGNORECASE),
            re.compile(r'\b(?:Random Forest|XGBoost|Gradient Boosting)\b', re.IGNORECASE),
        ]
        
        # Dataset patterns
        self.dataset_patterns = [
            re.compile(r'\b(?:ImageNet|CIFAR-?\d+|MNIST|Fashion-MNIST)\b', re.IGNORECASE),
            re.compile(r'\b(?:COCO|Pascal VOC|ADE20K)\b', re.IGNORECASE),
            re.compile(r'\b(?:WikiText|GLUE|SQuAD)\b', re.IGNORECASE),
            re.compile(r'\b(?:ChestX-ray14|MIMIC-CXR|NIH Chest X-ray)\b', re.IGNORECASE),
        ]
        
        # Metrics patterns
        self.metric_patterns = {
            'accuracy': re.compile(r'accuracy[:\s]+(\d+\.?\d*)\s*%?', re.IGNORECASE),
            'precision': re.compile(r'precision[:\s]+(\d+\.?\d*)\s*%?', re.IGNORECASE),
            'recall': re.compile(r'recall[:\s]+(\d+\.?\d*)\s*%?', re.IGNORECASE),
            'f1_score': re.compile(r'f1[-\s]?score[:\s]+(\d+\.?\d*)', re.IGNORECASE),
            'auc': re.compile(r'AUC[:\s]+(\d+\.?\d*)', re.IGNORECASE),
            'map': re.compile(r'mAP[:\s]+(\d+\.?\d*)', re.IGNORECASE),
        }
        
    def parse_pdf(self, pdf_path: Path) -> ScientificPaper:
        """
        Parse a scientific PDF paper.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            ScientificPaper object with extracted information
        """
        logger.info(f"Parsing scientific PDF: {pdf_path}")
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Extract text from all pages
                full_text = ""
                page_texts = []
                
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text() or ""
                    page_texts.append(page_text)
                    full_text += page_text + "\n"
                
                # Parse different components
                title = self._extract_title(page_texts[0] if page_texts else "")
                authors = self._extract_authors(page_texts[0] if page_texts else "")
                abstract = self._extract_abstract(full_text)
                sections = self._extract_sections(full_text)
                keywords = self._extract_keywords(full_text)
                references = self._extract_references(full_text)
                
                # Extract scientific content
                citations = self._extract_citations(full_text)
                methods = self._extract_methods(full_text)
                datasets = self._extract_datasets(full_text)
                metrics = self._extract_metrics(full_text)
                
                # Extract figures and tables
                figures = self._extract_figures(full_text)
                tables = self._extract_tables(full_text)
                equations = self._extract_equations(full_text)
                
                # Build metadata
                metadata = {
                    'file_path': str(pdf_path),
                    'file_name': pdf_path.name,
                    'page_count': len(pdf.pages),
                    'parsed_date': datetime.now().isoformat(),
                    'file_size': pdf_path.stat().st_size,
                }
                
                return ScientificPaper(
                    title=title,
                    authors=authors,
                    abstract=abstract,
                    sections=sections,
                    keywords=keywords,
                    references=references,
                    figures=figures,
                    tables=tables,
                    equations=equations,
                    metadata=metadata,
                    citations_in_text=citations,
                    methods_mentioned=methods,
                    datasets_mentioned=datasets,
                    metrics_reported=metrics
                )
                
        except Exception as e:
            logger.error(f"Error parsing PDF {pdf_path}: {str(e)}")
            raise
    
    def _extract_title(self, first_page: str) -> str:
        """Extract paper title from first page."""
        lines = first_page.split('\n')[:10]  # Title usually in first 10 lines
        
        # Look for the longest line that's not all caps (likely title)
        title_candidates = []
        for line in lines:
            line = line.strip()
            if len(line) > 10 and not line.isupper():
                title_candidates.append(line)
        
        # Return longest candidate
        return max(title_candidates, key=len) if title_candidates else "Unknown Title"
    
    def _extract_authors(self, first_page: str) -> List[str]:
        """Extract author names from first page."""
        # Simple heuristic: look for lines with names (contain commas or "and")
        lines = first_page.split('\n')[2:20]  # Authors usually after title
        
        authors = []
        for line in lines:
            if (',' in line or ' and ' in line) and len(line) < 200:
                # Clean and split author names
                line = re.sub(r'[0-9\*\†]', '', line)  # Remove footnote markers
                line = re.sub(r'\s+', ' ', line.strip())
                
                if ',' in line:
                    authors.extend([a.strip() for a in line.split(',') if a.strip()])
                elif ' and ' in line:
                    authors.extend([a.strip() for a in line.split(' and ') if a.strip()])
                
                if len(authors) > 0:
                    break
        
        return authors[:10]  # Limit to 10 authors
    
    def _extract_abstract(self, text: str) -> str:
        """Extract abstract section."""
        # Find abstract section
        abstract_match = self.section_patterns['abstract'].search(text)
        if abstract_match:
            start = abstract_match.end()
            
            # Find next section or keywords
            next_section = float('inf')
            for pattern in self.section_patterns.values():
                match = pattern.search(text[start:start+3000])
                if match:
                    next_section = min(next_section, match.start())
            
            # Also check for keywords
            keywords_match = re.search(r'^keywords?:', text[start:start+3000], re.IGNORECASE | re.MULTILINE)
            if keywords_match:
                next_section = min(next_section, keywords_match.start())
            
            if next_section < float('inf'):
                abstract = text[start:start+next_section].strip()
                return ' '.join(abstract.split())  # Clean whitespace
        
        return ""
    
    def _extract_sections(self, text: str) -> Dict[str, str]:
        """Extract all sections from paper."""
        sections = {}
        
        # Find all section positions
        section_positions = []
        for section_name, pattern in self.section_patterns.items():
            matches = list(pattern.finditer(text))
            for match in matches:
                section_positions.append((match.start(), match.end(), section_name))
        
        # Sort by position
        section_positions.sort(key=lambda x: x[0])
        
        # Extract content between sections
        for i, (start, end, name) in enumerate(section_positions):
            # Get content until next section
            if i + 1 < len(section_positions):
                content_end = section_positions[i + 1][0]
            else:
                content_end = len(text)
            
            content = text[end:content_end].strip()
            if content and len(content) > 50:  # Minimum content length
                sections[name] = ' '.join(content.split()[:1000])  # Limit length
        
        return sections
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from paper."""
        keywords = []
        
        # Look for explicit keywords section
        keywords_match = re.search(r'keywords?:?\s*([^\n]+)', text[:3000], re.IGNORECASE)
        if keywords_match:
            keywords_text = keywords_match.group(1)
            # Split by common delimiters
            keywords = re.split(r'[;,·•]', keywords_text)
            keywords = [k.strip() for k in keywords if k.strip()]
        
        return keywords[:20]  # Limit keywords
    
    def _extract_references(self, text: str) -> List[Dict[str, str]]:
        """Extract references from paper."""
        references = []
        
        # Find references section
        ref_match = self.section_patterns['references'].search(text)
        if ref_match:
            ref_text = text[ref_match.end():]
            
            # Simple reference extraction (numbered)
            ref_pattern = re.compile(r'\[(\d+)\]\s*([^\[\]]+?)(?=\[\d+\]|$)', re.DOTALL)
            matches = ref_pattern.findall(ref_text)
            
            for ref_num, ref_content in matches[:100]:  # Limit to 100 refs
                # Try to parse author, title, year
                ref_data = {
                    'number': ref_num,
                    'raw': ref_content.strip()
                }
                
                # Extract year
                year_match = re.search(r'\b(19|20)\d{2}\b', ref_content)
                if year_match:
                    ref_data['year'] = year_match.group()
                
                references.append(ref_data)
        
        return references
    
    def _extract_citations(self, text: str) -> List[str]:
        """Extract in-text citations."""
        citations = []
        matches = self.citation_pattern.findall(text)
        
        for match in matches:
            if match[0]:  # Numbered citation
                citations.extend([f"[{num.strip()}]" for num in match[0].split(',')])
            elif match[1]:  # Author-year citation
                citations.append(match[1])
        
        return list(set(citations))[:200]  # Unique citations, limited
    
    def _extract_methods(self, text: str) -> List[str]:
        """Extract mentioned methods/algorithms."""
        methods = []
        
        for pattern in self.method_patterns:
            matches = pattern.findall(text)
            methods.extend(matches)
        
        # Clean and deduplicate
        methods = list(set([m.strip() for m in methods if m.strip()]))
        return methods
    
    def _extract_datasets(self, text: str) -> List[str]:
        """Extract mentioned datasets."""
        datasets = []
        
        for pattern in self.dataset_patterns:
            matches = pattern.findall(text)
            datasets.extend(matches)
        
        # Clean and deduplicate
        datasets = list(set([d.strip() for d in datasets if d.strip()]))
        return datasets
    
    def _extract_metrics(self, text: str) -> Dict[str, float]:
        """Extract reported metrics."""
        metrics = {}
        
        for metric_name, pattern in self.metric_patterns.items():
            matches = pattern.findall(text)
            if matches:
                # Get the highest reported value
                values = []
                for match in matches:
                    try:
                        value = float(match.replace('%', ''))
                        if value <= 100:  # Sanity check
                            values.append(value)
                    except ValueError:
                        continue
                
                if values:
                    metrics[metric_name] = max(values)
        
        return metrics
    
    def _extract_figures(self, text: str) -> List[Dict[str, str]]:
        """Extract figure references and captions."""
        figures = []
        
        # Find figure captions
        fig_caption_pattern = re.compile(
            r'(?:Figure|Fig\.?)\s*(\d+)[:\.]?\s*([^\n]{10,200})', 
            re.IGNORECASE
        )
        
        matches = fig_caption_pattern.findall(text)
        for fig_num, caption in matches[:20]:  # Limit figures
            figures.append({
                'number': fig_num,
                'caption': caption.strip()
            })
        
        return figures
    
    def _extract_tables(self, text: str) -> List[Dict[str, str]]:
        """Extract table references and captions."""
        tables = []
        
        # Find table captions
        table_caption_pattern = re.compile(
            r'Table\s*(\d+)[:\.]?\s*([^\n]{10,200})', 
            re.IGNORECASE
        )
        
        matches = table_caption_pattern.findall(text)
        for table_num, caption in matches[:20]:  # Limit tables
            tables.append({
                'number': table_num,
                'caption': caption.strip()
            })
        
        return tables
    
    def _extract_equations(self, text: str) -> List[str]:
        """Extract mathematical equations."""
        equations = []
        
        # Look for numbered equations
        eq_pattern = re.compile(r'\(\d+\)\s*([^\n]+)')
        matches = eq_pattern.findall(text)
        
        for eq in matches[:20]:  # Limit equations
            eq = eq.strip()
            if any(c in eq for c in ['=', '∑', '∫', 'α', 'β', 'θ']):
                equations.append(eq)
        
        return equations
    
    def to_search_document(self, paper: ScientificPaper) -> Dict[str, Any]:
        """Convert ScientificPaper to searchable document format."""
        # Combine all searchable text
        searchable_content = f"""
Title: {paper.title}

Authors: {', '.join(paper.authors)}

Abstract: {paper.abstract}

Keywords: {', '.join(paper.keywords)}

Methods: {', '.join(paper.methods_mentioned)}

Datasets: {', '.join(paper.datasets_mentioned)}

{' '.join(paper.sections.values())}
        """
        
        return {
            'content': searchable_content.strip(),
            'metadata': {
                'title': paper.title,
                'authors': paper.authors,
                'year': paper.metadata.get('year'),
                'keywords': paper.keywords,
                'methods': paper.methods_mentioned,
                'datasets': paper.datasets_mentioned,
                'metrics': paper.metrics_reported,
                'num_references': len(paper.references),
                'num_figures': len(paper.figures),
                'num_tables': len(paper.tables),
                **paper.metadata
            },
            'sections': paper.sections,
            'references': paper.references
        }


# EOF