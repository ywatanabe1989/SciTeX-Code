#!/usr/bin/env python3
"""
Complete OpenAthens Authentication and Download Example

This example shows the proper way to use OpenAthens with SciTeX Scholar:
1. One-time authentication with 2FA
2. Session persistence for subsequent runs
3. PDF downloads using authenticated session

Run this script with:
    python openathens_complete_example.py

Environment setup:
    export SCITEX_SCHOLAR_OPENATHENS_EMAIL="your.email@university.edu"
    export SCITEX_SCHOLAR_DEBUG_MODE=true  # Optional, to see browser
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from scitex.scholar import Scholar


def main():
    """Complete OpenAthens workflow example."""
    
    print("🔬 SciTeX Scholar - OpenAthens Authentication Example")
    print("=" * 70)
    
    # Check environment
    email = os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    if not email:
        print("\n❌ Error: Please set your institutional email:")
        print("   export SCITEX_SCHOLAR_OPENATHENS_EMAIL='your.email@university.edu'")
        return
    
    print(f"\n📧 Using email: {email}")
    
    # Initialize Scholar with OpenAthens
    print("\n📚 Initializing Scholar with OpenAthens...")
    scholar = Scholar(
        openathens_enabled=True,
        openathens_email=email,
        enable_auto_download=True,
        acknowledge_scihub_ethical_usage=True,  # Allow fallback if needed
        pdf_dir="./openathens_pdfs"
    )
    
    # Check authentication status
    print("\n🔐 Checking authentication status...")
    is_authenticated = scholar.is_openathens_authenticated()
    
    if is_authenticated:
        print("   ✅ Already authenticated! Using existing session.")
    else:
        print("   ❌ Not authenticated. Starting authentication process...")
        print("\n⚠️  IMPORTANT: Manual authentication required!")
        print("   1. A browser window will open")
        print("   2. Select your institution")
        print("   3. Complete login with your credentials")
        print("   4. Complete 2FA if required")
        print("   5. Wait for 'Login successful' message\n")
        
        input("Press Enter to start authentication...")
        
        try:
            success = scholar.authenticate_openathens(force=True)
            if success:
                print("\n✅ Authentication successful! Session saved.")
            else:
                print("\n❌ Authentication failed.")
                return
        except Exception as e:
            print(f"\n❌ Authentication error: {e}")
            return
    
    # Test downloading papers
    print("\n📥 Testing PDF downloads...")
    
    # High-impact papers that typically require authentication
    test_papers = [
        {
            "doi": "10.1038/s41586-019-1666-5",
            "title": "Quantum supremacy using a programmable superconducting processor",
            "journal": "Nature"
        },
        {
            "doi": "10.1016/S0140-6736(20)30183-5",
            "title": "Clinical features of patients infected with 2019 novel coronavirus",
            "journal": "The Lancet"
        },
        {
            "doi": "10.1126/science.abb2507",
            "title": "Structure of the SARS-CoV-2 spike receptor-binding domain",
            "journal": "Science"
        }
    ]
    
    results = []
    
    for i, paper_info in enumerate(test_papers, 1):
        doi = paper_info["doi"]
        print(f"\n[{i}/{len(test_papers)}] Searching for: {doi}")
        print(f"     Expected: {paper_info['title'][:50]}...")
        print(f"     Journal: {paper_info['journal']}")
        
        try:
            # Search for the paper
            papers = scholar.search(doi, limit=1)
            
            if not papers:
                print("     ❌ Paper not found")
                results.append({"doi": doi, "status": "not_found"})
                continue
            
            paper = papers[0]
            print(f"     ✓ Found: {paper.title[:50]}...")
            
            # Check if already downloaded
            if paper.pdf_path and Path(paper.pdf_path).exists():
                print(f"     ✓ Already have PDF: {paper.pdf_path}")
                results.append({"doi": doi, "status": "exists", "path": paper.pdf_path})
                continue
            
            # Download PDF
            print("     ⬇️  Downloading PDF...")
            success = paper.download_pdf()
            
            if success and paper.pdf_path:
                print(f"     ✅ Downloaded successfully!")
                print(f"     📄 Saved to: {paper.pdf_path}")
                
                # Check which method was used
                df = papers.to_dataframe()
                method = df.iloc[0].get('pdf_source', 'Unknown')
                print(f"     🔧 Download method: {method}")
                
                results.append({
                    "doi": doi, 
                    "status": "downloaded", 
                    "path": paper.pdf_path,
                    "method": method
                })
            else:
                print("     ❌ Download failed")
                results.append({"doi": doi, "status": "failed"})
                
        except Exception as e:
            print(f"     ❌ Error: {str(e)[:100]}")
            results.append({"doi": doi, "status": "error", "error": str(e)})
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Download Summary:")
    
    successful = sum(1 for r in results if r["status"] in ["downloaded", "exists"])
    print(f"\n   Total papers: {len(test_papers)}")
    print(f"   Successful: {successful}")
    print(f"   Failed: {len(test_papers) - successful}")
    
    # Show download methods used
    methods = {}
    for r in results:
        if "method" in r:
            methods[r["method"]] = methods.get(r["method"], 0) + 1
    
    if methods:
        print("\n   Download methods used:")
        for method, count in methods.items():
            print(f"   - {method}: {count}")
    
    # List downloaded files
    pdf_dir = Path("./openathens_pdfs")
    if pdf_dir.exists():
        pdfs = list(pdf_dir.glob("*.pdf"))
        if pdfs:
            print(f"\n   📁 Downloaded PDFs in {pdf_dir}:")
            for pdf in pdfs[:5]:  # Show first 5
                size_kb = pdf.stat().st_size / 1024
                print(f"   - {pdf.name} ({size_kb:.1f} KB)")
            if len(pdfs) > 5:
                print(f"   ... and {len(pdfs) - 5} more")
    
    # Authentication tips
    print("\n💡 Tips:")
    print("   • OpenAthens sessions expire after ~8 hours")
    print("   • Re-run this script to re-authenticate when needed")
    print("   • Sessions are encrypted and stored locally")
    print("   • Check ~/.scitex/scholar/openathens_sessions/ for session files")
    
    if not is_authenticated:
        print("\n⚠️  Note: This was your first authentication.")
        print("   Next time you run this script, it will use the saved session!")


if __name__ == "__main__":
    main()