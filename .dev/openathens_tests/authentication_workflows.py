#!/usr/bin/env python3
"""
Comprehensive guide to OpenAthens authentication workflows in SciTeX Scholar.
"""

import os
import sys
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.scitex.scholar import Scholar


def show_authentication_workflows():
    """Demonstrate all authentication workflows."""
    
    print("📚 SciTeX Scholar - OpenAthens Authentication Workflows")
    print("=" * 70)
    
    print("\n🔐 METHOD 1: Manual Authentication Check")
    print("-" * 40)
    print("""
# Traditional approach - manual check and authenticate
scholar = Scholar(openathens_enabled=True)

if not scholar.is_openathens_authenticated():
    print("Please authenticate...")
    success = scholar.authenticate_openathens()
    if not success:
        print("Authentication failed!")
        exit(1)

# Now download
papers = scholar.search("quantum computing")
scholar.download_pdfs(papers)
""")
    
    print("\n🚀 METHOD 2: Auto-Authentication in Downloads")
    print("-" * 40)
    print("""
# Let download_pdfs handle authentication automatically
scholar = Scholar(openathens_enabled=True)
papers = scholar.search("quantum computing")

# This will prompt user and open browser if needed
scholar.download_pdfs(papers)  # Default: prompts before auth

# Or auto-open browser without prompting
scholar.download_pdfs(papers, auto_authenticate=True)
""")
    
    print("\n✨ METHOD 3: Ensure Authenticated (Recommended)")
    print("-" * 40)
    print("""
# Most convenient - ensure authenticated before operations
scholar = Scholar(openathens_enabled=True)

# This opens browser automatically if not authenticated
if scholar.ensure_authenticated():
    papers = scholar.search("machine learning")
    scholar.download_pdfs(papers, verify_auth_live=False)
else:
    print("Could not authenticate")
""")
    
    print("\n⚡ METHOD 4: Performance Optimized Batch")
    print("-" * 40)
    print("""
# For downloading many papers efficiently
scholar = Scholar(openathens_enabled=True)

# Authenticate once at the start
scholar.ensure_authenticated()

# Search for many papers
all_papers = scholar.search("deep learning", limit=100)

# Download in batches with fast auth checks
batch_size = 10
for i in range(0, len(all_papers), batch_size):
    batch = all_papers[i:i+batch_size]
    scholar.download_pdfs(
        batch,
        verify_auth_live=False,  # Skip live check after first auth
        show_progress=True
    )
""")
    
    print("\n🤖 METHOD 5: Non-Interactive Scripts")
    print("-" * 40)
    print("""
# For automated scripts and notebooks
scholar = Scholar(openathens_enabled=True)

# Auto-authenticate without any prompts
papers = scholar.search("nature reviews")
result = scholar.download_pdfs(
    papers,
    auto_authenticate=True,  # Auto-open browser
    verify_auth_live=True    # Verify session is valid
)

# Check results
if result['successful'] == 0:
    print(f"All downloads failed: {result.get('error', 'Unknown error')}")
""")
    
    print("\n📊 Authentication Check Options")
    print("-" * 40)
    print("""
# Different ways to check authentication status:

# 1. Quick check (just cookies) - fastest
is_auth = scholar.is_openathens_authenticated()  

# 2. Live verification - most reliable
is_auth = scholar._run_async(
    scholar._pdf_downloader.openathens_authenticator.is_authenticated(
        verify_live=True
    )
)

# 3. Detailed verification with reason
is_auth, details = scholar._run_async(
    scholar._pdf_downloader.openathens_authenticator.verify_authentication()
)
print(f"Authenticated: {is_auth}")
print(f"Details: {details}")
""")
    
    print("\n🛡️ Best Practices")
    print("-" * 40)
    print("""
1. Interactive Use:
   - Use ensure_authenticated() at start of session
   - Let download_pdfs() handle re-authentication

2. Scripts/Automation:
   - Authenticate once at script start
   - Use verify_auth_live=False for subsequent operations
   - Handle authentication failures gracefully

3. Notebooks:
   - Use auto_authenticate=True for seamless experience
   - Check results for authentication errors

4. Large Batches:
   - Authenticate before starting
   - Process in smaller batches
   - Use fast auth checks after initial verification

5. Error Handling:
   - Always check return values
   - Look for 'error' key in results
   - Provide clear feedback to users
""")


def demo_authentication_flow():
    """Live demo of authentication flow."""
    
    print("\n\n🎯 Live Authentication Demo")
    print("=" * 70)
    
    # Check if OpenAthens is configured
    email = os.getenv("SCITEX_SCHOLAR_OPENATHENS_EMAIL")
    if not email:
        print("⚠️  OpenAthens not configured!")
        print("\nTo configure:")
        print("1. Set environment variable:")
        print("   export SCITEX_SCHOLAR_OPENATHENS_EMAIL='your.email@institution.edu'")
        print("\n2. Or configure in code:")
        print("   scholar.configure_openathens('your.email@institution.edu')")
        return
    
    print(f"✓ OpenAthens email: {email}")
    
    # Initialize Scholar
    scholar = Scholar(openathens_enabled=True)
    
    # Show current status
    print("\n📊 Current Status:")
    try:
        # Quick check
        quick_auth = scholar.is_openathens_authenticated()
        print(f"   Quick check: {'✅ Authenticated' if quick_auth else '❌ Not authenticated'}")
        
        # Live check (if cookies exist)
        if quick_auth:
            print("   Performing live verification...")
            live_auth = scholar._run_async(
                scholar._pdf_downloader.openathens_authenticator.is_authenticated(verify_live=True)
            )
            print(f"   Live check: {'✅ Session valid' if live_auth else '❌ Session expired'}")
            
    except Exception as e:
        print(f"   Status check error: {e}")
    
    print("\n💡 Demo complete! Use the examples above in your code.")


if __name__ == "__main__":
    # Show all workflows
    show_authentication_workflows()
    
    # Run demo
    demo_authentication_flow()
    
    print("\n✅ Guide complete! Happy researching! 📚")