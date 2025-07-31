#!/usr/bin/env python3
"""Example: Complete Scholar workflow with MCP server."""

import json
from pathlib import Path


def complete_workflow_example():
    """Demonstrate the complete Scholar workflow through MCP."""
    
    print("=== SciTeX Scholar MCP - Complete Workflow ===\n")
    print("This example shows the full workflow from search to PDF download.\n")
    
    # Step 1: Search for papers
    print("Step 1: Search for papers")
    print("-" * 50)
    
    search_params = {
        "query": "machine learning climate change 2024",
        "limit": 5,
        "sources": ["crossref", "pubmed", "semantic_scholar"]
    }
    
    print("MCP Tool: search_papers")
    print(f"Parameters: {json.dumps(search_params, indent=2)}")
    print("\nExpected result: List of papers with titles, authors, years\n")
    
    # Step 2: Save to BibTeX
    print("\nStep 2: Save search results to BibTeX")
    print("-" * 50)
    
    # In real usage, papers would come from search results
    save_params = {
        "papers": "[papers from search]",
        "output_path": "./ml_climate_2024.bib"
    }
    
    print("Using Scholar module to save BibTeX")
    print(f"Output: {save_params['output_path']}\n")
    
    # Step 3: Enrich BibTeX
    print("\nStep 3: Enrich BibTeX with metadata")
    print("-" * 50)
    
    enrich_params = {
        "bibtex_path": "./ml_climate_2024.bib",
        "output_path": "./ml_climate_2024_enriched.bib",
        "add_abstracts": True,
        "add_impact_factors": True
    }
    
    print("MCP Tool: enrich_bibtex")
    print(f"Parameters: {json.dumps(enrich_params, indent=2)}")
    print("\nThis will add:")
    print("- Missing DOIs")
    print("- Impact factors (JCR 2024)")
    print("- Citation counts")
    print("- Abstracts\n")
    
    # Step 4: Resolve DOIs (if needed)
    print("\nStep 4: Resolve missing DOIs")
    print("-" * 50)
    
    resolve_params = {
        "papers": [
            {
                "title": "Deep Learning for Climate Prediction",
                "authors": ["Smith, J.", "Doe, A."],
                "year": 2024
            }
        ],
        "progress_file": "./doi_resolution_progress.json"
    }
    
    print("MCP Tool: resolve_dois")
    print(f"Parameters: {json.dumps(resolve_params, indent=2)}")
    print("\nFeatures:")
    print("- Resumable if interrupted")
    print("- Searches CrossRef, PubMed, Semantic Scholar")
    print("- Shows rsync-style progress\n")
    
    # Step 5: Resolve OpenURLs
    print("\nStep 5: Get publisher URLs via OpenURL")
    print("-" * 50)
    
    openurl_params = {
        "dois": ["10.1234/example.2024.001", "10.5678/example.2024.002"],
        "resolver_url": "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41",
        "progress_file": "./openurl_progress.json"
    }
    
    print("MCP Tool: resolve_openurls")
    print(f"Parameters: {json.dumps(openurl_params, indent=2)}")
    print("\nUses institutional resolver for full-text access\n")
    
    # Step 6: Download PDFs with Crawl4AI
    print("\nStep 6: Download PDFs using Crawl4AI")
    print("-" * 50)
    
    # Configure Crawl4AI first
    config_params = {
        "profile_name": "ml_climate_papers",
        "browser_type": "chromium",
        "headless": False,  # Show browser for first run
        "simulate_user": True,
        "viewport_size": [1920, 1080]
    }
    
    print("MCP Tool: configure_crawl4ai")
    print(f"Parameters: {json.dumps(config_params, indent=2)}")
    
    # Then download
    download_params = {
        "dois": ["10.1234/example.2024.001", "10.5678/example.2024.002"],
        "output_dir": "./pdfs/ml_climate_2024",
        "strategy": "crawl4ai",
        "max_concurrent": 2
    }
    
    print("\nMCP Tool: download_pdfs_batch")
    print(f"Parameters: {json.dumps(download_params, indent=2)}")
    print("\nCrawl4AI advantages:")
    print("- Bypasses anti-bot measures")
    print("- Handles JavaScript-rendered PDFs")
    print("- Maintains authentication sessions")
    print("- Free and open source\n")
    
    # Step 7: Check download status
    print("\nStep 7: Monitor download progress")
    print("-" * 50)
    
    status_params = {
        "batch_id": "download_20250801_140000"
    }
    
    print("MCP Tool: get_download_status")
    print(f"Parameters: {json.dumps(status_params, indent=2)}")
    print("\nProvides:")
    print("- Total/completed/failed counts")
    print("- Individual paper status")
    print("- Paths to downloaded PDFs\n")
    
    # Summary
    print("\n" + "=" * 70)
    print("COMPLETE WORKFLOW SUMMARY")
    print("=" * 70)
    
    print("\n1. Search papers → 2. Save as BibTeX → 3. Enrich metadata")
    print("4. Resolve DOIs → 5. Get publisher URLs → 6. Download PDFs")
    print("7. Monitor progress")
    
    print("\nAll steps are:")
    print("✓ Resumable - Can continue after interruption")
    print("✓ Cached - Avoids redundant API calls")
    print("✓ Rate-limited - Respects API limits")
    print("✓ Progress-tracked - Shows real-time status")
    
    print("\nMCP Integration Benefits:")
    print("- Claude can execute entire workflow")
    print("- Each step exposed as a tool")
    print("- Async operations handled automatically")
    print("- Results returned as structured JSON")


def troubleshooting_guide():
    """Show common issues and solutions."""
    
    print("\n\n=== Troubleshooting Guide ===\n")
    
    issues = [
        {
            "issue": "Crawl4AI not installed",
            "solution": "pip install crawl4ai[all] && playwright install chromium"
        },
        {
            "issue": "Authentication required",
            "solution": "Use profile with saved cookies or configure OpenAthens"
        },
        {
            "issue": "Rate limiting errors",
            "solution": "Reduce max_concurrent or add delays between requests"
        },
        {
            "issue": "PDFs not downloading",
            "solution": "Try headless=False to debug, check JavaScript execution"
        },
        {
            "issue": "Import errors",
            "solution": "Ensure scitex is installed: pip install -e ."
        }
    ]
    
    for item in issues:
        print(f"Issue: {item['issue']}")
        print(f"Solution: {item['solution']}")
        print()


if __name__ == "__main__":
    # Run examples
    complete_workflow_example()
    troubleshooting_guide()
    
    print("\n" + "=" * 70)
    print("To use this workflow in Claude:")
    print("1. Install the MCP server")
    print("2. Configure in Claude settings")
    print("3. Use the tools shown above")
    print("=" * 70)