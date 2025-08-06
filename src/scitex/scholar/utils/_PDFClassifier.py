#!/usr/bin/env python3
"""
PDF Classification Utility

Properly classifies detected PDFs as main article vs supplementary material
based on URL patterns, link text, and context analysis.
"""

from typing import List, Dict, Any
import re
import logging

logger = logging.getLogger(__name__)


class PDFClassifier:
    """
    Classifies PDF URLs as main article, supplementary, or other types.
    
    Uses URL patterns, link text, and context to determine PDF type with
    high accuracy based on publisher-specific patterns.
    """
    
    def __init__(self):
        # Publisher-specific patterns for main article PDFs
        self.main_pdf_patterns = [
            # Science.org patterns
            r'/doi/pdf/10\.',  # Standard DOI PDF URLs
            r'/doi/epdf/10\.',  # Electronic PDF URLs
            
            # Nature patterns
            r'/articles/[^/]+\.pdf$',
            r'/content/pdf/[^/]+\.pdf$',
            
            # Springer patterns
            r'/article/10\.[^/]+/[^/]+\.pdf$',
            
            # Wiley patterns
            r'/doi/pdf/10\.[^/]+/[^/]+$',
            
            # General patterns
            r'/pdf/10\.',  # DOI-based PDF URLs
            r'\.pdf$',     # Direct PDF files (lowest priority)
        ]
        
        # Patterns that indicate supplementary material
        self.supplementary_patterns = [
            r'/suppl/',
            r'/supplement/',
            r'/supporting',
            r'_supplement\.pdf$',
            r'_supp\.pdf$',
            r'_si\.pdf$',  # Supporting Information
            r'/sm\.pdf$',  # Supplementary Material
            r'suppl_file',
        ]
        
        # Text patterns that indicate main article
        self.main_text_indicators = [
            'download pdf',
            'full text pdf',
            'pdf download',
            'article pdf',
            'view pdf',
            'pdf version',
        ]
        
        # Text patterns that indicate supplementary material
        self.supplementary_text_indicators = [
            'supplement',
            'supporting',
            'additional',
            'appendix',
            'sup info',
            'si pdf',
            'supp material',
            'revision',
        ]
    
    def classify_pdf_url(self, pdf_url: str, link_text: str = "", context: str = "") -> Dict[str, Any]:
        """
        Classify a single PDF URL.
        
        Args:
            pdf_url: The PDF URL to classify
            link_text: Text of the link (if available)
            context: Surrounding context text (if available)
        
        Returns:
            Dictionary with classification results
        """
        pdf_url_lower = pdf_url.lower()
        link_text_lower = link_text.lower().strip()
        context_lower = context.lower()
        
        # Initialize result
        result = {
            'url': pdf_url,
            'type': 'unknown',
            'confidence': 0.0,
            'is_main': False,
            'is_supplementary': False,
            'reasoning': []
        }
        
        # Check for supplementary patterns first (more specific)
        supplementary_score = 0
        for pattern in self.supplementary_patterns:
            if re.search(pattern, pdf_url_lower):
                supplementary_score += 2
                result['reasoning'].append(f"URL matches supplementary pattern: {pattern}")
        
        for indicator in self.supplementary_text_indicators:
            if indicator in link_text_lower:
                supplementary_score += 1
                result['reasoning'].append(f"Link text contains supplementary indicator: {indicator}")
            if indicator in context_lower:
                supplementary_score += 0.5
                result['reasoning'].append(f"Context contains supplementary indicator: {indicator}")
        
        # Check for main article patterns
        main_score = 0
        for i, pattern in enumerate(self.main_pdf_patterns):
            if re.search(pattern, pdf_url_lower):
                # Earlier patterns are more specific, give higher scores
                weight = len(self.main_pdf_patterns) - i
                main_score += weight
                result['reasoning'].append(f"URL matches main PDF pattern: {pattern} (weight: {weight})")
                break  # Only count the best match
        
        for indicator in self.main_text_indicators:
            if indicator in link_text_lower:
                main_score += 1
                result['reasoning'].append(f"Link text contains main PDF indicator: {indicator}")
        
        # Special checks for Science.org
        if 'science.org' in pdf_url_lower:
            if '/doi/pdf/' in pdf_url_lower and 'suppl' not in pdf_url_lower:
                main_score += 3
                result['reasoning'].append("Science.org main article pattern: /doi/pdf/ without suppl")
        
        # Determine classification
        if supplementary_score > main_score:
            result['type'] = 'supplementary'
            result['is_supplementary'] = True
            result['confidence'] = min(supplementary_score / 4.0, 1.0)
        elif main_score > supplementary_score:
            result['type'] = 'main'
            result['is_main'] = True
            result['confidence'] = min(main_score / 5.0, 1.0)
        else:
            result['type'] = 'unknown'
            result['confidence'] = 0.0
        
        return result
    
    def classify_pdf_list(self, pdf_urls: List[str], link_texts: List[str] = None, contexts: List[str] = None) -> Dict[str, Any]:
        """
        Classify a list of PDF URLs and return organized results.
        
        Args:
            pdf_urls: List of PDF URLs to classify
            link_texts: Optional list of link texts (same order as URLs)
            contexts: Optional list of context texts (same order as URLs)
        
        Returns:
            Dictionary with organized classification results
        """
        if not pdf_urls:
            return {
                'main_pdfs': [],
                'supplementary_pdfs': [],
                'unknown_pdfs': [],
                'total_count': 0,
                'main_count': 0,
                'supplementary_count': 0,
                'unknown_count': 0
            }
        
        # Ensure lists are same length
        link_texts = link_texts or [''] * len(pdf_urls)
        contexts = contexts or [''] * len(pdf_urls)
        
        # Classify each PDF
        main_pdfs = []
        supplementary_pdfs = []
        unknown_pdfs = []
        
        for i, pdf_url in enumerate(pdf_urls):
            link_text = link_texts[i] if i < len(link_texts) else ''
            context = contexts[i] if i < len(contexts) else ''
            
            classification = self.classify_pdf_url(pdf_url, link_text, context)
            
            if classification['is_main']:
                main_pdfs.append(classification)
            elif classification['is_supplementary']:
                supplementary_pdfs.append(classification)
            else:
                unknown_pdfs.append(classification)
        
        # Sort by confidence (highest first)
        main_pdfs.sort(key=lambda x: x['confidence'], reverse=True)
        supplementary_pdfs.sort(key=lambda x: x['confidence'], reverse=True)
        
        logger.info(f"📊 PDF Classification Results: {len(main_pdfs)} main, {len(supplementary_pdfs)} supplementary, {len(unknown_pdfs)} unknown")
        
        return {
            'main_pdfs': main_pdfs,
            'supplementary_pdfs': supplementary_pdfs,
            'unknown_pdfs': unknown_pdfs,
            'total_count': len(pdf_urls),
            'main_count': len(main_pdfs),
            'supplementary_count': len(supplementary_pdfs),
            'unknown_count': len(unknown_pdfs)
        }
    
    def get_best_main_pdf(self, pdf_urls: List[str], link_texts: List[str] = None, contexts: List[str] = None) -> str:
        """
        Get the most likely main PDF URL from a list.
        
        Returns:
            The URL of the best main PDF candidate, or empty string if none found
        """
        classification_result = self.classify_pdf_list(pdf_urls, link_texts, contexts)
        
        if classification_result['main_pdfs']:
            best_main = classification_result['main_pdfs'][0]  # Already sorted by confidence
            logger.info(f"🎯 Best main PDF: {best_main['url']} (confidence: {best_main['confidence']:.2f})")
            return best_main['url']
        
        logger.warning("❌ No main PDF identified from URL list")
        return ""