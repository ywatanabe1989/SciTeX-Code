#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-12 03:32:00"
# Author: Claude
# Description: Example usage of LaTeX parser functionality

"""
Example usage of LaTeX parser for scientific documents.

This example demonstrates how to:
1. Parse LaTeX documents to extract structured information
2. Extract mathematical equations and formulas
3. Parse bibliography entries
4. Handle complex LaTeX structures
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scitex_scholar.latex_parser import LaTeXParser


def example_basic_parsing():
    """Example of basic LaTeX document parsing."""
    print("=== Basic LaTeX Parsing Example ===\n")
    
    # Initialize parser
    parser = LaTeXParser()
    
    # Example LaTeX content
    latex_content = r"""
    \documentclass{article}
    \usepackage{amsmath}
    \usepackage{graphicx}
    
    \title{Deep Learning for Medical Image Analysis}
    \author{John Smith \and Jane Doe}
    \date{January 2024}
    
    \begin{document}
    \maketitle
    
    \begin{abstract}
    This paper presents a novel deep learning approach for medical image analysis.
    We propose a hybrid CNN-Transformer architecture that achieves state-of-the-art
    performance on multiple medical imaging benchmarks.
    \end{abstract}
    
    \section{Introduction}
    Medical image analysis has been revolutionized by deep learning methods
    \cite{smith2023review}. Recent advances in transformer architectures
    \cite{doe2023transformers} have opened new possibilities.
    
    \section{Methods}
    Our approach combines convolutional neural networks with transformer blocks.
    The loss function is defined as:
    \begin{equation}
    \mathcal{L} = \mathcal{L}_{seg} + \lambda \mathcal{L}_{reg}
    \end{equation}
    
    where $\mathcal{L}_{seg}$ is the segmentation loss and $\mathcal{L}_{reg}$
    is the regularization term.
    
    \section{Results}
    We evaluated our method on three datasets:
    \begin{itemize}
    \item Dataset A: 95.2\% accuracy
    \item Dataset B: 93.7\% accuracy
    \item Dataset C: 96.1\% accuracy
    \end{itemize}
    
    \bibliographystyle{plain}
    \bibliography{references}
    \end{document}
    """
    
    # Parse the document
    parsed = parser.parse(latex_content)
    
    # Display results
    print(f"Title: {parsed.get('title', 'N/A')}")
    print(f"Authors: {', '.join(parsed.get('authors', []))}")
    print(f"Date: {parsed.get('date', 'N/A')}")
    print(f"\nAbstract: {parsed.get('abstract', 'N/A')[:100]}...")
    print(f"\nNumber of sections: {len(parsed.get('sections', {}))}")
    print(f"Number of equations: {len(parsed.get('equations', []))}")
    print(f"Number of citations: {len(parsed.get('citations', []))}")


def example_equation_extraction():
    """Example of extracting mathematical equations."""
    print("\n\n=== Equation Extraction Example ===\n")
    
    parser = LaTeXParser()
    
    latex_with_equations = r"""
    \section{Mathematical Framework}
    
    The objective function for our neural network is:
    \begin{equation}
    J(\theta) = \frac{1}{m} \sum_{i=1}^{m} L(y^{(i)}, \hat{y}^{(i)}) + \frac{\lambda}{2m} \sum_{l=1}^{L} ||\theta^{(l)}||^2
    \label{eq:objective}
    \end{equation}
    
    The gradient descent update rule:
    \begin{align}
    \theta^{(l)} &= \theta^{(l)} - \alpha \frac{\partial J}{\partial \theta^{(l)}} \\
    &= \theta^{(l)} - \alpha \left( \frac{1}{m} X^T (h_\theta(X) - y) + \frac{\lambda}{m} \theta^{(l)} \right)
    \label{eq:gradient}
    \end{align}
    
    For the attention mechanism:
    \[
    \text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
    \]
    """
    
    # Parse and extract equations
    parsed = parser.parse(latex_with_equations)
    equations = parsed.get('equations', [])
    
    print(f"Found {len(equations)} equations:\n")
    for i, eq in enumerate(equations, 1):
        print(f"Equation {i}:")
        print(f"  Type: {eq.get('type', 'inline')}")
        print(f"  Label: {eq.get('label', 'None')}")
        print(f"  Content: {eq.get('content', '')[:60]}...")
        print()


def example_bibliography_parsing():
    """Example of parsing bibliography entries."""
    print("\n\n=== Bibliography Parsing Example ===\n")
    
    parser = LaTeXParser()
    
    # Example .bib content
    bib_content = r"""
    @article{smith2023review,
        author = {Smith, John and Johnson, Alice},
        title = {A Comprehensive Review of Deep Learning in Medical Imaging},
        journal = {Medical Image Analysis},
        year = {2023},
        volume = {45},
        pages = {123--145},
        doi = {10.1016/j.media.2023.01.001}
    }
    
    @inproceedings{doe2023transformers,
        author = {Doe, Jane and Brown, Bob},
        title = {Vision Transformers for Medical Image Segmentation},
        booktitle = {Proceedings of MICCAI 2023},
        year = {2023},
        pages = {234--243}
    }
    
    @book{wilson2022foundations,
        author = {Wilson, Carol},
        title = {Foundations of Medical AI},
        publisher = {Academic Press},
        year = {2022},
        isbn = {978-0-12-345678-9}
    }
    """
    
    # Parse bibliography
    bib_entries = parser.parse_bibliography(bib_content)
    
    print(f"Found {len(bib_entries)} bibliography entries:\n")
    for key, entry in bib_entries.items():
        print(f"Key: {key}")
        print(f"  Type: {entry.get('type', 'N/A')}")
        print(f"  Title: {entry.get('title', 'N/A')}")
        print(f"  Authors: {entry.get('author', 'N/A')}")
        print(f"  Year: {entry.get('year', 'N/A')}")
        print()


def example_complex_document_parsing():
    """Example of parsing a complex LaTeX document with multiple elements."""
    print("\n\n=== Complex Document Parsing Example ===\n")
    
    parser = LaTeXParser()
    
    complex_latex = r"""
    \documentclass[conference]{IEEEtran}
    \usepackage{algorithmic}
    \usepackage{algorithm}
    \usepackage{booktabs}
    
    \begin{document}
    
    \title{Advanced Neural Architecture Search}
    
    \begin{abstract}
    We present AutoML-Net, an automated approach to neural architecture design.
    \end{abstract}
    
    \section{Algorithm}
    
    \begin{algorithm}
    \caption{Neural Architecture Search}
    \label{alg:nas}
    \begin{algorithmic}
    \STATE Initialize population $P$ with random architectures
    \FOR{$i = 1$ to $max\_iterations$}
        \STATE Evaluate fitness of each architecture
        \STATE Select top-k architectures
        \STATE Generate new architectures via mutation
        \STATE Update population $P$
    \ENDFOR
    \RETURN Best architecture
    \end{algorithmic}
    \end{algorithm}
    
    \section{Experimental Results}
    
    \begin{table}[h]
    \centering
    \caption{Performance Comparison}
    \label{tab:results}
    \begin{tabular}{lcc}
    \toprule
    Method & Accuracy & Parameters \\
    \midrule
    ResNet-50 & 94.2\% & 25.6M \\
    EfficientNet & 95.1\% & 5.3M \\
    AutoML-Net (Ours) & \textbf{96.3\%} & 4.8M \\
    \bottomrule
    \end{tabular}
    \end{table}
    
    \begin{figure}[h]
    \centering
    \includegraphics[width=0.8\linewidth]{architecture.png}
    \caption{Discovered neural architecture}
    \label{fig:architecture}
    \end{figure}
    
    \end{document}
    """
    
    # Parse the complex document
    parsed = parser.parse(complex_latex)
    
    # Extract various elements
    print("Document Structure:")
    print(f"  Document class: {parsed.get('documentclass', 'N/A')}")
    print(f"  Packages used: {', '.join(parsed.get('packages', []))}")
    print(f"  Algorithms: {len(parsed.get('algorithms', []))}")
    print(f"  Tables: {len(parsed.get('tables', []))}")
    print(f"  Figures: {len(parsed.get('figures', []))}")
    
    # Display algorithm details
    algorithms = parsed.get('algorithms', [])
    if algorithms:
        print("\nAlgorithm Details:")
        for alg in algorithms:
            print(f"  Caption: {alg.get('caption', 'N/A')}")
            print(f"  Label: {alg.get('label', 'N/A')}")
    
    # Display table details
    tables = parsed.get('tables', [])
    if tables:
        print("\nTable Details:")
        for table in tables:
            print(f"  Caption: {table.get('caption', 'N/A')}")
            print(f"  Label: {table.get('label', 'N/A')}")


def example_citation_analysis():
    """Example of analyzing citations in a LaTeX document."""
    print("\n\n=== Citation Analysis Example ===\n")
    
    parser = LaTeXParser()
    
    latex_with_citations = r"""
    \section{Related Work}
    
    Deep learning has shown remarkable success in medical imaging 
    \cite{smith2023review, doe2023transformers}. Early work by 
    \cite{johnson2020foundation} established the theoretical framework.
    
    Recent advances include:
    \begin{itemize}
    \item Vision transformers \cite{doe2023transformers, wang2023vit}
    \item Self-supervised learning \cite{chen2023ssl, liu2023pretraining}
    \item Multi-modal fusion \cite{zhang2023fusion}
    \end{itemize}
    
    \section{Discussion}
    
    Our approach builds upon \cite{smith2023review} and extends the 
    work of \cite{doe2023transformers, johnson2020foundation}.
    """
    
    # Parse and analyze citations
    parsed = parser.parse(latex_with_citations)
    citations = parsed.get('citations', [])
    
    # Count citation frequency
    citation_counts = {}
    for cite in citations:
        for ref in cite.get('references', []):
            citation_counts[ref] = citation_counts.get(ref, 0) + 1
    
    print(f"Total citations: {len(citations)}")
    print(f"Unique references: {len(citation_counts)}")
    print("\nCitation frequency:")
    for ref, count in sorted(citation_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {ref}: {count} times")
    
    # Analyze citation context
    print("\nCitation contexts:")
    for i, cite in enumerate(citations[:3], 1):  # Show first 3
        print(f"\nCitation {i}:")
        print(f"  References: {', '.join(cite.get('references', []))}")
        print(f"  Context: ...{cite.get('context', 'N/A')[:50]}...")


def example_latex_to_text_conversion():
    """Example of converting LaTeX to plain text."""
    print("\n\n=== LaTeX to Text Conversion Example ===\n")
    
    parser = LaTeXParser()
    
    latex_content = r"""
    \section{Introduction}
    
    This paper introduces \textbf{DeepMed}, a novel \emph{deep learning} 
    framework for medical image analysis. We achieve \texttt{state-of-the-art} 
    performance with $95.3\%$ accuracy.
    
    Key contributions:
    \begin{enumerate}
    \item A new architecture combining CNNs and transformers
    \item Extensive evaluation on \underline{five} medical datasets
    \item Open-source implementation available at \url{https://github.com/deepmed}
    \end{enumerate}
    """
    
    # Convert to plain text
    plain_text = parser.to_plain_text(latex_content)
    
    print("Original LaTeX:")
    print(latex_content)
    print("\nConverted to plain text:")
    print(plain_text)


def main():
    """Run all LaTeX parser examples."""
    print("SciTeX-Scholar LaTeX Parser Examples")
    print("=" * 50)
    
    # Run examples
    example_basic_parsing()
    example_equation_extraction()
    example_bibliography_parsing()
    example_complex_document_parsing()
    example_citation_analysis()
    example_latex_to_text_conversion()
    
    print("\n" + "=" * 50)
    print("All LaTeX parser examples completed!")


if __name__ == "__main__":
    main()