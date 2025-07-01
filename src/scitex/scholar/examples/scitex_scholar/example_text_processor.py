#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-12 03:35:00"
# Author: Claude
# Description: Example usage of text processor functionality

"""
Example usage of the SciTeX-Scholar text processor.

This example demonstrates how to:
1. Clean and normalize text
2. Extract text from various file formats
3. Tokenize and process scientific text
4. Handle special characters and equations
5. Perform text analysis and statistics
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scitex_scholar.text_processor import TextProcessor


def example_basic_text_processing():
    """Example of basic text processing operations."""
    print("=== Basic Text Processing Example ===\n")
    
    # Initialize text processor
    processor = TextProcessor()
    
    # Sample text with various issues
    messy_text = """
    This   is   a   sample   text   with   extra   spaces.
    It contains MIXED case WORDS and numbers like 123 and 456.
    Special characters: @#$% and symbols: α, β, γ.
    URLs: https://example.com and emails: user@example.com
    
    
    Extra blank lines above!
    """
    
    print("Original text:")
    print(repr(messy_text))
    
    # Clean the text
    cleaned = processor.clean_text(messy_text)
    print("\nCleaned text:")
    print(repr(cleaned))
    
    # Normalize the text
    normalized = processor.normalize_text(cleaned)
    print("\nNormalized text:")
    print(repr(normalized))


def example_scientific_text_processing():
    """Example of processing scientific text with equations."""
    print("\n\n=== Scientific Text Processing Example ===\n")
    
    processor = TextProcessor()
    
    # Scientific text with equations and references
    scientific_text = """
    The loss function is defined as $L = -\sum_{i=1}^{N} y_i \log(p_i)$
    where $y_i$ is the true label and $p_i$ is the predicted probability.
    
    According to Smith et al. (2023), the accuracy improved by 15.3%.
    The p-value was < 0.001, indicating statistical significance.
    
    Chemical formula: C₆H₁₂O₆ (glucose)
    Temperature: 37°C ± 0.5°C
    """
    
    print("Original scientific text:")
    print(scientific_text)
    
    # Process scientific text
    processed = processor.process_scientific_text(scientific_text)
    
    print("\nProcessed text:")
    print(f"  Text: {processed['text'][:100]}...")
    print(f"  Equations found: {len(processed.get('equations', []))}")
    print(f"  Numbers found: {processed.get('numbers', [])}")
    print(f"  Chemical formulas: {processed.get('formulas', [])}")


def example_tokenization():
    """Example of text tokenization."""
    print("\n\n=== Tokenization Example ===\n")
    
    processor = TextProcessor()
    
    # Text to tokenize
    text = "Machine learning models, including BERT and GPT-3, have revolutionized NLP."
    
    # Word tokenization
    words = processor.tokenize_words(text)
    print(f"Word tokens: {words}")
    print(f"Number of words: {len(words)}")
    
    # Sentence tokenization
    sentences_text = """
    Deep learning has transformed AI. It uses neural networks with many layers.
    Dr. Smith's research shows 95% accuracy! What are the implications?
    """
    
    sentences = processor.tokenize_sentences(sentences_text)
    print(f"\nSentences found: {len(sentences)}")
    for i, sent in enumerate(sentences, 1):
        print(f"  {i}. {sent}")


def example_text_extraction():
    """Example of extracting text from various formats."""
    print("\n\n=== Text Extraction Example ===\n")
    
    processor = TextProcessor()
    
    # Simulate different file formats
    print("Extracting text from different formats:")
    
    # 1. Plain text
    plain_text = "This is plain text content."
    result = processor.extract_text_from_string(plain_text, format='txt')
    print(f"\n1. Plain text: {result}")
    
    # 2. Markdown
    markdown_text = """
    # Title
    
    This is **bold** and this is *italic*.
    
    - Item 1
    - Item 2
    
    [Link](https://example.com)
    """
    result = processor.extract_text_from_string(markdown_text, format='md')
    print(f"\n2. Markdown: {result[:50]}...")
    
    # 3. HTML
    html_text = """
    <html>
    <body>
    <h1>Title</h1>
    <p>This is a <strong>paragraph</strong> with <em>emphasis</em>.</p>
    </body>
    </html>
    """
    result = processor.extract_text_from_string(html_text, format='html')
    print(f"\n3. HTML: {result}")


def example_text_statistics():
    """Example of computing text statistics."""
    print("\n\n=== Text Statistics Example ===\n")
    
    processor = TextProcessor()
    
    # Sample document
    document = """
    Artificial intelligence (AI) is transforming healthcare. Machine learning
    algorithms can diagnose diseases with high accuracy. Deep learning models
    analyze medical images to detect abnormalities. Natural language processing
    helps extract information from clinical notes.
    
    AI applications include:
    1. Disease diagnosis
    2. Drug discovery
    3. Treatment planning
    4. Patient monitoring
    
    The future of AI in healthcare is promising, but challenges remain.
    """
    
    # Compute statistics
    stats = processor.compute_text_statistics(document)
    
    print("Text Statistics:")
    print(f"  Characters: {stats['char_count']}")
    print(f"  Words: {stats['word_count']}")
    print(f"  Sentences: {stats['sentence_count']}")
    print(f"  Average word length: {stats['avg_word_length']:.1f}")
    print(f"  Average sentence length: {stats['avg_sentence_length']:.1f} words")
    print(f"  Vocabulary size: {stats['unique_words']}")
    print(f"  Lexical diversity: {stats['lexical_diversity']:.2f}")


def example_keyword_extraction():
    """Example of extracting keywords from text."""
    print("\n\n=== Keyword Extraction Example ===\n")
    
    processor = TextProcessor()
    
    # Technical document
    text = """
    Convolutional Neural Networks (CNNs) have revolutionized computer vision.
    These deep learning architectures use convolution operations to extract
    features from images. Popular CNN architectures include ResNet, VGG, and
    Inception. Transfer learning with pre-trained CNNs has enabled rapid
    development of image classification systems. Recent advances combine CNNs
    with attention mechanisms for improved performance.
    """
    
    # Extract keywords
    keywords = processor.extract_keywords(text, num_keywords=10)
    
    print("Extracted Keywords:")
    for i, (keyword, score) in enumerate(keywords, 1):
        print(f"  {i}. {keyword} (score: {score:.3f})")


def example_text_chunking():
    """Example of chunking text for processing."""
    print("\n\n=== Text Chunking Example ===\n")
    
    processor = TextProcessor()
    
    # Long document
    long_text = """
    Section 1: Introduction
    
    Machine learning is a subset of artificial intelligence that enables
    systems to learn from data. It has applications in many domains.
    
    Section 2: Supervised Learning
    
    Supervised learning uses labeled data to train models. Common algorithms
    include decision trees, support vector machines, and neural networks.
    The goal is to learn a mapping from inputs to outputs.
    
    Section 3: Unsupervised Learning
    
    Unsupervised learning finds patterns in unlabeled data. Clustering and
    dimensionality reduction are key techniques. K-means and PCA are popular
    algorithms in this category.
    
    Section 4: Reinforcement Learning
    
    Reinforcement learning trains agents to make decisions through interaction
    with an environment. The agent learns to maximize cumulative reward.
    """
    
    # Chunk by sentences
    chunks = processor.chunk_text(long_text, chunk_size=3, chunk_type='sentence')
    
    print(f"Text chunked into {len(chunks)} parts:")
    for i, chunk in enumerate(chunks, 1):
        print(f"\nChunk {i}:")
        print(f"  {chunk[:80]}...")
    
    # Chunk by words
    word_chunks = processor.chunk_text(long_text, chunk_size=50, chunk_type='word')
    print(f"\nAlternatively, chunked by words: {len(word_chunks)} chunks of ~50 words each")


def example_language_detection():
    """Example of detecting language in text."""
    print("\n\n=== Language Detection Example ===\n")
    
    processor = TextProcessor()
    
    # Texts in different languages
    texts = [
        ("English", "Machine learning is transforming technology."),
        ("Spanish", "El aprendizaje automático está transformando la tecnología."),
        ("French", "L'apprentissage automatique transforme la technologie."),
        ("German", "Maschinelles Lernen verändert die Technologie."),
        ("Mixed", "This is English, pero también tiene español.")
    ]
    
    print("Detecting languages:")
    for label, text in texts:
        language = processor.detect_language(text)
        print(f"  {label}: '{text[:40]}...' → {language}")


def example_text_similarity():
    """Example of computing text similarity."""
    print("\n\n=== Text Similarity Example ===\n")
    
    processor = TextProcessor()
    
    # Reference text
    text1 = "Deep learning uses neural networks with multiple layers."
    
    # Comparison texts
    comparison_texts = [
        "Neural networks with many layers are used in deep learning.",
        "Machine learning algorithms process data to make predictions.",
        "Convolutional networks are a type of deep learning model.",
        "The weather today is sunny and warm."
    ]
    
    print(f"Reference: '{text1}'")
    print("\nSimilarity scores:")
    
    for text2 in comparison_texts:
        similarity = processor.compute_similarity(text1, text2)
        print(f"  '{text2[:50]}...' → {similarity:.3f}")


def example_special_character_handling():
    """Example of handling special characters and symbols."""
    print("\n\n=== Special Character Handling Example ===\n")
    
    processor = TextProcessor()
    
    # Text with various special characters
    special_text = """
    Mathematical symbols: ∑ ∏ ∫ ∂ ∇ ∞ ≈ ≠ ≤ ≥
    Greek letters: α β γ δ ε θ λ μ π σ φ ω
    Arrows: → ← ↑ ↓ ⇒ ⇐ ↔ ⇔
    Subscripts: H₂O, CO₂, x₁, x₂
    Superscripts: E=mc², x³+y³=z³
    Special quotes: "curly quotes" and 'single quotes'
    Em dash — and en dash –
    Ellipsis… and bullets • ▪ ▸
    """
    
    print("Original text with special characters:")
    print(special_text)
    
    # Process with different strategies
    print("\n1. Convert to ASCII:")
    ascii_text = processor.convert_to_ascii(special_text)
    print(ascii_text[:200] + "...")
    
    print("\n2. Normalize Unicode:")
    normalized = processor.normalize_unicode(special_text)
    print(normalized[:200] + "...")
    
    print("\n3. Preserve scientific notation:")
    scientific = processor.process_scientific_notation(special_text)
    print(scientific[:200] + "...")


def main():
    """Run all text processor examples."""
    print("SciTeX-Scholar Text Processor Examples")
    print("=" * 50)
    
    # Run examples
    example_basic_text_processing()
    example_scientific_text_processing()
    example_tokenization()
    example_text_extraction()
    example_text_statistics()
    example_keyword_extraction()
    example_text_chunking()
    example_language_detection()
    example_text_similarity()
    example_special_character_handling()
    
    print("\n" + "=" * 50)
    print("All text processor examples completed!")


if __name__ == "__main__":
    main()