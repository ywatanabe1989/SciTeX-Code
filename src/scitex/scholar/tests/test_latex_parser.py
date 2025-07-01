#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-05-22 16:30:00 (ywatanabe)"
# File: tests/test_latex_parser.py

"""
Test module for LaTeX parsing functionality.

This module tests the LaTeX-specific parsing capabilities including
command extraction, environment parsing, mathematical expressions,
and citation handling for scientific documents.
"""

import unittest
import sys
sys.path.insert(0, './src')


class TestLaTeXParser(unittest.TestCase):
    """Test suite for LaTeX parser functionality."""
    
    def test_latex_parser_import(self):
        """Test that LaTeX parser module can be imported."""
        try:
            from scitex_scholar.latex_parser import LaTeXParser
        except ImportError:
            self.fail("Failed to import LaTeXParser from scitex_scholar.latex_parser")

    def test_latex_parser_initialization(self):
        """Test LaTeXParser can be initialized with default settings."""
        from scitex_scholar.latex_parser import LaTeXParser
        
        parser = LaTeXParser()
        self.assertIsNotNone(parser)
        self.assertTrue(hasattr(parser, 'parse_document'))
        self.assertTrue(hasattr(parser, 'extract_commands'))
        self.assertTrue(hasattr(parser, 'extract_environments'))
        self.assertTrue(hasattr(parser, 'extract_math_expressions'))

    def test_extract_basic_commands(self):
        """Test extraction of basic LaTeX commands."""
        from scitex_scholar.latex_parser import LaTeXParser
        
        parser = LaTeXParser()
        
        latex_text = r"""
        \documentclass{article}
        \title{Sample Document}
        \author{John Doe}
        \section{Introduction}
        This is the introduction.
        \subsection{Background}
        Some background information.
        """
        
        commands = parser.extract_commands(latex_text)
        
        self.assertIsInstance(commands, list)
        self.assertGreater(len(commands), 0)
        
        # Check for specific commands
        command_names = [cmd['command'] for cmd in commands]
        self.assertIn('documentclass', command_names)
        self.assertIn('title', command_names)
        self.assertIn('author', command_names)
        self.assertIn('section', command_names)
        self.assertIn('subsection', command_names)

    def test_extract_environments(self):
        """Test extraction of LaTeX environments."""
        from scitex_scholar.latex_parser import LaTeXParser
        
        parser = LaTeXParser()
        
        latex_text = r"""
        \begin{abstract}
        This is the abstract of the paper.
        \end{abstract}
        
        \begin{figure}
        \centering
        \includegraphics{image.png}
        \caption{Sample figure}
        \end{figure}
        
        \begin{table}
        \begin{tabular}{cc}
        A & B \\
        1 & 2 \\
        \end{tabular}
        \caption{Sample table}
        \end{table}
        """
        
        environments = parser.extract_environments(latex_text)
        
        self.assertIsInstance(environments, list)
        self.assertGreaterEqual(len(environments), 3)
        
        # Check for specific environments
        env_names = [env['name'] for env in environments]
        self.assertIn('abstract', env_names)
        self.assertIn('figure', env_names)
        self.assertIn('table', env_names)
        
        # Check content extraction
        abstract_env = next(env for env in environments if env['name'] == 'abstract')
        self.assertIn('abstract of the paper', abstract_env['content'])

    def test_extract_math_expressions(self):
        """Test extraction of mathematical expressions."""
        from scitex_scholar.latex_parser import LaTeXParser
        
        parser = LaTeXParser()
        
        latex_text = r"""
        The equation $E = mc^2$ is famous.
        
        We can also write:
        $$\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}$$
        
        \begin{equation}
        \frac{d}{dx} \sin(x) = \cos(x)
        \end{equation}
        
        \begin{align}
        a &= b + c \\
        d &= e + f
        \end{align}
        """
        
        math_expressions = parser.extract_math_expressions(latex_text)
        
        self.assertIsInstance(math_expressions, list)
        self.assertGreaterEqual(len(math_expressions), 4)
        
        # Check for different types of math
        math_types = [expr['type'] for expr in math_expressions]
        self.assertIn('inline', math_types)  # $...$
        self.assertIn('display', math_types)  # $$...$$
        self.assertIn('equation', math_types)  # \begin{equation}
        self.assertIn('align', math_types)  # \begin{align}
        
        # Check content extraction
        inline_math = next(expr for expr in math_expressions if expr['type'] == 'inline')
        self.assertIn('E = mc^2', inline_math['content'])

    def test_extract_citations(self):
        """Test extraction of LaTeX citations."""
        from scitex_scholar.latex_parser import LaTeXParser
        
        parser = LaTeXParser()
        
        latex_text = r"""
        According to \cite{smith2020}, this is important.
        See also \citep{jones2019} and \citet{brown2018}.
        Multiple citations \cite{doe2021,wilson2020} are common.
        
        \bibliography{references}
        \bibliographystyle{plain}
        """
        
        citations = parser.extract_citations(latex_text)
        
        self.assertIsInstance(citations, list)
        self.assertGreaterEqual(len(citations), 5)
        
        # Check citation keys
        citation_keys = [cite['key'] for cite in citations]
        self.assertIn('smith2020', citation_keys)
        self.assertIn('jones2019', citation_keys)
        self.assertIn('brown2018', citation_keys)
        self.assertIn('doe2021', citation_keys)
        self.assertIn('wilson2020', citation_keys)
        
        # Check citation types
        citation_types = [cite['type'] for cite in citations]
        self.assertIn('cite', citation_types)
        self.assertIn('citep', citation_types)
        self.assertIn('citet', citation_types)

    def test_parse_document_structure(self):
        """Test parsing of complete LaTeX document structure."""
        from scitex_scholar.latex_parser import LaTeXParser
        
        parser = LaTeXParser()
        
        latex_document = r"""
        \documentclass{article}
        \title{Machine Learning in Scientific Research}
        \author{John Doe}
        
        \begin{document}
        
        \maketitle
        
        \begin{abstract}
        This paper presents machine learning applications in scientific research.
        \end{abstract}
        
        \section{Introduction}
        Machine learning has become increasingly important.
        
        \subsection{Motivation}
        The motivation is clear from \cite{smith2020}.
        
        \section{Methods}
        We use the formula $f(x) = \frac{1}{1 + e^{-x}}$.
        
        \begin{equation}
        \nabla \cdot \mathbf{E} = \frac{\rho}{\epsilon_0}
        \end{equation}
        
        \section{Conclusion}
        Our results show significant improvements.
        
        \bibliography{references}
        
        \end{document}
        """
        
        parsed = parser.parse_document(latex_document)
        
        self.assertIsInstance(parsed, dict)
        self.assertIn('metadata', parsed)
        self.assertIn('structure', parsed)
        self.assertIn('content', parsed)
        self.assertIn('math_expressions', parsed)
        self.assertIn('citations', parsed)
        
        # Check metadata extraction
        metadata = parsed['metadata']
        self.assertIn('title', metadata)
        self.assertIn('author', metadata)
        self.assertEqual(metadata['title'], 'Machine Learning in Scientific Research')
        self.assertEqual(metadata['author'], 'John Doe')
        
        # Check structure extraction
        structure = parsed['structure']
        self.assertIn('sections', structure)
        sections = structure['sections']
        section_titles = [sec['title'] for sec in sections]
        self.assertIn('Introduction', section_titles)
        self.assertIn('Methods', section_titles)
        self.assertIn('Conclusion', section_titles)
        
        # Check content extraction
        content = parsed['content']
        self.assertIn('abstract', content)
        self.assertIn('machine learning applications', content['abstract'].lower())

    def test_clean_latex_content(self):
        """Test cleaning of LaTeX content for text processing."""
        from scitex_scholar.latex_parser import LaTeXParser
        
        parser = LaTeXParser()
        
        latex_text = r"""
        This is \textbf{bold} text and \textit{italic} text.
        We have \cite{ref} and some math $x + y = z$.
        Also \footnote{This is a footnote}.
        """
        
        cleaned = parser.clean_latex_content(latex_text)
        
        self.assertIsInstance(cleaned, str)
        # LaTeX commands should be removed or converted
        self.assertNotIn('\\textbf{', cleaned)
        self.assertNotIn('\\textit{', cleaned)
        self.assertNotIn('\\footnote{', cleaned)
        # But content should remain
        self.assertIn('bold', cleaned)
        self.assertIn('italic', cleaned)
        self.assertIn('text', cleaned)

    def test_integration_with_text_processor(self):
        """Test integration with existing TextProcessor."""
        from scitex_scholar.latex_parser import LaTeXParser
        from scitex_scholar.text_processor import TextProcessor
        
        latex_parser = LaTeXParser()
        text_processor = TextProcessor()
        
        latex_document = r"""
        \section{Machine Learning}
        Machine learning algorithms are used in \cite{smith2020}.
        The equation $y = mx + b$ represents a line.
        """
        
        # Parse LaTeX content
        parsed = latex_parser.parse_document(latex_document)
        
        # Extract clean text for processing
        clean_text = latex_parser.clean_latex_content(latex_document)
        
        # Process with TextProcessor
        processed = text_processor.process_document(clean_text)
        
        self.assertIsInstance(processed, dict)
        self.assertIn('keywords', processed)
        self.assertIn('cleaned_text', processed)
        
        # Should extract scientific keywords
        keywords = processed['keywords']
        self.assertTrue(any('machine' in kw.lower() for kw in keywords))
        self.assertTrue(any('learning' in kw.lower() for kw in keywords))


if __name__ == "__main__":
    unittest.main()

# EOF