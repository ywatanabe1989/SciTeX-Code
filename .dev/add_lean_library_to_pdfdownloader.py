#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-01-25 03:10:00 (ywatanabe)"
# File: ./.dev/add_lean_library_to_pdfdownloader.py
# ----------------------------------------

"""
Patch to add Lean Library support to PDFDownloader.

This shows the changes needed to integrate Lean Library into the Scholar module.
"""

# Here are the key changes needed in _PDFDownloader.py:

# 1. Add to __init__ parameters:
"""
def __init__(
    self,
    download_dir: Optional[Path] = None,
    use_translators: bool = True,
    use_scihub: bool = True,
    use_playwright: bool = True,
    use_openathens: bool = False,
    use_lean_library: bool = True,  # NEW: Enable by default
    openathens_config: Optional[Dict[str, Any]] = None,
    lean_library_config: Optional[Dict[str, Any]] = None,  # NEW
    ...
):
"""

# 2. Add initialization after OpenAthens (around line 170):
"""
# Initialize Lean Library authenticator
self.lean_library_authenticator = None
self.use_lean_library = use_lean_library

if use_lean_library:
    try:
        from ._LeanLibraryAuthenticator import LeanLibraryAuthenticator
        self.lean_library_authenticator = LeanLibraryAuthenticator(
            config=lean_library_config
        )
        # Check if it's actually available
        if not asyncio.run(self.lean_library_authenticator.is_available_async()):
            logger.warning("Lean Library not available (no browser profile found)")
            self.lean_library_authenticator = None
            self.use_lean_library = False
    except Exception as e:
        logger.warning(f"Failed to initialize Lean Library: {e}")
        self.lean_library_authenticator = None
        self.use_lean_library = False
"""

# 3. Add to _should_use_strategy method (around line 411):
"""
def _should_use_strategy(self, strategy: str) -> bool:
    if strategy == "Lean Library":
        return (
            self.use_lean_library
            and self.lean_library_authenticator is not None
        )
    elif strategy == "OpenAthens":
        ...
"""

# 4. Add new strategy method (after _try_openathens_async):
"""
async def _try_lean_library_async(
    self, doi: str, url: str, output_path: Path, auth_session: Optional[Dict[str, Any]] = None
) -> Optional[Path]:
    '''Try download using Lean Library browser extension.'''
    if not self.lean_library_authenticator:
        return None
        
    try:
        logger.info(f"Using Lean Library for {url}")
        result = await self.lean_library_authenticator.download_with_extension_async(
            url=url,
            output_path=output_path
        )
        return result
    except Exception as e:
        logger.error(f"Lean Library download failed: {e}")
        return None
"""

# 5. Update download strategies (around line 323):
"""
# Determine strategy order based on available authentication
if self.use_lean_library and self.lean_library_authenticator:
    # Lean Library first - it's the most seamless
    strategies = [
        ("Lean Library", self._try_lean_library_async),
        ("Direct patterns", self._try_direct_patterns_async),  
        ("OpenAthens", self._try_openathens_async),  # Fallback to OpenAthens
        ("Sci-Hub", self._try_scihub_async),  # Last resort
    ]
elif auth_session and self.use_openathens and self.openathens_authenticator:
    strategies = [
        ("OpenAthens", self._try_openathens_async),
        ("Direct patterns", self._try_direct_patterns_async),
        ("Sci-Hub", self._try_scihub_async),
    ]
else:
    strategies = [
        ("Zotero translators", self._try_zotero_translator_async),
        ("Direct patterns", self._try_direct_patterns_async),
        ("Playwright", self._try_playwright_async),
        ("Sci-Hub", self._try_scihub_async),
    ]
"""

# 6. Update _get_authenticated_session_async to check Lean Library:
"""
async def _get_authenticated_session_async(self) -> Optional[Dict[str, Any]]:
    '''Get authenticated session from available providers.'''
    
    # Check Lean Library first (it's automatic, no session needed)
    if self.use_lean_library and self.lean_library_authenticator:
        if await self.lean_library_authenticator.is_available_async():
            return {
                'context': {
                    'provider': 'Lean Library',
                    'type': 'browser_extension'
                },
                'cookies': None,  # Lean Library handles auth internally
            }
    
    # Then check OpenAthens
    if self.use_openathens and self.openathens_authenticator:
        ...
"""

print("Patch description created!")
print("\nTo implement:")
print("1. Add these changes to src/scitex/scholar/_PDFDownloader.py")
print("2. Update ScholarConfig to include use_lean_library option")
print("3. Update Scholar class to pass lean_library config to PDFDownloader")
print("4. Add documentation about installing and using Lean Library")

# Example usage after implementation:
example_code = '''
# After implementation, usage would be:
from scitex.scholar import Scholar

# Lean Library will be used automatically if available
scholar = Scholar(use_lean_library=True)  # Default

# Download papers - Lean Library will be tried first
papers = scholar.search("quantum computing")
scholar.download_pdfs(papers)

# The download order will be:
# 1. Lean Library (if browser extension installed)
# 2. Direct patterns
# 3. OpenAthens (if configured)  
# 4. Sci-Hub (if acknowledged)
'''

print("\nExample usage:")
print(example_code)