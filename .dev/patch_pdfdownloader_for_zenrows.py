#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2025-07-30 21:45:00
# Author: ywatanabe
# File: /home/ywatanabe/proj/SciTeX-Code/.dev/patch_pdfdownloader_for_zenrows.py
# ----------------------------------------
"""Patch to update PDFDownloader to use ZenRows-enhanced OpenURL resolver.

This patch modifies the PDFDownloader initialization to use the
OpenURLResolverWithZenRows when ZenRows is configured.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def create_patch():
    """Create the patch for PDFDownloader."""
    
    patch_content = '''--- a/src/scitex/scholar/download/_PDFDownloader.py
+++ b/src/scitex/scholar/download/_PDFDownloader.py
@@ -41,7 +41,8 @@ from ..utils._formatters import normalize_filename
 from ._ZoteroTranslatorRunner import ZoteroTranslatorRunner
 from ..auth._LeanLibraryAuthentication import LeanLibraryAuthenticator
-from ..core._OpenURLResolver import OpenURLResolver
+from ..open_url._OpenURLResolver import OpenURLResolver
+from ..open_url._OpenURLResolverWithZenRows import OpenURLResolverWithZenRows
 from ..core._ResolverLinkFinder import ResolverLinkFinder, find_and_click_resolver_link
 # BrowserAutomation removed - using direct playwright calls
 # OpenAthensURLTransformer removed - not needed for basic functionality
@@ -91,6 +92,8 @@ class PDFDownloader:
         use_lean_library: bool = True,
         openurl_resolver: Optional[str] = None,
+        zenrows_api_key: Optional[str] = None,
+        use_zenrows: bool = False,
         timeout: int = 30,
         max_retries: int = 3,
         max_concurrent: int = 3,
@@ -108,6 +111,8 @@ class PDFDownloader:
             openathens_config: OpenAthens configuration dict
             use_lean_library: Enable Lean Library browser extension
             openurl_resolver: OpenURL resolver URL (e.g., University of Melbourne)
+            zenrows_api_key: ZenRows API key for anti-bot bypass
+            use_zenrows: Enable ZenRows for OpenURL resolution
             timeout: Download timeout in seconds
             max_retries: Maximum retry attempts
             max_concurrent: Maximum concurrent downloads
@@ -197,10 +202,25 @@ class PDFDownloader:
         # Initialize OpenURL resolver
         self.openurl_resolver = None
         if openurl_resolver:
             try:
-                self.openurl_resolver = OpenURLResolver(openurl_resolver)
-                logger.info(f"OpenURL resolver initialized: {openurl_resolver}")
+                # Use ZenRows-enhanced resolver if configured
+                if use_zenrows and zenrows_api_key:
+                    from ..auth import AuthenticationManager
+                    auth_manager = AuthenticationManager()
+                    
+                    self.openurl_resolver = OpenURLResolverWithZenRows(
+                        auth_manager=auth_manager,
+                        resolver_url=openurl_resolver,
+                        zenrows_api_key=zenrows_api_key,
+                        use_zenrows=True
+                    )
+                    logger.info(f"OpenURL resolver initialized with ZenRows: {openurl_resolver}")
+                else:
+                    # Standard resolver without ZenRows
+                    self.openurl_resolver = OpenURLResolver(openurl_resolver)
+                    logger.info(f"OpenURL resolver initialized: {openurl_resolver}")
             except Exception as e:
                 logger.warning(f"Could not initialize OpenURL resolver: {e}")
+                self.openurl_resolver = None
 
         # Track downloads to avoid duplicates
         self._active_downloads: Set[str] = set()
'''
    
    return patch_content


def show_usage_example():
    """Show how to use the updated PDFDownloader."""
    
    example = '''
# Example usage with ZenRows-enhanced PDFDownloader

import os
from pathlib import Path
from scitex.scholar.download._PDFDownloader import PDFDownloader
from scitex.scholar._Paper import Paper

# Initialize downloader with ZenRows
downloader = PDFDownloader(
    download_dir=Path("./pdfs"),
    use_translators=True,
    use_scihub=True,
    use_playwright=True,
    use_openathens=True,
    openathens_config={
        "email": os.environ.get("OPENATHENS_EMAIL"),
        "username": os.environ.get("OPENATHENS_USERNAME"),
        "password": os.environ.get("OPENATHENS_PASSWORD"),
        "org_id": os.environ.get("OPENATHENS_ORG_ID")
    },
    openurl_resolver="https://unimelb.hosted.exlibrisgroup.com/sfxlcl41",
    zenrows_api_key=os.environ.get("ZENROWS_API_KEY"),
    use_zenrows=True,  # Enable ZenRows
    max_concurrent=3,
    debug_mode=True
)

# Download a paper
paper = Paper(
    doi="10.1038/nature12373",
    title="A mesoscale connectome of the mouse brain",
    journal="Nature",
    year=2014
)

# The downloader will now:
# 1. Try direct publisher patterns
# 2. Use OpenURL resolver with ZenRows for anti-bot bypass
# 3. Fall back to other methods if needed

pdf_path = await downloader.download_pdf_async(
    identifier=paper.doi,
    metadata={
        "title": paper.title,
        "authors": paper.authors,
        "year": paper.year
    }
)

if pdf_path:
    print(f"✅ Downloaded to: {pdf_path}")
else:
    print("❌ Download failed")
'''
    
    return example


def main():
    """Main function to display patch information."""
    
    print("PDFDownloader ZenRows Integration Patch")
    print("=" * 50)
    
    print("\n1. PATCH CONTENT:")
    print("-" * 30)
    print(create_patch())
    
    print("\n2. MANUAL UPDATE INSTRUCTIONS:")
    print("-" * 30)
    print("Edit: src/scitex/scholar/download/_PDFDownloader.py")
    print("\nAdd to imports (line ~44):")
    print("from ..open_url._OpenURLResolverWithZenRows import OpenURLResolverWithZenRows")
    
    print("\nAdd to __init__ parameters (after openurl_resolver):")
    print("    zenrows_api_key: Optional[str] = None,")
    print("    use_zenrows: bool = False,")
    
    print("\nReplace OpenURL resolver initialization (lines 197-205) with:")
    print("""
        # Initialize OpenURL resolver
        self.openurl_resolver = None
        if openurl_resolver:
            try:
                # Use ZenRows-enhanced resolver if configured
                if use_zenrows and zenrows_api_key:
                    from ..auth import AuthenticationManager
                    auth_manager = AuthenticationManager()
                    
                    self.openurl_resolver = OpenURLResolverWithZenRows(
                        auth_manager=auth_manager,
                        resolver_url=openurl_resolver,
                        zenrows_api_key=zenrows_api_key,
                        use_zenrows=True
                    )
                    logger.info(f"OpenURL resolver initialized with ZenRows: {openurl_resolver}")
                else:
                    # Standard resolver without ZenRows
                    self.openurl_resolver = OpenURLResolver(openurl_resolver)
                    logger.info(f"OpenURL resolver initialized: {openurl_resolver}")
            except Exception as e:
                logger.warning(f"Could not initialize OpenURL resolver: {e}")
                self.openurl_resolver = None
""")
    
    print("\n3. USAGE EXAMPLE:")
    print("-" * 30)
    print(show_usage_example())
    
    print("\n4. ENVIRONMENT VARIABLES NEEDED:")
    print("-" * 30)
    print("export ZENROWS_API_KEY='your-api-key'")
    print("export OPENATHENS_USERNAME='your-username'")
    print("export OPENATHENS_PASSWORD='your-password'")
    print("export OPENATHENS_ORG_ID='your-org-id'")
    
    print("\n5. TESTING:")
    print("-" * 30)
    print("After applying the patch, test with:")
    print("python .dev/test_zenrows_cookie_transfer_real.py")


if __name__ == "__main__":
    main()