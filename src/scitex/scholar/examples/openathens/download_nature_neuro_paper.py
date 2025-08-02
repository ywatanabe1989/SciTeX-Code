#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Download Nature Neuroscience paper directly
# ----------------------------------------

"""
Direct download of the Nature Neuroscience paper using OpenAthens.
"""

import asyncio
import os
from pathlib import Path

os.environ["SCITEX_SCHOLAR_OPENATHENS_ENABLED"] = "true"

from scitex.scholar._OpenAthensAuthenticator import OpenAthensAuthenticator


async def download_paper():
    """Download the specific paper."""
    
    print("=== Downloading Nature Neuroscience Paper ===\n")
    
    doi = "10.1038/s41593-025-01990-7"
    title = "Addressing artifactual bias in large, automated MRI analyses of brain development"
    
    print(f"Title: {title}")
    print(f"DOI: {doi}")
    print(f"Journal: Nature Neuroscience\n")
    
    # Create authenticator
    auth = OpenAthensAuthenticator(email="Yusuke.Watanabe@unimelb.edu.au")
    await auth.initialize()
    
    # Check if authenticated
    if await auth.is_authenticated_async():
        print("✅ Using saved OpenAthens session\n")
    else:
        print("❌ No valid session - would need to authenticate\n")
        return
    
    # Try different URL formats
    urls_to_try = [
        f"https://www.nature.com/articles/{doi.split('/')[-1]}.pdf",
        f"https://www.nature.com/articles/{doi.split('/')[-1]}",
        f"https://doi.org/{doi}"
    ]
    
    output_dir = Path("nature_neuro_paper")
    output_dir.mkdir(exist_ok=True)
    
    for i, url in enumerate(urls_to_try, 1):
        print(f"\nAttempt {i}: {url}")
        
        output_path = output_dir / f"nature_neuro_{doi.replace('/', '_')}.pdf"
        
        try:
            result = await auth.download_with_auth_async(url, output_path)
            
            if result and result.exists():
                size = result.stat().st_size
                print(f"✅ Success!")
                print(f"   File: {result}")
                print(f"   Size: {size:,} bytes")
                
                # Verify it's a PDF
                with open(result, 'rb') as f:
                    header = f.read(4)
                    if header == b'%PDF':
                        print("   ✅ Verified as PDF")
                    else:
                        print("   ⚠️  File doesn't appear to be a PDF")
                
                await auth.close()
                return result
            else:
                print("❌ Download failed")
                
        except Exception as e:
            print(f"❌ Error: {str(e)[:200]}")
    
    await auth.close()
    
    print("\n❌ All attempts failed")
    print("\nPossible reasons:")
    print("1. The paper might be very new (2025) and not yet accessible")
    print("2. Your institution might not have access to this specific journal")
    print("3. The paper might require additional authentication steps")
    
    print(f"\nTry accessing directly: https://www.nature.com/articles/{doi.split('/')[-1]}")


if __name__ == "__main__":
    asyncio.run(download_paper())