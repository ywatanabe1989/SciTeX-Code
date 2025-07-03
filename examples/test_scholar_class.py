#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-03 09:35:00 (ywatanabe)"
# File: ./examples/test_scholar_class.py
# ----------------------------------------
import os
__FILE__ = (
    "./examples/test_scholar_class.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Test script for the new Scholar class.

Functionalities:
  - Tests Scholar class initialization
  - Tests basic search functionality
  - Tests PaperCollection methods
  - Verifies error handling
  - Tests workspace management

Dependencies:
  - scitex.scholar module
  - Internet connection for search tests

Input:
  - None (hardcoded test queries)

Output:
  - Test results printed to console
  - Creates temporary test files in ./test_scholar_workspace/
"""

"""Imports"""
import sys
import warnings
from pathlib import Path

# Add project root to path for testing
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from scitex.scholar import Scholar, PaperCollection
    print("✅ Successfully imported Scholar and PaperCollection")
except ImportError as e:
    print(f"❌ Failed to import Scholar: {e}")
    # Try direct import as fallback
    try:
        sys.path.insert(0, str(project_root / "src"))
        from scitex.scholar._scholar import Scholar, PaperCollection
        print("✅ Successfully imported Scholar from _scholar module")
    except ImportError as e2:
        print(f"❌ Failed fallback import: {e2}")
        sys.exit(1)

"""Functions & Classes"""
def test_scholar_initialization():
    """Test Scholar class initialization."""
    print("\n=== Testing Scholar Initialization ===")
    
    try:
        # Test basic initialization
        scholar = Scholar()
        print("✅ Basic Scholar initialization successful")
        
        # Test with custom parameters  
        test_workspace = Path("./test_scholar_workspace")
        scholar_custom = Scholar(
            workspace_dir=test_workspace,
            enrich_by_default=False,
            cache_results=True
        )
        print("✅ Custom Scholar initialization successful")
        
        # Test workspace info
        info = scholar_custom.get_workspace_info()
        print(f"✅ Workspace info retrieved: {len(info)} items")
        
        return scholar, scholar_custom
        
    except Exception as e:
        print(f"❌ Scholar initialization failed: {e}")
        return None, None


def test_paper_collection():
    """Test PaperCollection functionality."""
    print("\n=== Testing PaperCollection ===")
    
    try:
        # Create mock papers for testing
        from scitex.scholar._paper import Paper
        
        # Test with empty collection
        empty_collection = PaperCollection([])
        print(f"✅ Empty collection: {len(empty_collection)} papers")
        
        # Create test papers
        papers = []
        for i in range(3):
            paper = Paper(
                title=f"Test Paper {i+1}",
                authors=[f"Author {i+1}"],
                abstract=f"Abstract for test paper {i+1}",
                year=2020 + i,
                source="test"
            )
            # Add optional attributes
            paper.citation_count = 10 * (i + 1)
            papers.append(paper)
        
        collection = PaperCollection(papers)
        print(f"✅ Test collection created: {len(collection)} papers")
        
        # Test filtering
        recent = collection.filter(year_min=2021)
        print(f"✅ Filter test: {len(recent)} papers from 2021+")
        
        # Test sorting
        sorted_collection = collection.sort_by("citations")
        print(f"✅ Sort test: {len(sorted_collection)} papers sorted")
        
        # Test slicing
        first_two = collection[:2]
        print(f"✅ Slice test: {len(first_two)} papers from slice")
        
        return True
        
    except Exception as e:
        print(f"❌ PaperCollection test failed: {e}")
        return False


def test_basic_search(scholar):
    """Test basic search functionality."""
    print("\n=== Testing Basic Search ===")
    
    if not scholar:
        print("❌ No scholar instance available for testing")
        return False
    
    try:
        # Test search with minimal parameters
        print("Testing search with query 'machine learning'...")
        papers = scholar.search("machine learning", limit=3, show_progress=True)
        
        print(f"✅ Search completed: {len(papers)} papers found")
        
        if len(papers) > 0:
            paper = papers[0]
            print(f"✅ First paper: {paper.title[:50]}...")
            print(f"   Authors: {', '.join(paper.authors[:2]) if paper.authors else 'Unknown'}")
            print(f"   Year: {paper.year}, Citations: {paper.citation_count}")
            
            # Check if enrichment worked
            if hasattr(paper, 'impact_factor') and paper.impact_factor:
                print(f"   📊 Impact Factor: {paper.impact_factor}")
                print("✅ Paper enrichment detected")
            else:
                print("ℹ️  No enrichment data (may be expected if service unavailable)")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic search test failed: {e}")
        warnings.warn(f"Search error: {e}")
        return False


def test_search_with_filters(scholar):
    """Test search with filtering and sorting."""
    print("\n=== Testing Search with Filters ===")
    
    if not scholar:
        print("❌ No scholar instance available for testing")
        return False
    
    try:
        # Test search with filters
        print("Testing filtered search...")
        papers = scholar.search("neural networks", limit=10, show_progress=False)
        
        if len(papers) > 0:
            # Test filtering
            recent_papers = papers.filter(year_min=2020)
            print(f"✅ Filter by year: {len(recent_papers)}/{len(papers)} papers from 2020+")
            
            # Test sorting
            sorted_papers = papers.sort_by("citations", reverse=True)
            print(f"✅ Sort by citations: {len(sorted_papers)} papers sorted")
            
            # Test chaining
            if len(papers) >= 5:
                chained = papers.filter(year_min=2018).sort_by("year")
                print(f"✅ Chained operations: {len(chained)} papers after filtering and sorting")
        else:
            print("ℹ️  No papers found for filter testing")
        
        return True
        
    except Exception as e:
        print(f"❌ Filter test failed: {e}")
        return False


def test_bibliography_generation(scholar):
    """Test bibliography generation."""
    print("\n=== Testing Bibliography Generation ===")
    
    if not scholar:
        print("❌ No scholar instance available for testing")
        return False
    
    try:
        # Get some papers for bibliography
        papers = scholar.search("artificial intelligence", limit=3, show_progress=False)
        
        if len(papers) > 0:
            # Test BibTeX generation
            test_bib_file = "./test_bibliography.bib"
            bib_path = papers.save_bibliography(test_bib_file)
            
            # Check if file was created
            if Path(bib_path).exists():
                file_size = Path(bib_path).stat().st_size
                print(f"✅ Bibliography created: {bib_path} ({file_size} bytes)")
                
                # Clean up test file
                Path(bib_path).unlink()
                print("✅ Test file cleaned up")
            else:
                print("❌ Bibliography file not created")
                return False
        else:
            print("ℹ️  No papers available for bibliography test")
        
        return True
        
    except Exception as e:
        print(f"❌ Bibliography test failed: {e}")
        return False


def test_error_handling():
    """Test error handling and fallbacks."""
    print("\n=== Testing Error Handling ===")
    
    try:
        # Test with invalid workspace (should handle gracefully)
        # Use a more reasonable invalid path that won't cause permission errors
        invalid_path = Path("./nonexistent_directory_12345")
        scholar = Scholar(workspace_dir=invalid_path)
        print("✅ Handled invalid workspace path gracefully")
        
        # Test search with potentially failing components
        papers = scholar.search("test query", limit=1, show_progress=False)
        print(f"✅ Search with potential failures: {len(papers)} papers")
        
        # Test with disabled enrichment
        scholar_no_enrich = Scholar(enrich_by_default=False)
        papers_no_enrich = scholar_no_enrich.search("test", limit=1, show_progress=False)
        print(f"✅ Search without enrichment: {len(papers_no_enrich)} papers")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


def run_all_tests():
    """Run all tests and report results."""
    print("🔬 Starting Scholar Class Tests")
    print("=" * 50)
    
    test_results = []
    
    # Test 1: Initialization
    scholar, scholar_custom = test_scholar_initialization()
    test_results.append(scholar is not None)
    
    # Test 2: PaperCollection
    collection_ok = test_paper_collection()
    test_results.append(collection_ok)
    
    # Test 3: Basic search
    search_ok = test_basic_search(scholar)
    test_results.append(search_ok)
    
    # Test 4: Search with filters
    filter_ok = test_search_with_filters(scholar)
    test_results.append(filter_ok)
    
    # Test 5: Bibliography generation
    bib_ok = test_bibliography_generation(scholar)
    test_results.append(bib_ok)
    
    # Test 6: Error handling
    error_ok = test_error_handling()
    test_results.append(error_ok)
    
    # Results summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    test_names = [
        "Scholar Initialization",
        "PaperCollection Methods",
        "Basic Search",
        "Search with Filters",
        "Bibliography Generation",
        "Error Handling"
    ]
    
    passed = sum(test_results)
    total = len(test_results)
    
    for name, result in zip(test_names, test_results):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("-" * 50)
    print(f"📈 OVERALL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Scholar class is working correctly.")
    elif passed >= total * 0.8:
        print("✅ Most tests passed. Scholar class is mostly functional.")
    else:
        print("⚠️  Some tests failed. Scholar class may have issues.")
    
    return passed == total


def main():
    """Main test function."""
    print(__doc__)
    
    # Run tests
    all_passed = run_all_tests()
    
    # Exit with appropriate code
    exit_code = 0 if all_passed else 1
    print(f"\nExiting with code: {exit_code}")
    
    return exit_code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

# EOF