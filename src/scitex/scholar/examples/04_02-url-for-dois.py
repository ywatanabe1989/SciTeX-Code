#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: 04_02-url-for-dois.py
# ----------------------------------------

"""
Test URL finding for multiple DOIs from CSV.

This script loads DOIs from a CSV file and tests the URL finder
to check if the OpenURL resolution works across different publishers.
"""

import argparse
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd

import scitex as stx
from scitex import log
from scitex.scholar import (
    ScholarAuthManager,
    ScholarBrowserManager,
    ScholarURLFinder,
)

logger = log.getLogger(__name__)


async def test_doi_url_finding(
    doi: str,
    url_finder: ScholarURLFinder,
    use_cache: bool = True
) -> Dict:
    """
    Test URL finding for a single DOI.
    
    Returns:
        dict with URL results and timing
    """
    start_time = datetime.now()
    
    try:
        logger.info(f"Testing DOI: {doi}")
        
        # Find URLs
        result = await url_finder.find_urls(doi=doi)
        
        # Add timing
        end_time = datetime.now()
        result["time_seconds"] = (end_time - start_time).total_seconds()
        result["success"] = bool(result.get("url_openurl_resolved"))
        
        # Check if reached final article
        resolved = result.get("url_openurl_resolved", "")
        result["reached_article"] = (
            "/article/" in resolved or
            "/content/" in resolved or
            "/full/" in resolved or
            ".pdf" in resolved
        )
        result["stopped_at_auth"] = (
            "auth." in resolved.lower() or
            "login" in resolved.lower() or
            "shibboleth" in resolved.lower()
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing DOI {doi}: {e}")
        return {
            "doi": doi,
            "error": str(e),
            "success": False,
            "time_seconds": (datetime.now() - start_time).total_seconds()
        }


async def process_dois_batch(
    dois: List[str],
    url_finder: ScholarURLFinder,
    batch_size: int = 5,
    use_cache: bool = True
) -> List[Dict]:
    """
    Process DOIs in batches to avoid overwhelming the browser.
    """
    results = []
    
    for i in range(0, len(dois), batch_size):
        batch = dois[i:i+batch_size]
        logger.info(f"Processing batch {i//batch_size + 1}: {len(batch)} DOIs")
        
        # Process batch sequentially (to avoid multiple tabs)
        for doi in batch:
            if not doi or pd.isna(doi):
                logger.warning(f"Skipping empty DOI")
                continue
                
            result = await test_doi_url_finding(doi, url_finder, use_cache)
            results.append(result)
            
            # Small delay between requests
            await asyncio.sleep(2)
        
        logger.info(f"Batch complete. Processed {len(results)}/{len(dois)} DOIs")
    
    return results


def load_dois_from_csv(csv_path: Path, limit: Optional[int] = None) -> List[str]:
    """Load DOIs from CSV file."""
    dois = []
    
    df = pd.read_csv(csv_path)
    
    # Find DOI column (could be 'doi', 'DOI', 'doi_url', etc.)
    doi_columns = [col for col in df.columns if 'doi' in col.lower()]
    
    if not doi_columns:
        raise ValueError(f"No DOI column found in {csv_path}")
    
    doi_column = doi_columns[0]
    logger.info(f"Using column '{doi_column}' for DOIs")
    
    # Extract DOIs
    for value in df[doi_column].dropna():
        # Extract DOI from URL if needed
        if 'doi.org/' in str(value):
            doi = value.split('doi.org/')[-1]
        else:
            doi = str(value)
        
        if doi and doi != 'nan':
            dois.append(doi)
    
    if limit:
        dois = dois[:limit]
    
    logger.info(f"Loaded {len(dois)} DOIs from {csv_path}")
    return dois


def generate_report(results: List[Dict], output_dir: Path):
    """Generate summary report of URL finding results."""
    
    # Create summary
    total = len(results)
    successful = sum(1 for r in results if r.get("success"))
    reached_article = sum(1 for r in results if r.get("reached_article"))
    stopped_at_auth = sum(1 for r in results if r.get("stopped_at_auth"))
    errors = sum(1 for r in results if r.get("error"))
    
    # Average time
    times = [r.get("time_seconds", 0) for r in results if "time_seconds" in r]
    avg_time = sum(times) / len(times) if times else 0
    
    report = {
        "summary": {
            "total_dois": total,
            "successful": successful,
            "reached_article": reached_article,
            "stopped_at_auth": stopped_at_auth,
            "errors": errors,
            "success_rate": f"{(successful/total)*100:.1f}%" if total > 0 else "0%",
            "article_reach_rate": f"{(reached_article/total)*100:.1f}%" if total > 0 else "0%",
            "avg_time_seconds": round(avg_time, 2)
        },
        "results": results
    }
    
    # Save report
    report_path = output_dir / "url_finding_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    # Save CSV for easy analysis
    df = pd.DataFrame(results)
    csv_path = output_dir / "url_finding_results.csv"
    df.to_csv(csv_path, index=False)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 URL Finding Summary")
    print("="*60)
    print(f"Total DOIs tested: {total}")
    print(f"Successful: {successful} ({report['summary']['success_rate']})")
    print(f"Reached article: {reached_article} ({report['summary']['article_reach_rate']})")
    print(f"Stopped at auth: {stopped_at_auth}")
    print(f"Errors: {errors}")
    print(f"Average time: {avg_time:.2f} seconds")
    print(f"\nReports saved to:")
    print(f"  - {report_path}")
    print(f"  - {csv_path}")
    
    return report


async def main():
    parser = argparse.ArgumentParser(
        description="Test URL finding for multiple DOIs from CSV"
    )
    parser.add_argument(
        "--csv",
        type=str,
        default="/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/99_maintenance_out/data/scholar/pac_title_and_doi_url.csv",
        help="Path to CSV file with DOIs"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Limit number of DOIs to test (default: 10)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5,
        help="Batch size for processing (default: 5)"
    )
    parser.add_argument(
        "--no-cache",
        "-nc",
        action="store_true",
        help="Disable cache"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Output directory for reports"
    )
    
    args = parser.parse_args()
    
    print("🔗 Multi-DOI URL Finding Test")
    print("="*60)
    
    # Setup output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(f"./url_test_results_{timestamp}")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}")
    
    # Load DOIs
    csv_path = Path(args.csv)
    if not csv_path.exists():
        logger.error(f"CSV file not found: {csv_path}")
        return
    
    dois = load_dois_from_csv(csv_path, limit=args.limit)
    
    if not dois:
        logger.error("No DOIs found in CSV")
        return
    
    print(f"Testing {len(dois)} DOIs from {csv_path.name}")
    print("-"*60)
    
    # Initialize browser
    print("🌐 Initializing authenticated browser...")
    auth_manager = ScholarAuthManager()
    browser_manager = ScholarBrowserManager(
        auth_manager=auth_manager,
        browser_mode="stealth",
        chrome_profile_name="extension",
    )
    
    browser, context = await browser_manager.get_authenticated_browser_and_context_async()
    
    # Create URL finder
    print("🔍 Creating URL finder...")
    url_finder = ScholarURLFinder(
        context=context,
        use_cache=not args.no_cache
    )
    
    # Process DOIs
    print(f"\n📋 Processing {len(dois)} DOIs in batches of {args.batch_size}...")
    print("-"*60)
    
    results = await process_dois_batch(
        dois,
        url_finder,
        batch_size=args.batch_size,
        use_cache=not args.no_cache
    )
    
    # Generate report
    report = generate_report(results, output_dir)
    
    # Show problematic DOIs
    print("\n⚠️ DOIs that stopped at authentication:")
    for r in results:
        if r.get("stopped_at_auth"):
            print(f"  - {r.get('doi')}: {r.get('url_openurl_resolved', 'N/A')[:60]}...")
    
    print("\n❌ DOIs with errors:")
    for r in results:
        if r.get("error"):
            print(f"  - {r.get('doi')}: {r.get('error')[:60]}...")
    
    # Cleanup
    await browser.close()
    print("\n✅ Testing complete!")


if __name__ == "__main__":
    asyncio.run(main())