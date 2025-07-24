#!/usr/bin/env python3
"""Diagnose current OpenAthens issues."""

import os
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Set up environment
os.environ["SCITEX_SCHOLAR_DEBUG_MODE"] = "false"  # Headless for quick test
os.environ["SCITEX_SCHOLAR_OPENATHENS_EMAIL"] = "test@example.com"

try:
    from src.scitex.scholar import Scholar, ScholarConfig
    print("✅ Scholar import successful")
    
    # Try creating instance with config
    config = ScholarConfig(openathens_enabled=False)
    scholar = Scholar(config=config)
    print("✅ Scholar instance created")
    
    # Test basic search
    papers = scholar.search("test", limit=1)
    print(f"✅ Search works: {len(papers)} papers found")
    
    # Test if OpenAthens components exist
    from src.scitex.scholar._OpenAthensAuthenticator import OpenAthensAuthenticator
    print("✅ OpenAthensAuthenticator exists")
    
    from src.scitex.scholar._BrowserBasedDownloader import BrowserBasedDownloader
    print("✅ BrowserBasedDownloader exists")
    
    from src.scitex.scholar._MinimalOpenAthensAuthenticator import MinimalOpenAthensAuthenticator
    print("✅ MinimalOpenAthensAuthenticator exists")
    
    # Check if PDFDownloader properly integrates authentication
    from src.scitex.scholar._PDFDownloader import PDFDownloader
    print("✅ PDFDownloader exists")
    
    # Check URL transformer
    from src.scitex.scholar._OpenAthensURLTransformer import OpenAthensURLTransformer
    transformer = OpenAthensURLTransformer()
    
    # Test URL transformation
    test_urls = [
        "https://doi.org/10.1038/s41586-021-03819-2",
        "https://www.nature.com/articles/s41586-021-03819-2",
        "https://journals.lww.com/test"
    ]
    
    print("\n📝 URL Transformation Test:")
    for url in test_urls:
        needs = transformer.needs_transformation(url)
        print(f"   {url}: {'✅ Needs transform' if needs else '❌ No transform needed'}")
        if needs:
            transformed = transformer.transform_url_for_openathens(url)
            print(f"      → {transformed}")
    
    print("\n✅ All components are available")
    print("\n❓ What specific issue are you experiencing?")
    print("   1. Authentication fails?")
    print("   2. Downloads fail after authentication?")
    print("   3. Browser closes prematurely?")
    print("   4. Page unresponsive during login?")
    print("   5. Other issue?")
    
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()