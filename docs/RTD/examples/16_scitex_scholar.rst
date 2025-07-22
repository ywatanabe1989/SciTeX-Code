16 SciTeX Scholar
=================

.. note::
   This page is generated from the Jupyter notebook `16_scitex_scholar.ipynb <https://github.com/scitex/scitex/blob/main/examples/16_scitex_scholar.ipynb>`_
   
   To run this notebook interactively:
   
   .. code-block:: bash
   
      cd examples/
      jupyter notebook 16_scitex_scholar.ipynb


This notebook demonstrates the new simplified ``Scholar`` class for
scientific literature management with comprehensive impact factor
support.

Key Improvements
----------------

-  **Single entry point**: One ``Scholar`` class for all functionality
-  **Default enrichment**: Papers are enriched with journal metrics by
   default
-  **No async complexity**: Simple synchronous API that works in
   notebooks
-  **Chainable methods**: Fluent interface for common workflows
-  **Smart defaults**: Works out-of-the-box with reasonable settings
-  **📊 Impact Factor Integration**: Automatic journal impact factor
   lookup using the ``impact_factor`` package
-  **🏆 Journal Rankings**: Quartile and ranking information for
   comprehensive evaluation

Installation & Setup
--------------------

Make sure you have scitex and impact_factor installed:

.. code:: bash

   pip install -e ~/proj/scitex_repo
   # impact_factor package should be automatically available

.. code:: ipython3

    # Import the new simplified interface
    from scitex.scholar import Scholar
    
    # Import impact factor tools for direct database access
    import sqlite3
    import pandas as pd
    import impact_factor
    
    # Optional: Set up API keys for enhanced features
    import os
    # os.environ['SEMANTIC_SCHOLAR_API_KEY'] = 'your_key_here'
    # os.environ['OPENAI_API_KEY'] = 'your_key_here'
    
    print("✅ Scholar and Impact Factor tools loaded successfully!")
    print(f"📊 Impact Factor database: {impact_factor.DEFAULT_DB}")
    print(f"📈 Database size: {os.path.getsize(impact_factor.DEFAULT_DB) / 1024 / 1024:.1f} MB")

1. Quick Start - Simple Search
------------------------------

The fastest way to get started:

.. code:: ipython3

    # Quick search using Scholar class directly with impact factor enrichment
    scholar = Scholar(enrich_by_default=True)  # Ensure enrichment is enabled
    papers = scholar.search("deep learning neuroscience", limit=5)
    
    # Display results with comprehensive impact factor information
    print(f"📚 Found {len(papers)} papers (automatically enriched with impact factors):\n")
    for i, paper in enumerate(papers, 1):
        print(f"{i}. {paper.title}")
        print(f"   Authors: {', '.join(paper.authors[:2]) if paper.authors else 'Unknown'}...")
        print(f"   Journal: {paper.journal if paper.journal else 'Unknown'}")
        print(f"   Year: {paper.year}, Citations: {paper.citation_count}")
        
        # Show enriched impact factor data if available
        if hasattr(paper, 'impact_factor') and paper.impact_factor:
            print(f"   📊 Journal Impact Factor: {paper.impact_factor}")
        if hasattr(paper, 'journal_quartile') and paper.journal_quartile:
            print(f"   🏆 Journal Quartile: {paper.journal_quartile}")
        if hasattr(paper, 'journal_ranking') and paper.journal_ranking:
            print(f"   📈 Journal Ranking: {paper.journal_ranking}")
        
        # Additional impact factor lookup if not automatically enriched
        if paper.journal and (not hasattr(paper, 'impact_factor') or not paper.impact_factor):
            # Direct lookup from impact_factor database
            try:
                conn = sqlite3.connect(impact_factor.DEFAULT_DB)
                query = "SELECT factor, jcr FROM factor WHERE journal LIKE ? ORDER BY factor DESC LIMIT 1"
                result = pd.read_sql_query(query, conn, params=[f'%{paper.journal}%'])
                conn.close()
                
                if len(result) > 0:
                    print(f"   📊 Impact Factor (manual lookup): {result.iloc[0]['factor']:.3f}")
                    print(f"   🏆 Quartile (manual lookup): {result.iloc[0]['jcr']}")
            except Exception as e:
                print(f"   ⚠️ Could not lookup impact factor: {e}")
        
        print()

2. Using the Scholar Class
--------------------------

For more control and advanced features:

.. code:: ipython3

    # Initialize Scholar with custom settings
    scholar = Scholar(
        email="researcher@university.edu",  # For PubMed access
        enrich_by_default=True,              # Default enrichment (can be turned off)
        workspace_dir="./scholar_workspace"  # Custom workspace
    )
    
    # Get workspace info
    info = scholar.get_workspace_info()
    print("Scholar Workspace Info:")
    for key, value in info.items():
        print(f"  {key}: {value}")

3. Enhanced Search with Filtering
---------------------------------

Search and filter papers using the fluent interface:

.. code:: ipython3

    # Search with filtering and sorting
    recent_papers = scholar.search("neural networks", limit=20) \
                          .filter(year_min=2020, min_citations=10) \
                          .sort_by("citations")
    
    print(f"Found {len(recent_papers)} recent high-impact papers:\n")
    
    for i, paper in enumerate(recent_papers[:5], 1):
        print(f"{i}. {paper.title[:80]}...")
        print(f"   Year: {paper.year}, Citations: {paper.citation_count}")
        if hasattr(paper, 'impact_factor') and paper.impact_factor:
            print(f"   Journal IF: {paper.impact_factor}")
        print()

4. Multiple Topic Search
------------------------

Search multiple topics and combine results:

.. code:: ipython3

    # Search multiple related topics
    topics = [
        "transformer neural networks",
        "attention mechanisms deep learning",
        "BERT language models"
    ]
    
    all_papers = scholar.search_multiple(
        queries=topics,
        papers_per_query=5,
        combine_results=True  # Automatically removes duplicates
    )
    
    print(f"Combined search found {len(all_papers)} unique papers")
    
    # Filter for high-impact recent work
    high_impact = all_papers.filter(year_min=2019, min_citations=50)
    print(f"High-impact recent papers: {len(high_impact)}")

5. Bibliography Generation
--------------------------

Generate enriched bibliographies with automatic formatting:

.. code:: ipython3

    # Search for papers on a specific topic with impact factor filtering
    ml_papers = scholar.search("machine learning interpretability", limit=15)
    
    # Filter for quality papers with impact factor consideration
    quality_papers = ml_papers.filter(year_min=2018, min_citations=20)
    
    print(f"📊 Generating enriched bibliography for {len(quality_papers)} papers...")
    
    # Enrich papers with impact factor information if not already enriched
    def enrich_paper_with_impact_factor(paper):
        """Add impact factor information to a paper if available."""
        if not paper.journal:
            return paper
        
        try:
            conn = sqlite3.connect(impact_factor.DEFAULT_DB)
            query = """
            SELECT factor, jcr, journal_abbr 
            FROM factor 
            WHERE journal LIKE ? 
            ORDER BY factor DESC 
            LIMIT 1
            """
            result = pd.read_sql_query(query, conn, params=[f'%{paper.journal}%'])
            conn.close()
            
            if len(result) > 0:
                paper.impact_factor = result.iloc[0]['factor']
                paper.journal_quartile = result.iloc[0]['jcr']
                paper.journal_abbr = result.iloc[0]['journal_abbr']
            
        except Exception as e:
            print(f"Could not enrich {paper.journal}: {e}")
        
        return paper
    
    # Enrich all papers
    enriched_papers = [enrich_paper_with_impact_factor(paper) for paper in quality_papers]
    
    # Show impact factor distribution
    impact_factors = [p.impact_factor for p in enriched_papers if hasattr(p, 'impact_factor') and p.impact_factor]
    if impact_factors:
        print(f"📈 Impact Factor Statistics:")
        print(f"   Papers with IF data: {len(impact_factors)}/{len(enriched_papers)}")
        print(f"   Average IF: {sum(impact_factors)/len(impact_factors):.3f}")
        print(f"   Highest IF: {max(impact_factors):.3f}")
        print(f"   Lowest IF: {min(impact_factors):.3f}")
    
    # Save as enriched BibTeX (includes impact factors)
    bib_file = "ml_interpretability_enriched.bib"
    print(f"\n💾 Saving enriched bibliography to: {bib_file}")
    
    try:
        # Generate enriched BibTeX entries
        with open(bib_file, 'w', encoding='utf-8') as f:
            for paper in enriched_papers:
                bibtex = paper.to_bibtex(include_enriched=True)
                f.write(bibtex + "\n\n")
        
        print(f"✅ Successfully saved {len(enriched_papers)} enriched entries")
        
    except Exception as e:
        print(f"❌ Error saving bibliography: {e}")
    
    # Preview first enriched entry
    if enriched_papers:
        print("\n📄 Sample enriched BibTeX entry:")
        print("=" * 60)
        try:
            sample_bibtex = enriched_papers[0].to_bibtex(include_enriched=True)
            # Show first 500 characters
            preview = sample_bibtex[:500] + "..." if len(sample_bibtex) > 500 else sample_bibtex
            print(preview)
        except Exception as e:
            print(f"Could not generate sample BibTeX: {e}")
    
    # Show papers by impact factor quartile
    quartile_distribution = {}
    for paper in enriched_papers:
        if hasattr(paper, 'journal_quartile') and paper.journal_quartile:
            quartile_distribution[paper.journal_quartile] = quartile_distribution.get(paper.journal_quartile, 0) + 1
    
    if quartile_distribution:
        print(f"\n🏆 Journal Quartile Distribution:")
        for quartile, count in sorted(quartile_distribution.items()):
            print(f"   {quartile}: {count} papers")

6. PDF Downloads
----------------

Download PDFs for open-access papers:

.. code:: ipython3

    # Search for open-access papers
    oa_papers = scholar.search("computer vision", limit=5)
    
    # Filter for potentially open-access papers
    recent_papers = oa_papers.filter(year_min=2020)
    
    print(f"Attempting to download PDFs for {len(recent_papers)} papers...")
    
    try:
        # Download PDFs (max 3 to avoid overwhelming servers)
        downloaded = scholar.download_pdfs(recent_papers, max_downloads=3)
        
        print(f"\nSuccessfully downloaded {len(downloaded)} PDFs:")
        for title, path in downloaded.items():
            print(f"  - {title[:60]}... → {path.name}")
            
    except Exception as e:
        print(f"PDF download failed: {e}")
        print("Note: PDF downloads require papers to be open-access")

7. Local PDF Indexing and Search
--------------------------------

Build searchable index from your local PDF collection:

.. code:: ipython3

    # If you have PDFs downloaded, build a local index
    pdf_dir = "./scholar_workspace/pdfs"
    
    try:
        import os
        if os.path.exists(pdf_dir) and os.listdir(pdf_dir):
            print(f"Building search index from {pdf_dir}...")
            index_path = scholar.build_local_index(pdf_dir)
            print(f"Index created: {index_path}")
            
            # Search your local collection
            local_results = scholar.search_local("neural networks")
            print(f"\nFound {len(local_results)} papers in local collection")
            
        else:
            print("No PDFs found for indexing. Download some PDFs first.")
            
    except Exception as e:
        print(f"Local indexing failed: {e}")

8. Advanced Features
--------------------

Paper Collection Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    # Get a larger collection for analysis
    ai_papers = scholar.search("artificial intelligence", limit=30)
    
    # Analyze the collection
    print("Collection Analysis:")
    print(f"Total papers: {len(ai_papers)}")
    
    # Year distribution
    years = [p.year for p in ai_papers if p.year]
    if years:
        print(f"Year range: {min(years)} - {max(years)}")
        from collections import Counter
        year_counts = Counter(years)
        print("Papers by year:")
        for year, count in sorted(year_counts.items(), reverse=True)[:5]:
            print(f"  {year}: {count} papers")
    
    # Citation analysis
    citations = [p.citation_count for p in ai_papers if p.citation_count]
    if citations:
        print(f"\nCitation statistics:")
        print(f"  Average citations: {sum(citations)/len(citations):.1f}")
        print(f"  Max citations: {max(citations)}")
        print(f"  Highly cited (>100): {sum(1 for c in citations if c > 100)}")
    
    # Export to different formats
    data_export = ai_papers.to_dict()
    print(f"\nExported {len(data_export)} papers to dictionary format")

Comparison with Old API
~~~~~~~~~~~~~~~~~~~~~~~

Here’s how the new API compares to the old approach:

.. code:: ipython3

    print("=== OLD API (Complex) ===")
    print("""
    # Old way - multiple imports and manual enrichment
    from scitex.scholar import search_papers, PaperEnrichmentService, generate_enriched_bibliography
    import asyncio
    
    # Async search
    papers = await search_papers("deep learning", limit=10)
    
    # Manual enrichment
    enricher = PaperEnrichmentService()
    enriched_papers = enricher._enrich_papers(papers)
    
    # Manual bibliography generation
    generate_enriched_bibliography(enriched_papers, "output.bib", enrich=False)
    """)
    
    print("\n=== NEW API (Simple) ===")
    print("""
    # New way - one class, automatic enrichment
    from scitex.scholar import Scholar
    
    # Simple search with automatic enrichment
    scholar = Scholar()
    papers = scholar.search("deep learning", limit=10)
    
    # One-liner bibliography with enrichment
    papers.save_bibliography("output.bib")
    """)
    
    print("\n✅ The new API is much simpler and more intuitive!")

9. Best Practices
-----------------

Performance Tips
~~~~~~~~~~~~~~~~

.. code:: ipython3

    # 1. Reuse Scholar instance for multiple searches
    scholar = Scholar(enrich_by_default=True)  # Initialize once
    
    # Multiple searches reuse the same components
    papers1 = scholar.search("topic 1", limit=5)
    papers2 = scholar.search("topic 2", limit=5)
    
    # 2. Use appropriate limits
    # For exploration: limit=10-20
    # For comprehensive reviews: limit=50-100
    # For quick checks: limit=5
    
    # 3. Filter early to reduce processing
    recent_quality = scholar.search("machine learning", limit=50) \
                           .filter(year_min=2020, min_citations=10) \
                           .sort_by("impact_factor")
    
    print(f"Filtered to {len(recent_quality)} high-quality recent papers")

Error Handling
~~~~~~~~~~~~~~

.. code:: ipython3

    # The Scholar class handles errors gracefully
    try:
        # Even if some components fail, basic search should work
        papers = scholar.search("test query", limit=3)
        print(f"Search successful: found {len(papers)} papers")
        
    except Exception as e:
        print(f"Search failed: {e}")
        # Fallback to basic Scholar search with minimal features
        scholar_basic = Scholar(enrich_by_default=False)
        papers = scholar_basic.search("test query", limit=3)
        print(f"Fallback search: found {len(papers)} papers")

Summary
-------

The new ``Scholar`` class provides:

| ✅ **Single entry point** - No need to import multiple classes
| ✅ **Default enrichment** - Papers automatically get journal metrics
| ✅ **Simple sync API** - No async/await complexity
| ✅ **Chainable methods** - Fluent interface for workflows
| ✅ **Smart defaults** - Works out-of-the-box
| ✅ **Progress feedback** - See what’s happening during long operations
| ✅ **Error resilience** - Graceful fallbacks when components fail

Quick Reference
~~~~~~~~~~~~~~~

.. code:: python

   # Basic usage
   from scitex.scholar import Scholar
   scholar = Scholar()
   papers = scholar.search("your topic", limit=20)
   papers.save_bibliography("papers.bib")

   # Advanced workflow
   papers = scholar.search("topic", limit=50) \
                  .filter(year_min=2020, min_citations=10) \
                  .sort_by("impact_factor")
   scholar.download_pdfs(papers, max_downloads=5)

The Scholar class maintains backward compatibility with all existing
components while providing a much simpler interface for new users.
