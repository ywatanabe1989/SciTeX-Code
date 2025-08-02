#!/usr/bin/env python3
"""Example demonstrating enhanced PDF download with pre-flight checks."""

import asyncio
import sys
sys.path.insert(0, '../src')

from pathlib import Path
from scitex.scholar.download._PDFDownloader import PDFDownloader
from scitex.scholar.validation import run_preflight_checks


async def enhanced_batch_download_with_preflight(downloader, identifiers, **kwargs):
    """Enhanced batch download with pre-flight checks."""
    
    print("=== Running Pre-flight Checks ===")
    
    # Run pre-flight checks
    try:
        preflight_results = await run_preflight_checks(
            download_dir=kwargs.get('output_dir', downloader.download_dir),
            use_translators=downloader.use_translators,
            use_playwright=downloader.use_playwright,
            use_openathens=downloader.use_openathens,
            zenrows_api_key=getattr(downloader, 'zenrows_api_key', None),
            openurl_resolver=getattr(downloader, 'openurl_resolver', None),
        )
        
        # Display results
        print(f"\nAll checks passed: {preflight_results['all_passed']}")
        
        if preflight_results['warnings']:
            print("\n⚠️  Warnings:")
            for warning in preflight_results['warnings']:
                print(f"  - {warning}")
        
        if preflight_results['errors']:
            print("\n❌ Errors:")
            for error in preflight_results['errors']:
                print(f"  - {error}")
            
            print("\n📋 Recommendations:")
            for rec in preflight_results['recommendations']:
                print(f"  - {rec}")
            
            # Don't proceed if critical errors
            if preflight_results['errors']:
                print("\n❗ Critical errors found. Please fix them before proceeding.")
                return {}
        
        # Show check details
        print("\n✅ Check Results:")
        for check, passed in preflight_results['checks'].items():
            status = "✓" if passed else "✗"
            print(f"  {status} {check}: {passed}")
        
    except Exception as e:
        print(f"\n❌ Pre-flight checks failed: {e}")
        return {}
    
    print("\n=== Proceeding with Downloads ===\n")
    
    # Run the actual download
    results = await downloader.batch_download_async(identifiers, **kwargs)
    
    return results


async def main():
    """Demonstrate enhanced PDF download workflow."""
    
    # Example DOIs
    dois = [
        "10.1038/s41586-021-03819-2",  # Nature paper
        "10.1126/science.abj8754",      # Science paper
        "10.1016/j.cell.2021.07.012",  # Cell paper
    ]
    
    # Initialize downloader with various options
    downloader = PDFDownloader(
        download_dir=Path("./test_pdfs"),
        use_translators=True,
        use_playwright=True,
        use_openathens=False,  # Set to True if you have OpenAthens
        zenrows_api_key=None,  # Add your key if you have one
        max_concurrent=2,
        debug_mode=True,
    )
    
    # Run enhanced download with pre-flight checks
    results = await enhanced_batch_download_with_preflight(
        downloader,
        dois,
        output_dir=Path("./test_pdfs"),
        organize_by_year=True,
        show_progress=True,
        return_detailed=True,
    )
    
    # Display results
    print("\n=== Download Results ===")
    success_count = 0
    for doi, result in results.items():
        if isinstance(result, dict) and result.get('path'):
            print(f"✓ {doi}: {result['path']} (via {result.get('method', 'unknown')})")
            success_count += 1
        else:
            print(f"✗ {doi}: Failed")
    
    print(f"\nTotal: {success_count}/{len(dois)} successful")
    
    # Show post-download recommendations
    print("\n=== Post-Download Recommendations ===")
    if success_count < len(dois):
        print("Some downloads failed. Consider:")
        print("  - Adding institutional authentication (OpenAthens)")
        print("  - Using ZenRows API for anti-bot bypass")
        print("  - Checking if papers are open access")
        print("  - Trying again with different options")


if __name__ == "__main__":
    asyncio.run(main())