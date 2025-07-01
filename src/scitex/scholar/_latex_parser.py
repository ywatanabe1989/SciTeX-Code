#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-22 16:35:00 (ywatanabe)"
# File: src/scitex_scholar/latex_parser.py

"""
LaTeX parsing module for scientific documents.

This module provides functionality for parsing LaTeX-specific content including
commands, environments, mathematical expressions, and citations from scientific papers.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from functools import lru_cache


class LaTeXParser:
    """
    LaTeX parser for scientific documents.
    
    Provides methods for extracting LaTeX commands, environments, mathematical
    expressions, and citations from LaTeX source documents.
    """
    
    def __init__(self):
        """Initialize LaTeXParser with optimized regex patterns for common LaTeX constructs."""
        # Compile all regex patterns once for better performance
        self._compile_patterns()
        
        # Cache for frequently accessed environments
        self._environment_cache: Dict[str, List[Dict[str, Any]]] = {}
        
    def _compile_patterns(self) -> None:
        """Compile all regex patterns for optimal performance."""
        # Basic command pattern: \command{content} or \command[options]{content}
        self.command_pattern = re.compile(
            r'\\([a-zA-Z]+)(?:\[[^\]]*\])?\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}'
        )
        
        # Environment pattern: \begin{env}...\end{env}
        self.environment_pattern = re.compile(
            r'\\begin\{([^}]+)\}(.*?)\\end\{\1\}',
            re.DOTALL
        )
        
        # Math patterns - optimized for common cases
        self.inline_math_pattern = re.compile(r'\$([^$]+)\$')
        self.display_math_pattern = re.compile(r'\$\$([^$]+)\$\$')
        
        # Citation patterns - combined for efficiency
        self.citation_patterns = {
            'cite': re.compile(r'\\cite\{([^}]+)\}'),
            'citep': re.compile(r'\\citep\{([^}]+)\}'),
            'citet': re.compile(r'\\citet\{([^}]+)\}'),
            'citealp': re.compile(r'\\citealp\{([^}]+)\}'),
            'citealt': re.compile(r'\\citealt\{([^}]+)\}'),
        }
        
        # Optimized cleanup patterns with precompiled regex
        self.cleanup_patterns = [
            (re.compile(r'\\textbf\{([^}]+)\}'), r'\1'),  # Bold text
            (re.compile(r'\\textit\{([^}]+)\}'), r'\1'),  # Italic text
            (re.compile(r'\\emph\{([^}]+)\}'), r'\1'),    # Emphasized text
            (re.compile(r'\\footnote\{[^}]+\}'), ''),     # Remove footnotes
            (re.compile(r'\\label\{[^}]+\}'), ''),        # Remove labels
            (re.compile(r'\\ref\{[^}]+\}'), '[REF]'),     # Replace references
            (re.compile(r'\\url\{[^}]+\}'), '[URL]'),     # Replace URLs
        ]
    
    def extract_commands(self, latex_text: str) -> List[Dict[str, str]]:
        """
        Extract LaTeX commands from text.
        
        Args:
            latex_text: LaTeX source text
            
        Returns:
            List of dictionaries containing command information
        """
        commands = []
        
        for match in self.command_pattern.finditer(latex_text):
            command_name = match.group(1)
            command_content = match.group(2)
            
            commands.append({
                'command': command_name,
                'content': command_content,
                'start': match.start(),
                'end': match.end()
            })
        
        return commands
    
    @lru_cache(maxsize=128)
    def _get_environment_pattern(self, env_name: str) -> re.Pattern:
        """Get compiled regex pattern for specific environment (cached)."""
        return re.compile(
            rf'\\begin\{{{re.escape(env_name)}\}}(.*?)\\end\{{{re.escape(env_name)}\}}',
            re.DOTALL
        )
    
    def extract_environments(self, latex_text: str) -> List[Dict[str, Any]]:
        """
        Extract LaTeX environments from text with optimized pattern matching.
        
        Args:
            latex_text: LaTeX source text
            
        Returns:
            List of dictionaries containing environment information
        """
        # Check cache first for performance
        text_hash = hash(latex_text)
        if text_hash in self._environment_cache:
            return self._environment_cache[text_hash]
        
        environments = []
        processed_positions = set()
        
        # Priority environments - extract these first for better performance
        priority_environments = [
            'abstract', 'figure', 'table', 'equation', 'align', 'gather'
        ]
        
        # Extract priority environments first
        for env_name in priority_environments:
            pattern = self._get_environment_pattern(env_name)
            for match in pattern.finditer(latex_text):
                pos_key = (match.start(), match.end())
                if pos_key not in processed_positions:
                    environments.append({
                        'name': env_name,
                        'content': match.group(1).strip(),
                        'start': match.start(),
                        'end': match.end()
                    })
                    processed_positions.add(pos_key)
        
        # Extract remaining environments using general pattern
        for match in self.environment_pattern.finditer(latex_text):
            pos_key = (match.start(), match.end())
            if pos_key not in processed_positions:
                environments.append({
                    'name': match.group(1),
                    'content': match.group(2).strip(),
                    'start': match.start(),
                    'end': match.end()
                })
                processed_positions.add(pos_key)
        
        # Sort by position for consistent ordering
        environments.sort(key=lambda x: x['start'])
        
        # Cache result for future use
        self._environment_cache[text_hash] = environments
        
        return environments
    
    def extract_math_expressions(self, latex_text: str) -> List[Dict[str, str]]:
        """
        Extract mathematical expressions from LaTeX text with optimized pattern matching.
        
        Args:
            latex_text: LaTeX source text
            
        Returns:
            List of dictionaries containing math expression information
        """
        math_expressions = []
        processed_positions = set()
        
        # Extract inline math ($...$) - most common, check first
        for match in self.inline_math_pattern.finditer(latex_text):
            pos_key = (match.start(), match.end())
            if pos_key not in processed_positions:
                math_expressions.append({
                    'type': 'inline',
                    'content': match.group(1),
                    'start': match.start(),
                    'end': match.end()
                })
                processed_positions.add(pos_key)
        
        # Extract display math ($$...$$)
        for match in self.display_math_pattern.finditer(latex_text):
            pos_key = (match.start(), match.end())
            if pos_key not in processed_positions:
                math_expressions.append({
                    'type': 'display',
                    'content': match.group(1),
                    'start': match.start(),
                    'end': match.end()
                })
                processed_positions.add(pos_key)
        
        # Extract math environments - use cached patterns for performance
        math_environments = ['equation', 'align', 'gather', 'multline', 'eqnarray']
        for env_name in math_environments:
            pattern = self._get_environment_pattern(env_name)
            for match in pattern.finditer(latex_text):
                pos_key = (match.start(), match.end())
                if pos_key not in processed_positions:
                    math_expressions.append({
                        'type': env_name,
                        'content': match.group(1).strip(),
                        'start': match.start(),
                        'end': match.end()
                    })
                    processed_positions.add(pos_key)
        
        # Sort by position for consistency
        math_expressions.sort(key=lambda x: x['start'])
        
        return math_expressions
    
    def extract_citations(self, latex_text: str) -> List[Dict[str, str]]:
        """
        Extract citations from LaTeX text.
        
        Args:
            latex_text: LaTeX source text
            
        Returns:
            List of dictionaries containing citation information
        """
        citations = []
        
        for cite_type, pattern in self.citation_patterns.items():
            for match in pattern.finditer(latex_text):
                citation_keys = match.group(1).split(',')
                for key in citation_keys:
                    citations.append({
                        'type': cite_type,
                        'key': key.strip(),
                        'start': match.start(),
                        'end': match.end()
                    })
        
        return citations
    
    def extract_document_metadata(self, latex_text: str) -> Dict[str, str]:
        """
        Extract metadata from LaTeX document.
        
        Args:
            latex_text: LaTeX source text
            
        Returns:
            Dictionary containing document metadata
        """
        metadata = {}
        
        # Extract title
        title_match = re.search(r'\\title\{([^}]+)\}', latex_text)
        if title_match:
            metadata['title'] = title_match.group(1)
        
        # Extract author
        author_match = re.search(r'\\author\{([^}]+)\}', latex_text)
        if author_match:
            metadata['author'] = author_match.group(1)
        
        # Extract document class
        docclass_match = re.search(r'\\documentclass(?:\[[^\]]*\])?\{([^}]+)\}', latex_text)
        if docclass_match:
            metadata['documentclass'] = docclass_match.group(1)
        
        return metadata
    
    def extract_document_structure(self, latex_text: str) -> Dict[str, Any]:
        """
        Extract document structure (sections, subsections, etc.).
        
        Args:
            latex_text: LaTeX source text
            
        Returns:
            Dictionary containing document structure information
        """
        structure = {'sections': []}
        
        # Section patterns in order of hierarchy
        section_patterns = [
            ('section', re.compile(r'\\section\{([^}]+)\}')),
            ('subsection', re.compile(r'\\subsection\{([^}]+)\}')),
            ('subsubsection', re.compile(r'\\subsubsection\{([^}]+)\}')),
        ]
        
        for section_type, pattern in section_patterns:
            for match in pattern.finditer(latex_text):
                structure['sections'].append({
                    'type': section_type,
                    'title': match.group(1),
                    'start': match.start(),
                    'end': match.end()
                })
        
        # Sort by position in document
        structure['sections'].sort(key=lambda x: x['start'])
        
        return structure
    
    def clean_latex_content(self, latex_text: str) -> str:
        """
        Clean LaTeX content for text processing.
        
        Args:
            latex_text: LaTeX source text
            
        Returns:
            Cleaned text with LaTeX commands removed or converted
        """
        cleaned = latex_text
        
        # Apply cleanup patterns
        for pattern, replacement in self.cleanup_patterns:
            cleaned = pattern.sub(replacement, cleaned)
        
        # Remove remaining simple commands
        cleaned = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', cleaned)
        
        # Remove math expressions for clean text (keep content)
        cleaned = re.sub(r'\$\$([^$]+)\$\$', r'\1', cleaned)
        cleaned = re.sub(r'\$([^$]+)\$', r'\1', cleaned)
        
        # Clean up whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned.strip())
        
        return cleaned
    
    def clear_cache(self) -> None:
        """
        Clear internal caches to free memory.
        
        Useful when processing many different documents or when memory usage
        becomes a concern.
        """
        self._environment_cache.clear()
        self._get_environment_pattern.cache_clear()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about cache usage for performance monitoring.
        
        Returns:
            Dictionary containing cache statistics
        """
        return {
            'environment_cache_size': len(self._environment_cache),
            'pattern_cache_info': self._get_environment_pattern.cache_info()._asdict()
        }
    
    def parse_document(self, latex_text: str) -> Dict[str, Any]:
        """
        Parse a complete LaTeX document.
        
        Args:
            latex_text: LaTeX source text
            
        Returns:
            Dictionary containing all parsed information
        """
        # Extract all components
        metadata = self.extract_document_metadata(latex_text)
        structure = self.extract_document_structure(latex_text)
        environments = self.extract_environments(latex_text)
        math_expressions = self.extract_math_expressions(latex_text)
        citations = self.extract_citations(latex_text)
        
        # Extract specific content sections
        content = {}
        
        # Extract abstract
        for env in environments:
            if env['name'] == 'abstract':
                content['abstract'] = env['content']
                break
        
        # Clean text for general processing
        clean_text = self.clean_latex_content(latex_text)
        
        return {
            'metadata': metadata,
            'structure': structure,
            'content': content,
            'environments': environments,
            'math_expressions': math_expressions,
            'citations': citations,
            'clean_text': clean_text
        }

# EOF