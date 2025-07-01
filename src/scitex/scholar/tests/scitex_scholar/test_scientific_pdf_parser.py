#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-06 03:45:00 (ywatanabe)"
# File: tests/scitex_scholar/test_scientific_pdf_parser.py

"""
Test module for scientific PDF parser functionality.

This module tests the extraction of structured information from
scientific PDF documents including metadata, sections, and citations.
"""

import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys
sys.path.insert(0, './src')

from scitex_scholar.scientific_pdf_parser import ScientificPDFParser, ScientificPaper


class TestScientificPDFParser(unittest.TestCase):
    """Test suite for scientific PDF parser functionality."""
    
    def setUp(self):
        """Set up for each test."""
        self.parser = ScientificPDFParser()
    
    def test_scientific_pdf_parser_initialization(self):
        """Test ScientificPDFParser can be initialized."""
        self.assertIsNotNone(self.parser)
        self.assertIsNotNone(self.parser.section_patterns)
        self.assertIsNotNone(self.parser.citation_pattern)
        self.assertIsNotNone(self.parser.method_patterns)
    
    def test_scientific_paper_dataclass(self):
        """Test ScientificPaper dataclass."""
        paper = ScientificPaper(
            title="Test Paper",
            authors=["John Doe", "Jane Smith"],
            abstract="Test abstract",
            sections={"introduction": "Intro text"},
            keywords=["machine learning", "AI"],
            references=[{"number": "1", "raw": "Test ref"}],
            figures=[{"number": "1", "caption": "Test figure"}],
            tables=[{"number": "1", "caption": "Test table"}],
            equations=["E = mc^2"],
            metadata={"page_count": 10},
            citations_in_text=["[1]", "[2]"],
            methods_mentioned=["CNN", "LSTM"],
            datasets_mentioned=["MNIST"],
            metrics_reported={"accuracy": 95.5}
        )
        
        self.assertEqual(paper.title, "Test Paper")
        self.assertEqual(len(paper.authors), 2)
        self.assertEqual(paper.metrics_reported["accuracy"], 95.5)
        
        # Test to_dict conversion
        data = paper.to_dict()
        self.assertIsInstance(data, dict)
        self.assertEqual(data['title'], "Test Paper")
    
    def test_extract_title(self):
        """Test title extraction from first page."""
        first_page = """
        Some header text
        
        Deep Learning for Medical Image Analysis:
        A Comprehensive Survey
        
        John Doe, Jane Smith
        University of Example
        """
        
        title = self.parser._extract_title(first_page)
        self.assertIsNotNone(title)
        self.assertIn("Deep Learning", title)
    
    def test_extract_authors(self):
        """Test author extraction."""
        first_page = """
        Title of Paper
        
        John Doe¹, Jane Smith², and Robert Johnson³
        
        ¹University A, ²University B, ³University C
        """
        
        authors = self.parser._extract_authors(first_page)
        self.assertIsInstance(authors, list)
        self.assertGreater(len(authors), 0)
        # Should extract at least one author name
        self.assertTrue(any("John" in author or "Doe" in author for author in authors))
    
    def test_extract_abstract(self):
        """Test abstract extraction."""
        text = """
        Title
        Authors
        
        Abstract
        This paper presents a novel approach to machine learning for medical imaging.
        We propose a new architecture that achieves state-of-the-art results.
        
        Keywords: machine learning, medical imaging, deep learning
        
        1. Introduction
        The introduction begins here...
        """
        
        abstract = self.parser._extract_abstract(text)
        self.assertIsNotNone(abstract)
        self.assertIn("novel approach", abstract)
        self.assertIn("machine learning", abstract)
    
    def test_extract_sections(self):
        """Test section extraction."""
        text = """
        Abstract
        This is the abstract.
        
        1. Introduction
        This is the introduction section with some content.
        
        2. Related Work
        Previous studies have shown...
        
        3. Methods
        Our methodology involves...
        
        4. Results
        We achieved the following results...
        
        5. Conclusion
        In conclusion, we have shown...
        
        References
        [1] Smith et al. (2020)
        """
        
        sections = self.parser._extract_sections(text)
        self.assertIsInstance(sections, dict)
        self.assertIn('introduction', sections)
        self.assertIn('methods', sections)
        self.assertIn('conclusion', sections)
        
        # Check content
        self.assertIn("introduction section", sections['introduction'])
        self.assertIn("methodology", sections['methods'])
    
    def test_extract_keywords(self):
        """Test keyword extraction."""
        text = """
        Abstract
        ...
        
        Keywords: machine learning, deep neural networks, computer vision, 
                  medical imaging, convolutional networks
        
        1. Introduction
        """
        
        keywords = self.parser._extract_keywords(text)
        self.assertIsInstance(keywords, list)
        self.assertGreater(len(keywords), 0)
        self.assertIn("machine learning", keywords)
        self.assertIn("computer vision", keywords)
    
    def test_extract_references(self):
        """Test reference extraction."""
        text = """
        5. Conclusion
        ...
        
        References
        
        [1] Smith, J., Doe, J. (2023). Deep Learning for Medical Imaging. 
            Journal of AI Research, 45(2), 123-145.
            
        [2] Johnson, R. et al. (2022). Convolutional Neural Networks in Healthcare.
            Nature Machine Intelligence, 4(3), 234-256.
            
        [3] Brown, A. (2021). Survey of ML Methods. ACM Computing Surveys.
        """
        
        references = self.parser._extract_references(text)
        self.assertIsInstance(references, list)
        self.assertGreater(len(references), 0)
        
        # Check first reference
        self.assertEqual(references[0]['number'], '1')
        self.assertIn("Smith", references[0]['raw'])
        self.assertEqual(references[0]['year'], '2023')
    
    def test_extract_citations(self):
        """Test in-text citation extraction."""
        text = """
        Previous work [1,2] has shown that neural networks [3] can be effective.
        Smith et al. (2020) demonstrated this approach. According to (Johnson, 2021),
        the results are promising. See also [4, 5, 6] for more details.
        """
        
        citations = self.parser._extract_citations(text)
        self.assertIsInstance(citations, list)
        self.assertIn("[1]", citations)
        self.assertIn("[2]", citations)
        self.assertIn("[3]", citations)
        self.assertIn("Smith et al., 2020", citations)
        self.assertIn("Johnson, 2021", citations)
    
    def test_extract_methods(self):
        """Test method extraction."""
        text = """
        We used a Convolutional Neural Network (CNN) for image classification.
        The model includes LSTM layers for temporal modeling. We also compared
        with traditional SVM and Random Forest baselines. Our transformer-based
        approach outperformed the ResNet baseline.
        """
        
        methods = self.parser._extract_methods(text)
        self.assertIsInstance(methods, list)
        self.assertIn("CNN", methods)
        self.assertIn("LSTM", methods)
        self.assertIn("SVM", methods)
        self.assertIn("Transformer", methods)
        self.assertIn("ResNet", methods)
    
    def test_extract_datasets(self):
        """Test dataset extraction."""
        text = """
        We evaluated our method on several benchmark datasets including MNIST,
        CIFAR-10, and ImageNet. For medical imaging, we used the ChestX-ray14
        dataset. Additional experiments were conducted on COCO for object detection.
        """
        
        datasets = self.parser._extract_datasets(text)
        self.assertIsInstance(datasets, list)
        self.assertIn("MNIST", datasets)
        self.assertIn("CIFAR-10", datasets)
        self.assertIn("ImageNet", datasets)
        self.assertIn("ChestX-ray14", datasets)
        self.assertIn("COCO", datasets)
    
    def test_extract_metrics(self):
        """Test metric extraction."""
        text = """
        Our model achieved an accuracy of 95.2% on the test set. The precision
        was 93.5% and recall reached 94.8%. We obtained an F1-score of 94.1.
        The AUC was 0.982 and mAP: 87.3%. These results show significant improvement.
        """
        
        metrics = self.parser._extract_metrics(text)
        self.assertIsInstance(metrics, dict)
        self.assertAlmostEqual(metrics['accuracy'], 95.2)
        self.assertAlmostEqual(metrics['precision'], 93.5)
        self.assertAlmostEqual(metrics['recall'], 94.8)
        self.assertAlmostEqual(metrics['f1_score'], 94.1)
        self.assertAlmostEqual(metrics['auc'], 98.2)  # Converted from 0.982
        self.assertAlmostEqual(metrics['map'], 87.3)
    
    def test_extract_figures(self):
        """Test figure extraction."""
        text = """
        As shown in Figure 1, the architecture consists of multiple layers.
        
        Figure 1: Overview of the proposed neural network architecture with
        attention mechanisms and skip connections.
        
        Fig. 2 demonstrates the training curves over 100 epochs.
        
        Figure 2: Training and validation loss curves showing convergence.
        """
        
        figures = self.parser._extract_figures(text)
        self.assertIsInstance(figures, list)
        self.assertEqual(len(figures), 2)
        self.assertEqual(figures[0]['number'], '1')
        self.assertIn("neural network architecture", figures[0]['caption'])
        self.assertEqual(figures[1]['number'], '2')
        self.assertIn("loss curves", figures[1]['caption'])
    
    def test_extract_tables(self):
        """Test table extraction."""
        text = """
        Results are summarized in Table 1 below.
        
        Table 1: Comparison of different methods on benchmark datasets
        showing accuracy and training time.
        
        Table 2 presents the ablation study results.
        
        Table 2: Ablation study showing the impact of each component.
        """
        
        tables = self.parser._extract_tables(text)
        self.assertIsInstance(tables, list)
        self.assertEqual(len(tables), 2)
        self.assertEqual(tables[0]['number'], '1')
        self.assertIn("Comparison", tables[0]['caption'])
    
    def test_extract_equations(self):
        """Test equation extraction."""
        text = """
        The loss function is defined as:
        
        (1) L = -∑ y_i log(ŷ_i)
        
        We optimize using gradient descent:
        
        (2) θ = θ - α∇L
        
        Where α is the learning rate and (3) ∇L = ∂L/∂θ
        """
        
        equations = self.parser._extract_equations(text)
        self.assertIsInstance(equations, list)
        self.assertGreater(len(equations), 0)
        self.assertTrue(any("∑" in eq for eq in equations))
        self.assertTrue(any("∇" in eq for eq in equations))
    
    @patch('pdfplumber.open')
    def test_parse_pdf_integration(self, mock_pdf_open):
        """Test complete PDF parsing with mocked pdfplumber."""
        # Mock PDF pages
        mock_page1 = Mock()
        mock_page1.extract_text.return_value = """
        Deep Learning for Medical Imaging
        
        John Doe, Jane Smith
        
        Abstract
        This paper presents a novel CNN approach for medical image analysis.
        
        Keywords: deep learning, medical imaging, CNN
        """
        
        mock_page2 = Mock()
        mock_page2.extract_text.return_value = """
        1. Introduction
        Medical imaging has benefited from deep learning...
        
        2. Methods
        We used a ResNet-50 architecture with modifications...
        """
        
        mock_pdf = Mock()
        mock_pdf.pages = [mock_page1, mock_page2]
        mock_pdf.__enter__ = Mock(return_value=mock_pdf)
        mock_pdf.__exit__ = Mock(return_value=None)
        mock_pdf_open.return_value = mock_pdf
        
        # Parse PDF
        pdf_path = Path("test.pdf")
        pdf_path.stat = Mock(return_value=Mock(st_size=1000))
        
        paper = self.parser.parse_pdf(pdf_path)
        
        self.assertIsInstance(paper, ScientificPaper)
        self.assertIn("Deep Learning", paper.title)
        self.assertIn("CNN", paper.keywords)
        self.assertIn("introduction", paper.sections)
        self.assertIn("ResNet", paper.methods_mentioned)
    
    def test_to_search_document(self):
        """Test conversion to searchable document format."""
        paper = ScientificPaper(
            title="Test Paper",
            authors=["Author 1", "Author 2"],
            abstract="Test abstract",
            sections={"intro": "Introduction text"},
            keywords=["keyword1", "keyword2"],
            references=[],
            figures=[],
            tables=[],
            equations=[],
            metadata={"year": "2024"},
            citations_in_text=[],
            methods_mentioned=["Method1"],
            datasets_mentioned=["Dataset1"],
            metrics_reported={"accuracy": 95.0}
        )
        
        doc = self.parser.to_search_document(paper)
        
        self.assertIsInstance(doc, dict)
        self.assertIn('content', doc)
        self.assertIn('metadata', doc)
        self.assertIn('sections', doc)
        
        # Check searchable content includes all important fields
        self.assertIn("Test Paper", doc['content'])
        self.assertIn("Author 1", doc['content'])
        self.assertIn("Test abstract", doc['content'])
        self.assertIn("keyword1", doc['content'])


if __name__ == "__main__":
    unittest.main()

# EOF