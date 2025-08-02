#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 15:10:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/examples/scholar_complete_workflow.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./examples/scholar_complete_workflow.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Complete Scholar workflow: From AI2 BibTeX to enhanced library.

This example demonstrates the full value proposition:
1. Start with BibTeX from AI2 services (Semantic Scholar, etc.)
2. Resolve DOIs automatically
3. Download PDFs (automated where possible, browser helper for auth-required)
4. Create organized, searchable library
5. Ready for text mining and analysis
"""

import asyncio
from pathlib import Path

from scitex.scholar import Scholar
from scitex.scholar.io import BibtexIO


async def complete_workflow_example():
    """Complete workflow from BibTeX to enhanced library."""
    print("=" * 80)
    print("SciTeX Scholar - Complete Workflow")
    print("From AI2 BibTeX → DOI Resolution → PDF Download → Text Mining Ready")
    print("=" * 80)
    
    # Initialize Scholar
    scholar = Scholar("research_2025")
    
    # Step 1: Import from AI2 BibTeX
    print("\n1. IMPORT FROM AI2 BIBTEX")
    print("-" * 40)
    
    # Example: BibTeX exported from Semantic Scholar
    ai2_bibtex = """
@article{vaswani2017attention,
  title={Attention is all you need},
  author={Vaswani, Ashish and Shazeer, Noam and Parmar, Niki and Uszkoreit, Jakob and Jones, Llion and Gomez, Aidan N and Kaiser, Lukasz and Polosukhin, Illia},
  journal={Advances in neural information processing systems},
  volume={30},
  year={2017}
}

@article{devlin2018bert,
  title={BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding},
  author={Devlin, Jacob and Chang, Ming-Wei and Lee, Kenton and Toutanova, Kristina},
  journal={arXiv preprint arXiv:1810.04805},
  year={2018}
}

@article{brown2020language,
  title={Language models are few-shot learners},
  author={Brown, Tom and Mann, Benjamin and Ryder, Nick and others},
  journal={Advances in neural information processing systems},
  volume={33},
  pages={1877--1901},
  year={2020}
}
    """
    
    # Save to temp file
    temp_bib = Path("/tmp/ai2_papers.bib")
    with open(temp_bib, 'w') as f:
        f.write(ai2_bibtex)
    
    # Import
    stats = scholar.import_from_bibtex(temp_bib)
    print(f"Imported: {stats['added']} papers")
    print(f"Skipped: {stats['skipped']} (already exist)")
    
    # Step 2: Resolve DOIs
    print("\n2. DOI RESOLUTION")
    print("-" * 40)
    
    papers_without_doi = scholar.get_papers_without_doi()
    print(f"Papers needing DOI resolution: {len(papers_without_doi)}")
    
    for paper in papers_without_doi[:3]:  # Demo with first 3
        print(f"\nResolving: {paper['title'][:60]}...")
        doi = await scholar.resolve_doi(paper['id'])
        if doi:
            print(f"  ✓ Found DOI: {doi}")
        else:
            print(f"  ✗ DOI not found")
    
    # Step 3: Download PDFs
    print("\n3. PDF DOWNLOAD")
    print("-" * 40)
    
    papers_without_pdf = scholar.get_papers_without_pdf()
    print(f"Papers needing PDFs: {len(papers_without_pdf)}")
    
    # Try automated download with screenshots
    for paper in papers_without_pdf[:2]:  # Demo with first 2
        print(f"\nDownloading: {paper['title'][:60]}...")
        
        # First try automated download with screenshot capture
        result = scholar.download_pdf(paper['id'], method="screenshot")
        
        if result['success']:
            print(f"  ✓ Downloaded successfully!")
            print(f"  File: {result['pdf_path']}")
            print(f"  Screenshots: {len(result['screenshots'])}")
        else:
            print(f"  ✗ Automated download failed")
            print(f"  Errors: {result.get('errors', [])}")
            
            # Create browser helper session for manual download
            browser_result = scholar.download_pdf(paper['id'], method="browser")
            print(f"  → Browser helper created: {browser_result['session_id']}")
    
    # Step 4: Show organized library
    print("\n4. ORGANIZED LIBRARY STRUCTURE")
    print("-" * 40)
    
    stats = scholar.get_statistics()
    storage = scholar.get_storage_info()
    
    print(f"Library statistics:")
    print(f"  Total papers: {stats['papers']['total_papers']}")
    print(f"  Papers with DOI: {stats['papers']['with_doi']}")
    print(f"  Papers with PDF: {stats['pdfs']['papers_with_pdf']}")
    print(f"  Total PDFs: {stats['pdfs']['total_pdfs']}")
    print(f"  Storage size: {storage['total_size_mb']:.1f} MB")
    print(f"  PDFs with original names: {storage['pdfs_with_original_names']}")
    print(f"  Human-readable links: {storage['human_readable_links']}")
    
    # Step 5: Ready for text mining
    print("\n5. READY FOR TEXT MINING")
    print("-" * 40)
    
    print("Your enhanced library structure:")
    print("""
    ~/.scitex/scholar/library/research_2025/
    ├── scholar.sqlite                          # Searchable database
    ├── storage/
    │   ├── ABCD1234/
    │   │   ├── 2017.nips-8023.pdf            # Original filename from NIPS
    │   │   ├── metadata.json                  # Complete paper metadata
    │   │   ├── storage_metadata.json          # File metadata
    │   │   └── screenshots/                   # Download history
    │   │       ├── 20250801_150000-attempt-1-initial.jpg
    │   │       └── 20250801_150005-attempt-1-success.jpg
    │   ├── EFGH5678/
    │   │   ├── 1810.04805v2.pdf              # arXiv filename preserved
    │   │   └── ...
    │   └── IJKL9012/
    │       ├── 2020-neurips-language-models.pdf
    │       └── ...
    └── storage-human-readable/
        ├── Vaswani-2017-NeurIPS-ABCD -> ../storage/ABCD1234
        ├── Devlin-2018-arXiv-EFGH -> ../storage/EFGH5678
        └── Brown-2020-NeurIPS-IJKL -> ../storage/IJKL9012
    """)
    
    print("Benefits for text mining:")
    print("- All PDFs have consistent storage structure")
    print("- Original filenames preserved for verification")
    print("- Complete metadata available for each paper")
    print("- Screenshots document any download issues")
    print("- Human-readable links for easy navigation")
    print("- SQLite database for fast searching")
    print("- Ready for parallel processing (directory-based)")
    
    # Example: Access papers for text mining
    print("\n6. EXAMPLE: ACCESSING PAPERS FOR TEXT MINING")
    print("-" * 40)
    
    # Get all papers with PDFs
    all_papers = []
    for paper in scholar.db.get_papers_with_pdf():  # This method would need to be added
        pdf_path = scholar.get_pdf_path(paper['id'])
        if pdf_path:
            all_papers.append({
                'id': paper['id'],
                'title': paper['title'],
                'authors': paper['authors'],
                'year': paper['year'],
                'doi': paper.get('doi'),
                'pdf_path': pdf_path,
                'storage_key': paper['storage_key']
            })
    
    print(f"Found {len(all_papers)} papers with PDFs ready for text mining:")
    for p in all_papers[:3]:
        print(f"  - {p['title'][:60]}...")
        print(f"    PDF: {p['pdf_path']}")
        print(f"    Key: {p['storage_key']}")
    
    return scholar


def show_value_proposition():
    """Show the value proposition of the Scholar system."""
    print("\n" + "=" * 80)
    print("VALUE PROPOSITION")
    print("=" * 80)
    
    print("""
    1. START WITH AI2 SERVICES:
       - Export BibTeX from Semantic Scholar
       - Get paper recommendations from AI2
       - Import existing literature collections
       
    2. AUTOMATIC ENHANCEMENT:
       - DOI resolution from partial metadata
       - URL resolution via OpenURL/OpenAthens
       - Metadata enrichment from multiple sources
       
    3. INTELLIGENT PDF DOWNLOAD:
       - Automated download where possible
       - Screenshot capture for debugging
       - Browser helper for auth-required papers
       - Preserves original filenames
       
    4. ORGANIZED STORAGE:
       - Directory-based for concurrent access
       - Human-readable organization
       - Complete metadata preservation
       - Download history with screenshots
       
    5. READY FOR TEXT MINING:
       - Consistent structure for all papers
       - Fast database queries
       - Parallel processing support
       - All metadata available
       
    This creates a complete pipeline from literature discovery to analysis!
    """)


if __name__ == "__main__":
    # Run the complete workflow
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        scholar = loop.run_until_complete(complete_workflow_example())
        show_value_proposition()
        
        print("\n" + "=" * 80)
        print("NEXT STEPS")
        print("=" * 80)
        print("""
        1. Check the browser helper for papers requiring manual download
        2. Use text mining tools on the organized PDF collection
        3. Export enhanced BibTeX with all resolved metadata
        4. Share your library or migrate to other tools easily
        
        The Scholar system has created a solid foundation for your research!
        """)
        
    finally:
        loop.close()

# EOF