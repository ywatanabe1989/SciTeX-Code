#!/usr/bin/env python3
"""Working test for OpenAthens authentication and PDF download."""

import os
from pathlib import Path

# Add parent directories to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Enable debug mode to see browser
os.environ["SCITEX_SCHOLAR_DEBUG_MODE"] = "true"

from src.scitex.scholar import Scholar

def test_openathens():
    """Test OpenAthens with real DOIs."""
    
    print("🔬 OpenAthens Authentication and Download Test")
    print("=" * 60)
    
    # Check email is set
    email = os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    if not email:
        print("❌ Please set SCITEX_SCHOLAR_OPENATHENS_EMAIL environment variable")
        print("   export SCITEX_SCHOLAR_OPENATHENS_EMAIL='your.email@university.edu'")
        return
    
    print(f"📧 Using email: {email}")
    
    # Initialize Scholar with OpenAthens
    scholar = Scholar(
        openathens_enabled=True,
        openathens_email=email,
        enable_auto_download=True,
        acknowledge_scihub_ethical_usage=True,  # Allow fallback
        pdf_dir=".dev/openathens_tests/pdfs"
    )
    
    # Check if already authenticated
    print("\n🔐 Checking authentication status...")
    is_auth = scholar.is_openathens_authenticated()
    print(f"   Status: {'✅ Authenticated' if is_auth else '❌ Not authenticated'}")
    
    if not is_auth:
        print("\n🔑 Starting authentication...")
        print("   📱 Browser will open - please login with 2FA")
        
        try:
            success = scholar.authenticate_openathens(force=True)
            if success:
                print("   ✅ Authentication successful!")
            else:
                print("   ❌ Authentication failed")
                return
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return
    
    # Test with some DOIs
    test_dois = [
        "10.1097/WCO.0000000000001260",  # Wolters Kluwer
        "10.1016/j.yebeh.2024.109736",    # Elsevier
        "10.1038/s41586-019-1666-5",      # Nature
    ]
    
    print(f"\n📚 Testing {len(test_dois)} papers...")
    
    for i, doi in enumerate(test_dois, 1):
        print(f"\n[{i}/{len(test_dois)}] DOI: {doi}")
        
        try:
            # Search for the paper
            papers = scholar.search(doi, limit=1)
            
            if not papers:
                print("   ❌ Paper not found")
                continue
            
            paper = papers[0]
            print(f"   📄 {paper.title[:60]}...")
            
            # Check if already downloaded
            if paper.pdf_path and Path(paper.pdf_path).exists():
                print(f"   ✅ Already have PDF: {paper.pdf_path}")
                continue
            
            # Download PDF
            print("   ⬇️  Downloading...")
            success = paper.download_pdf()
            
            if success:
                print(f"   ✅ Downloaded: {paper.pdf_path}")
                # Check method
                papers_df = papers.to_dataframe()
                method = papers_df.iloc[0]['pdf_source']
                print(f"   🔧 Method: {method}")
            else:
                print("   ❌ Download failed")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Summary:")
    
    pdf_dir = Path(".dev/openathens_tests/pdfs")
    if pdf_dir.exists():
        pdfs = list(pdf_dir.glob("*.pdf"))
        print(f"   Downloaded PDFs: {len(pdfs)}")
        for pdf in pdfs:
            print(f"   - {pdf.name}")

if __name__ == "__main__":
    test_openathens()