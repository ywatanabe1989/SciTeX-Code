#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-01-06 03:55:00 (ywatanabe)"
# File: examples/scitex_scholar/example_scientific_pdf_parser.py

"""
Example: Parse scientific PDF papers to extract structured information.

This example demonstrates:
- Extracting metadata (title, authors, abstract)
- Finding sections and their content
- Extracting citations and references
- Identifying methods and datasets
- Getting reported metrics
"""

import sys
from pathlib import Path
from pprint import pprint
sys.path.insert(0, './src')

from scitex_scholar.scientific_pdf_parser import ScientificPDFParser


def main():
    """Demonstrate scientific PDF parsing capabilities."""
    
    print("=== Scientific PDF Parser Example ===\n")
    
    # Initialize parser
    parser = ScientificPDFParser()
    
    # Example PDF path (you'll need an actual PDF)
    pdf_path = Path("./Exported Items/files/436/Combrisson et al. - 2020 - Tensorpac An open-source Python toolbox for tenso.pdf")
    
    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}")
        print("\nTo test this example, please provide a scientific PDF.")
        print("You can use any PDF from './Exported Items/files/'")
        return
    
    print(f"Parsing: {pdf_path.name}\n")
    
    try:
        # Parse the PDF
        paper = parser.parse_pdf(pdf_path)
        
        # 1. Basic Metadata
        print("1. BASIC METADATA")
        print("-" * 50)
        print(f"Title: {paper.title}")
        print(f"Authors: {', '.join(paper.authors[:5])}")
        if len(paper.authors) > 5:
            print(f"         ... and {len(paper.authors) - 5} more")
        print(f"Year: {paper.metadata.get('year', 'Not found')}")
        print(f"Pages: {paper.metadata.get('page_count', 'Unknown')}")
        
        # 2. Abstract and Keywords
        print("\n\n2. ABSTRACT AND KEYWORDS")
        print("-" * 50)
        if paper.abstract:
            print(f"Abstract: {paper.abstract[:200]}...")
        else:
            print("Abstract: Not found")
        
        if paper.keywords:
            print(f"\nKeywords: {', '.join(paper.keywords[:10])}")
        
        # 3. Document Structure
        print("\n\n3. DOCUMENT STRUCTURE")
        print("-" * 50)
        print(f"Sections found: {len(paper.sections)}")
        for section_name, content in list(paper.sections.items())[:5]:
            print(f"  - {section_name}: {len(content)} characters")
        
        # 4. Scientific Content
        print("\n\n4. SCIENTIFIC CONTENT")
        print("-" * 50)
        
        if paper.methods_mentioned:
            print(f"Methods detected: {', '.join(paper.methods_mentioned)}")
        else:
            print("Methods detected: None found")
        
        if paper.datasets_mentioned:
            print(f"Datasets mentioned: {', '.join(paper.datasets_mentioned)}")
        else:
            print("Datasets mentioned: None found")
        
        # 5. Citations and References
        print("\n\n5. CITATIONS AND REFERENCES")
        print("-" * 50)
        print(f"In-text citations: {len(paper.citations_in_text)}")
        if paper.citations_in_text:
            print(f"Examples: {', '.join(paper.citations_in_text[:10])}")
        
        print(f"\nReferences: {len(paper.references)}")
        if paper.references:
            for ref in paper.references[:3]:
                print(f"  [{ref['number']}] {ref['raw'][:100]}...")
        
        # 6. Figures and Tables
        print("\n\n6. FIGURES AND TABLES")
        print("-" * 50)
        print(f"Figures: {len(paper.figures)}")
        if paper.figures:
            for fig in paper.figures[:3]:
                print(f"  Figure {fig['number']}: {fig['caption'][:80]}...")
        
        print(f"\nTables: {len(paper.tables)}")
        if paper.tables:
            for table in paper.tables[:3]:
                print(f"  Table {table['number']}: {table['caption'][:80]}...")
        
        # 7. Mathematical Content
        print("\n\n7. MATHEMATICAL CONTENT")
        print("-" * 50)
        print(f"Equations found: {len(paper.equations)}")
        if paper.equations:
            for i, eq in enumerate(paper.equations[:3], 1):
                print(f"  Eq {i}: {eq}")
        
        # 8. Reported Metrics
        print("\n\n8. REPORTED METRICS")
        print("-" * 50)
        if paper.metrics_reported:
            for metric, value in paper.metrics_reported.items():
                print(f"  {metric}: {value}%")
        else:
            print("  No quantitative metrics found")
        
        # 9. Convert to Searchable Format
        print("\n\n9. SEARCHABLE DOCUMENT FORMAT")
        print("-" * 50)
        search_doc = parser.to_search_document(paper)
        print(f"Searchable content length: {len(search_doc['content'])} characters")
        print(f"Metadata fields: {list(search_doc['metadata'].keys())}")
        
        # 10. Performance Stats
        print("\n\n10. PARSER PERFORMANCE")
        print("-" * 50)
        cache_info = parser.get_cache_info()
        print(f"Environment cache size: {cache_info['environment_cache_size']}")
        print(f"Pattern cache stats: {cache_info['pattern_cache_info']}")
        
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        print("\nTip: Make sure the PDF is a valid scientific paper.")


def analyze_multiple_pdfs():
    """Example: Analyze multiple PDFs in a directory."""
    print("\n\n=== BATCH ANALYSIS EXAMPLE ===\n")
    
    parser = ScientificPDFParser()
    pdf_dir = Path("./Exported Items/files")
    
    if not pdf_dir.exists():
        print("PDF directory not found")
        return
    
    # Find all PDFs
    pdf_files = list(pdf_dir.rglob("*.pdf"))[:5]  # Limit to 5 for demo
    
    print(f"Analyzing {len(pdf_files)} PDFs...\n")
    
    # Collect statistics
    all_methods = set()
    all_datasets = set()
    all_keywords = set()
    year_distribution = {}
    
    for pdf_path in pdf_files:
        try:
            paper = parser.parse_pdf(pdf_path)
            
            # Aggregate data
            all_methods.update(paper.methods_mentioned)
            all_datasets.update(paper.datasets_mentioned)
            all_keywords.update(paper.keywords)
            
            year = paper.metadata.get('year', 'Unknown')
            year_distribution[year] = year_distribution.get(year, 0) + 1
            
            print(f"✓ Parsed: {pdf_path.name}")
            
        except Exception as e:
            print(f"✗ Failed: {pdf_path.name} - {e}")
    
    # Summary statistics
    print("\n\nAGGREGATE STATISTICS")
    print("-" * 50)
    print(f"Total methods found: {len(all_methods)}")
    if all_methods:
        print(f"  Methods: {', '.join(sorted(all_methods))}")
    
    print(f"\nTotal datasets found: {len(all_datasets)}")
    if all_datasets:
        print(f"  Datasets: {', '.join(sorted(all_datasets))}")
    
    print(f"\nYear distribution:")
    for year, count in sorted(year_distribution.items()):
        print(f"  {year}: {count} papers")
    
    # Clear cache after batch processing
    parser.clear_cache()
    print("\n✓ Cache cleared")


if __name__ == "__main__":
    # Run single PDF analysis
    main()
    
    # Uncomment to run batch analysis
    # analyze_multiple_pdfs()

# EOF