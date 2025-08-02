#!/usr/bin/env python3
"""
Debug script to find where the second BrowserManager is created
"""

import asyncio
import sys
import os

sys.path.insert(0, 'src')

async def debug_browser_manager_creation():
    """Debug where multiple BrowserManagers are created."""
    print('🔍 DEBUGGING BROWSER MANAGER CREATION')
    print('='*50)
    
    # Set environment variables
    os.environ["SCITEX_SCHOLAR_OPENURL_RESOLVER_URL"] = "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41"
    
    # Remove ZenRows to ensure local browser
    if "SCITEX_SCHOLAR_ZENROWS_API_KEY" in os.environ:
        del os.environ["SCITEX_SCHOLAR_ZENROWS_API_KEY"]
    
    # Step 1: Create OpenURL resolver with invisible settings
    print('\n📋 Step 1: Creating OpenURL Resolver')
    from scitex.scholar.open_url._OpenURLResolver import OpenURLResolver
    from scitex.scholar.auth._AuthenticationManager import AuthenticationManager
    
    auth_manager = AuthenticationManager()
    print('✅ AuthenticationManager created')
    
    openurl_resolver = OpenURLResolver(
        auth_manager,
        invisible=True,
        viewport_size=(1, 1),
        capture_screenshots=True
    )
    print('✅ OpenURLResolver created')
    
    # Step 2: Try calling resolve (this is where the second BrowserManager appears)
    print('\n📋 Step 2: Calling resolve() method')
    try:
        doi = "10.1254/jpssuppl.92.0_jkl-06"
        print(f'🔗 Calling resolve("{doi}")')
        
        # This is where the second BrowserManager gets created
        resolved_url = openurl_resolver.resolve(doi)
        print(f'✅ Resolved: {resolved_url}')
        
    except Exception as e:
        print(f'❌ Error during resolve: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_browser_manager_creation())