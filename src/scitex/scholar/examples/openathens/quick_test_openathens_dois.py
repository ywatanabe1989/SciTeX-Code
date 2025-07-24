#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Quick test of specific paywalled DOIs
# ----------------------------------------

"""
Quick test script to check OpenAthens authentication with specific DOIs.
Run with: python quick_test_openathens_dois.py
"""

import asyncio
from pathlib import Path
from scitex.scholar import Scholar

# High-impact paywalled papers that definitely need authentication
TEST_DOIS = [
    # Nature - Quantum computing milestone
    "10.1038/s41586-019-1666-5",
    
    # Science - COVID-19 spike protein structure  
    "10.1126/science.abj8754",
    
    # Cell - Early COVID-19 paper
    "10.1016/j.cell.2020.02.052",
    
    # Annual Reviews - Neuroscience
    "10.1146/annurev-neuro-111020-103314",
    
    # The Lancet - Major clinical paper
    "10.1016/S0140-6736(20)30183-5"
]


async def quick_test():
    """Quick test of OpenAthens with specific DOIs."""
    
    print("=== Quick OpenAthens DOI Test ===\n")
    
    # Enable OpenAthens before creating Scholar
    import os
    os.environ["SCITEX_SCHOLAR_OPENATHENS_ENABLED"] = "true"
    
    # Initialize Scholar with OpenAthens enabled
    scholar = Scholar()
    
    email = scholar.config.openathens_email
    if not email:
        print("Please set your email first:")
        print("export SCITEX_SCHOLAR_OPENATHENS_EMAIL='your.email@institution.edu'\n")
        return
    
    print(f"Using email: {email}")
    
    # Authenticate
    print("\nAuthenticating with OpenAthens...")
    try:
        success = await scholar.authenticate_openathens()
        if not success:
            print("❌ Authentication failed!")
            return
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    print("✅ Authenticated!\n")
    
    # Test downloads
    output_dir = Path("openathens_test_pdfs")
    output_dir.mkdir(exist_ok=True)
    
    print(f"Testing {len(TEST_DOIS)} paywalled papers...\n")
    
    for i, doi in enumerate(TEST_DOIS, 1):
        print(f"[{i}/{len(TEST_DOIS)}] DOI: {doi}")
        
        try:
            pdf_path = await scholar.download_pdf_async(doi, output_dir=output_dir)
            
            if pdf_path and pdf_path.exists():
                size = pdf_path.stat().st_size
                print(f"    ✅ Success! ({size:,} bytes)")
            else:
                print(f"    ❌ Failed - no file")
                
        except Exception as e:
            print(f"    ❌ Error: {str(e)[:80]}")
        
        print()
    
    # Check results
    pdfs = list(output_dir.glob("*.pdf"))
    print(f"\n📊 Results: {len(pdfs)}/{len(TEST_DOIS)} PDFs downloaded")
    print(f"📁 Files in: {output_dir.absolute()}")
    
    if pdfs:
        print("\nDownloaded files:")
        for pdf in pdfs:
            print(f"  - {pdf.name} ({pdf.stat().st_size:,} bytes)")


if __name__ == "__main__":
    asyncio.run(quick_test())