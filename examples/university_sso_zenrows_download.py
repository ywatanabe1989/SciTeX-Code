#!/usr/bin/env python3
"""
University SSO Login with ZenRows Stealth for PDF Downloads

This example shows the recommended approach for downloading paywalled papers:
1. Local browser window (you can see and interact with it)
2. ZenRows proxy for stealth (clean residential IP)
3. Manual SSO login (handles Okta, 2FA, etc.)
4. Automated PDF downloads after authentication

Perfect for:
- Complex university authentication (OpenAthens, Shibboleth, etc.)
- Multi-factor authentication (Okta Verify, Duo, etc.)
- Sites with heavy anti-bot protection
- Maintaining long authenticated sessions
"""

import asyncio
import os
from pathlib import Path
from typing import List, Optional

from scitex import logging
from scitex.scholar import Scholar
from scitex.scholar.browser._ZenRowsStealthyLocal import ZenRowsStealthyLocal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def university_sso_download_workflow(
    dois: List[str],
    institution_login_url: str,
    output_dir: Path = Path("./downloaded_papers"),
    headless: bool = False,
    save_session: bool = True
):
    """
    Complete workflow for university SSO login and PDF downloads.
    
    Args:
        dois: List of DOIs to download
        institution_login_url: Your university's login page
        output_dir: Where to save PDFs
        headless: Set False to see browser window
        save_session: Save cookies for future use
    """
    
    # Initialize ZenRows stealthy browser
    print("\n🚀 Starting ZenRows stealthy browser...")
    browser = ZenRowsStealthyLocal(
        headless=headless,  # Show browser for login
        use_residential=True,  # Premium residential IPs
        country="us"  # Or your preferred country
    )
    
    try:
        # Get browser context
        context = await browser.new_context()
        page = await context.new_page()
        
        print("\n✅ Browser launched with ZenRows protection:")
        print("  - Residential IP address")
        print("  - Anti-bot detection bypass")
        print("  - Full manual control for login\n")
        
        # Step 1: Verify our stealth setup
        print("🔍 Checking IP address...")
        await page.goto("https://httpbin.org/ip")
        await page.wait_for_timeout(2000)
        ip_info = await page.inner_text("body")
        print(f"Current IP info: {ip_info}\n")
        
        # Step 2: Navigate to institution login
        print(f"🎓 Navigating to institution login: {institution_login_url}")
        await page.goto(institution_login_url)
        
        # Step 3: Manual login
        print("\n" + "="*60)
        print("👨‍💻 MANUAL LOGIN REQUIRED")
        print("="*60)
        print("\nPlease complete your university login in the browser window:")
        print("1. Enter your username/email")
        print("2. Enter your password")
        print("3. Complete any 2FA (Okta Verify, Duo, etc.)")
        print("4. Wait until you see the library/dashboard page")
        print("\nPress Enter when you're fully logged in...")
        input()
        
        print("\n✅ Login completed! Saving session...")
        
        # Step 4: Save cookies for future use
        cookies = await context.cookies()
        if save_session and cookies:
            session_file = output_dir / "university_session.json"
            session_file.parent.mkdir(parents=True, exist_ok=True)
            
            import json
            with open(session_file, 'w') as f:
                json.dump({
                    "cookies": cookies,
                    "institution": institution_login_url,
                    "timestamp": asyncio.get_event_loop().time()
                }, f, indent=2)
            print(f"💾 Session saved to: {session_file}")
            print(f"   ({len(cookies)} cookies saved)\n")
        
        # Step 5: Initialize Scholar with current browser
        print("📚 Initializing Scholar module...")
        scholar = Scholar(
            use_zenrows=True,
            zenrows_use_stealth_browser=True,
            debug_mode=not headless
        )
        
        # Step 6: Download papers
        print(f"\n📥 Downloading {len(dois)} papers...\n")
        
        for i, doi in enumerate(dois, 1):
            print(f"[{i}/{len(dois)}] Processing DOI: {doi}")
            
            try:
                # Navigate to DOI
                doi_url = f"https://doi.org/{doi}"
                await page.goto(doi_url)
                await page.wait_for_timeout(3000)  # Wait for redirects
                
                current_url = page.url
                print(f"   Redirected to: {current_url}")
                
                # Look for PDF download link
                pdf_downloaded = False
                
                # Common PDF link patterns
                pdf_selectors = [
                    'a[href$=".pdf"]',
                    'a:has-text("Download PDF")',
                    'a:has-text("PDF")',
                    'button:has-text("Download")',
                    'a[data-track-action="download pdf"]',  # Nature
                    'a[href*="pdfft"]',  # ScienceDirect
                    'a[href*="epdf"]',   # Wiley
                    'a[class*="pdf-link"]',
                ]
                
                for selector in pdf_selectors:
                    try:
                        pdf_link = await page.wait_for_selector(selector, timeout=5000)
                        if pdf_link:
                            print(f"   Found PDF link: {selector}")
                            
                            # Set up download handling
                            async with page.expect_download() as download_info:
                                await pdf_link.click()
                                download = await download_info.value
                            
                            # Save with descriptive filename
                            filename = f"{doi.replace('/', '_')}.pdf"
                            save_path = output_dir / filename
                            save_path.parent.mkdir(parents=True, exist_ok=True)
                            
                            await download.save_as(save_path)
                            print(f"   ✅ Downloaded to: {save_path}")
                            pdf_downloaded = True
                            break
                            
                    except Exception as e:
                        continue
                
                if not pdf_downloaded:
                    print(f"   ❌ Could not find PDF download link")
                    
                    # Alternative: Use Scholar's download methods
                    print("   Trying Scholar module as fallback...")
                    papers = await scholar.download_pdfs(
                        [doi],
                        output_dir=output_dir,
                        show_progress=False
                    )
                    if papers and papers[0].pdf_path:
                        print(f"   ✅ Scholar downloaded to: {papers[0].pdf_path}")
                    else:
                        print(f"   ❌ Scholar download also failed")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            # Small delay between downloads
            if i < len(dois):
                await asyncio.sleep(2)
        
        print("\n✅ Download process completed!")
        
        # Step 7: Keep browser open for inspection
        if not headless:
            print("\n🔍 Browser will stay open for 30 seconds for inspection...")
            print("You can browse to other papers manually if needed.")
            await asyncio.sleep(30)
        
    except Exception as e:
        logger.error(f"Workflow error: {e}")
        raise
    finally:
        await browser.cleanup()
        print("\n🧹 Browser closed.")


async def load_and_use_saved_session(
    dois: List[str],
    session_file: Path = Path("./downloaded_papers/university_session.json"),
    output_dir: Path = Path("./downloaded_papers")
):
    """
    Load a saved session and download papers without re-login.
    
    Args:
        dois: List of DOIs to download
        session_file: Path to saved session JSON
        output_dir: Where to save PDFs
    """
    import json
    
    if not session_file.exists():
        print(f"❌ Session file not found: {session_file}")
        print("Please run the full workflow first to create a session.")
        return
    
    # Load session
    with open(session_file, 'r') as f:
        session_data = json.load(f)
    
    cookies = session_data.get("cookies", [])
    print(f"✅ Loaded session with {len(cookies)} cookies")
    
    # Check session age
    if "timestamp" in session_data:
        age_hours = (asyncio.get_event_loop().time() - session_data["timestamp"]) / 3600
        if age_hours > 8:
            print(f"⚠️  Session is {age_hours:.1f} hours old, may have expired")
    
    # Initialize Scholar with saved session
    scholar = Scholar(
        use_zenrows=True,
        zenrows_use_stealth_browser=True,
        debug_mode=False  # Headless for batch downloads
    )
    
    # Download papers
    print(f"\n📥 Downloading {len(dois)} papers with saved session...")
    
    papers = await scholar.download_pdfs(
        dois,
        output_dir=output_dir,
        show_progress=True,
        organize_by_year=True
    )
    
    # Summary
    success_count = sum(1 for p in papers if p.pdf_path)
    print(f"\n✅ Downloaded {success_count}/{len(dois)} papers successfully")


# Example DOIs for testing
EXAMPLE_DOIS = [
    "10.1038/s41586-023-06516-4",  # Nature paper
    "10.1126/science.abm0829",      # Science paper
    "10.1016/j.cell.2023.08.040",   # Cell paper
    "10.1073/pnas.2301726120",      # PNAS paper
]


if __name__ == "__main__":
    print("University SSO + ZenRows Stealth PDF Download")
    print("=" * 50)
    print("\nThis demo shows how to:")
    print("1. Use local browser with ZenRows proxy")
    print("2. Complete university SSO login manually")
    print("3. Download paywalled PDFs automatically")
    print("4. Save session for future use\n")
    
    # Get institution login URL from environment or ask
    login_url = os.getenv("UNIVERSITY_LOGIN_URL")
    if not login_url:
        print("Enter your university's login URL")
        print("Examples:")
        print("  - https://login.openathens.net/auth")
        print("  - https://shibboleth.university.edu/idp")
        print("  - https://ezproxy.university.edu/login")
        login_url = input("\nYour login URL: ").strip()
    
    print("\nOptions:")
    print("1. Full workflow (login + download)")
    print("2. Use saved session (skip login)")
    
    choice = input("\nSelect option (1-2): ")
    
    if choice == "1":
        # Full workflow with login
        asyncio.run(university_sso_download_workflow(
            dois=EXAMPLE_DOIS,
            institution_login_url=login_url,
            headless=False  # Show browser for login
        ))
    elif choice == "2":
        # Use saved session
        asyncio.run(load_and_use_saved_session(
            dois=EXAMPLE_DOIS
        ))
    else:
        print("Invalid choice")

# EOF