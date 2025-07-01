#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-12 03:45:00"
# Author: Claude
# Description: Demonstration of SciTeX-Scholar literature review capabilities

"""
SciTeX-Scholar Literature Review Demo

This script demonstrates the core functionality of SciTeX-Scholar for:
1. Searching scientific publications from PubMed and arXiv
2. Downloading available PDFs
3. Parsing and analyzing scientific papers
4. Creating literature reviews with semantic search

Note: For subscription journals, manual download is required due to access restrictions.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from scitex.scholar import PaperAcquisition
from scitex.scholar import VectorSearchEngine as EnhancedVectorSearchEngine
from scitex.scholar._scientific_pdf_parser import ScientificPDFParser
from scitex.scholar import LiteratureReviewWorkflow


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"{title:^60}")
    print('='*60)


async def demo_paper_search():
    """Demonstrate paper search functionality."""
    print_section("1. PAPER SEARCH DEMONSTRATION")
    
    # Initialize paper acquisition
    acquisition = PaperAcquisition(
        email="your.email@example.com",  # Required for PubMed API
        rate_limit=3  # Respectful rate limiting
    )
    
    # Search query
    query = "deep learning medical imaging diagnosis"
    print(f"\nSearching for: '{query}'")
    print("Sources: PubMed and arXiv")
    
    # Search papers
    papers = await acquisition.search(
        query=query,
        max_results=10,
        sources=['pubmed', 'arxiv']
    )
    
    print(f"\nFound {len(papers)} papers:")
    for i, paper in enumerate(papers[:5], 1):  # Show first 5
        print(f"\n{i}. {paper.title}")
        print(f"   Authors: {', '.join(paper.authors[:3])}{'...' if len(paper.authors) > 3 else ''}")
        print(f"   Year: {paper.year}")
        print(f"   Source: {paper.source}")
        if paper.doi:
            print(f"   DOI: {paper.doi}")
        if paper.pdf_url:
            print(f"   PDF Available: Yes")
    
    return papers


async def demo_pdf_download(papers):
    """Demonstrate PDF download functionality."""
    print_section("2. PDF DOWNLOAD DEMONSTRATION")
    
    # Create workspace
    workspace = Path("./demo_workspace")
    workspace.mkdir(exist_ok=True)
    
    # Filter papers with available PDFs
    downloadable = [p for p in papers if p.pdf_url]
    print(f"\n{len(downloadable)} papers have PDFs available for download")
    
    if downloadable:
        # Download first 3 PDFs
        acquisition = PaperAcquisition()
        to_download = downloadable[:3]
        
        print(f"\nDownloading {len(to_download)} PDFs...")
        downloaded = await acquisition.batch_download(to_download, workspace)
        
        print(f"\nSuccessfully downloaded {len(downloaded)} PDFs:")
        for paper in downloaded:
            if paper.local_path:
                print(f"  ✓ {paper.title[:50]}...")
                print(f"    Saved to: {paper.local_path}")
    
    print("\nNote: Subscription journal PDFs require manual download due to access restrictions.")
    print("You can manually add PDFs to the workspace for processing.")
    
    return workspace


def demo_pdf_parsing(workspace):
    """Demonstrate PDF parsing functionality."""
    print_section("3. PDF PARSING DEMONSTRATION")
    
    parser = ScientificPDFParser()
    
    # Find PDFs in workspace
    pdf_files = list(workspace.glob("*.pdf"))
    
    if not pdf_files:
        print("\nNo PDFs found. Creating sample analysis...")
        return None
    
    # Parse first PDF
    pdf_path = pdf_files[0]
    print(f"\nParsing: {pdf_path.name}")
    
    try:
        paper = parser.parse_pdf(str(pdf_path))
        
        print("\nExtracted Information:")
        print(f"  Title: {paper.title or 'Not found'}")
        print(f"  Authors: {', '.join(paper.authors) if paper.authors else 'Not found'}")
        print(f"  Abstract: {paper.abstract[:100]}..." if paper.abstract else "  Abstract: Not found")
        
        if paper.methods_mentioned:
            print(f"\n  Methods detected: {', '.join(paper.methods_mentioned[:5])}")
        
        if paper.datasets_mentioned:
            print(f"  Datasets detected: {', '.join(paper.datasets_mentioned[:5])}")
        
        print(f"\n  Sections found: {len(paper.sections)}")
        for section, content in list(paper.sections.items())[:3]:
            print(f"    - {section}: {len(content)} characters")
            
    except Exception as e:
        print(f"\nError parsing PDF: {e}")
        print("This might be due to PDF structure or protection.")
    
    return pdf_files


def demo_vector_search(workspace):
    """Demonstrate vector search functionality."""
    print_section("4. SEMANTIC SEARCH DEMONSTRATION")
    
    # Initialize vector search engine
    print("\nInitializing vector search engine...")
    print("This uses SciBERT embeddings for scientific text understanding.")
    
    engine = VectorSearchEngine(
        collection_name="demo_literature",
        model_name="allenai/scibert_scivocab_uncased"
    )
    
    # Index sample documents
    print("\nIndexing scientific papers...")
    
    # Sample documents (in real use, these would be from parsed PDFs)
    documents = [
        {
            'id': 'paper1',
            'text': """Deep learning has revolutionized medical image analysis. 
                      Convolutional neural networks (CNNs) achieve state-of-the-art 
                      performance in detecting tumors, lesions, and abnormalities 
                      in X-rays, CT scans, and MRI images.""",
            'metadata': {
                'title': 'Deep Learning for Medical Imaging',
                'year': 2024,
                'method': 'CNN'
            }
        },
        {
            'id': 'paper2',
            'text': """Transformer architectures show promising results for 
                      medical text analysis and clinical note processing. 
                      BERT-based models can extract medical entities and 
                      relationships from electronic health records.""",
            'metadata': {
                'title': 'Transformers in Clinical NLP',
                'year': 2023,
                'method': 'Transformer'
            }
        },
        {
            'id': 'paper3',
            'text': """Traditional machine learning methods like SVM and 
                      Random Forest remain effective for structured medical data. 
                      These interpretable models are crucial for clinical 
                      decision support systems.""",
            'metadata': {
                'title': 'ML for Clinical Decision Support',
                'year': 2022,
                'method': 'SVM'
            }
        }
    ]
    
    for doc in documents:
        engine.add_document(
            document_id=doc['id'],
            text=doc['text'],
            metadata=doc['metadata']
        )
    
    # Demonstrate semantic search
    print("\nPerforming semantic search...")
    query = "neural networks for medical diagnosis"
    
    results = engine.search(query, n_results=3)
    
    print(f"\nSearch query: '{query}'")
    print("\nResults (ranked by semantic similarity):")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.metadata.get('title', 'Untitled')}")
        print(f"   Similarity score: {result.score:.3f}")
        print(f"   Method: {result.metadata.get('method', 'N/A')}")
        print(f"   Preview: {result.text[:100]}...")
    
    # Demonstrate finding similar papers
    print("\n\nFinding papers similar to the first result...")
    similar = engine.find_similar_documents(results[0].id, n_results=2)
    
    print("\nSimilar papers:")
    for i, sim in enumerate(similar, 1):
        print(f"{i}. {sim.metadata.get('title', 'Untitled')} (similarity: {sim.score:.3f})")


async def demo_literature_review():
    """Demonstrate complete literature review workflow."""
    print_section("5. LITERATURE REVIEW WORKFLOW")
    
    print("\nThe complete workflow includes:")
    print("1. Paper discovery from multiple sources")
    print("2. Automated PDF download (where available)")
    print("3. Information extraction and parsing")
    print("4. Semantic indexing for intelligent search")
    print("5. Research gap identification")
    print("6. Automated review generation")
    
    print("\nFor subscription journals:")
    print("- The system identifies relevant papers")
    print("- You manually download PDFs using institutional access")
    print("- Add PDFs to the workspace directory")
    print("- The system processes and indexes them automatically")
    
    print("\nKey features:")
    print("✓ Multi-source search (PubMed, arXiv, and more)")
    print("✓ Semantic search using SciBERT embeddings")
    print("✓ Automatic method and dataset extraction")
    print("✓ Citation network analysis")
    print("✓ Research gap identification")
    print("✓ Markdown report generation")


async def main():
    """Run the complete demonstration."""
    print("="*60)
    print("SciTeX-Scholar Literature Review System Demo".center(60))
    print("="*60)
    
    print("\nThis demo showcases the scientific publication search system")
    print("for literature review, including PDF processing capabilities.")
    
    try:
        # 1. Search papers
        papers = await demo_paper_search()
        
        # 2. Download PDFs
        workspace = await demo_pdf_download(papers)
        
        # 3. Parse PDFs
        pdf_files = demo_pdf_parsing(workspace)
        
        # 4. Vector search
        demo_vector_search(workspace)
        
        # 5. Complete workflow
        await demo_literature_review()
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        print("Some features may require additional setup or dependencies.")
    
    print("\n" + "="*60)
    print("Demo Complete!".center(60))
    print("="*60)
    
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Set your email for PubMed API in the code")
    print("3. Run actual literature searches with your queries")
    print("4. Add subscription journal PDFs manually to workspace")
    print("5. Use the web API (coming in Phase 3A) for easier access")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())