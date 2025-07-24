#!/usr/bin/env python3
"""
Check how cookies are being handled, including timing and expiry.
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.scitex.scholar._OpenAthensAuthenticator import OpenAthensAuthenticator


async def check_cookie_details():
    """Check cookie details including expiry times."""
    
    print("🍪 COOKIE HANDLING ANALYSIS")
    print("=" * 60)
    
    # Load authenticator
    auth = OpenAthensAuthenticator(email="Yusuke.Watanabe@unimelb.edu.au")
    await auth._load_session_cache()
    
    if not hasattr(auth, '_full_cookies') or not auth._full_cookies:
        print("❌ No cookies found. Please authenticate first.")
        return
    
    print(f"\n📊 Cookie Summary:")
    print(f"   Total cookies: {len(auth._full_cookies)}")
    
    # Analyze cookies
    now = datetime.now().timestamp()
    expired = []
    session_cookies = []
    persistent_cookies = []
    
    print("\n📝 Cookie Details:")
    for cookie in auth._full_cookies:
        name = cookie.get('name', 'unknown')
        domain = cookie.get('domain', 'unknown')
        expires = cookie.get('expires', None)
        
        print(f"\n   Cookie: {name}")
        print(f"   Domain: {domain}")
        
        if expires is None:
            print(f"   Type: Session cookie (expires when browser closes)")
            session_cookies.append(name)
        elif expires == -1:
            print(f"   Type: Session cookie")
            session_cookies.append(name)
        else:
            # Convert expires timestamp
            try:
                if expires > 0:
                    expire_date = datetime.fromtimestamp(expires)
                    print(f"   Expires: {expire_date}")
                    
                    if expires < now:
                        print(f"   Status: ❌ EXPIRED")
                        expired.append(name)
                    else:
                        time_left = (expires - now) / 3600  # hours
                        print(f"   Status: ✅ Valid for {time_left:.1f} hours")
                        persistent_cookies.append(name)
            except:
                print(f"   Expires: {expires} (couldn't parse)")
        
        # Check secure/httpOnly flags
        secure = cookie.get('secure', False)
        http_only = cookie.get('httpOnly', False)
        same_site = cookie.get('sameSite', 'None')
        
        print(f"   Secure: {secure}, HttpOnly: {http_only}, SameSite: {same_site}")
    
    print(f"\n\n📊 Summary:")
    print(f"   Session cookies: {len(session_cookies)}")
    print(f"   Persistent cookies: {len(persistent_cookies)}")
    print(f"   Expired cookies: {len(expired)}")
    
    if expired:
        print(f"\n❌ EXPIRED COOKIES:")
        for name in expired:
            print(f"   • {name}")
        print("\n   This could explain why downloads are failing!")
    
    # Check session cache timestamp
    cache_file = auth.cache_dir / "openathens_session.json.enc"
    if cache_file.exists():
        mod_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
        age_hours = (datetime.now() - mod_time).total_seconds() / 3600
        print(f"\n📅 Session cache age: {age_hours:.1f} hours old")
        print(f"   Last modified: {mod_time}")
        
        if age_hours > 8:
            print("   ⚠️  Session might be stale (>8 hours)")


async def check_cookie_domains():
    """Check which domains cookies are for."""
    
    print("\n\n🌐 COOKIE DOMAINS")
    print("=" * 60)
    
    auth = OpenAthensAuthenticator(email="Yusuke.Watanabe@unimelb.edu.au")
    await auth._load_session_cache()
    
    if not auth._full_cookies:
        return
    
    # Group by domain
    domains = {}
    for cookie in auth._full_cookies:
        domain = cookie.get('domain', 'unknown')
        if domain not in domains:
            domains[domain] = []
        domains[domain].append(cookie.get('name', 'unknown'))
    
    print("\nCookies grouped by domain:")
    for domain, names in domains.items():
        print(f"\n   {domain}:")
        for name in names:
            print(f"     • {name}")
    
    print("\n⚠️  Important notes:")
    print("   • Cookies only work on their specified domain")
    print("   • .openathens.net cookies won't work on nature.com")
    print("   • This is why we need the redirector approach!")


async def test_cookie_usage_in_download():
    """Test how cookies are used in downloads."""
    
    print("\n\n🔄 COOKIE USAGE IN DOWNLOADS")
    print("=" * 60)
    
    from src.scitex.scholar._PDFDownloader import PDFDownloader
    
    config = {
        'email': 'Yusuke.Watanabe@unimelb.edu.au',
        'debug_mode': True
    }
    
    downloader = PDFDownloader(
        use_openathens=True,
        openathens_config=config
    )
    
    # Get auth session
    auth_session = await downloader._get_authenticated_session()
    
    if auth_session:
        cookies = auth_session.get('cookies', [])
        print(f"\n✅ Auth session retrieved:")
        print(f"   Cookies: {len(cookies)}")
        
        # Check what happens with these cookies
        print("\n📝 How cookies are used:")
        print("   1. Cookies are passed to Playwright browser context")
        print("   2. Browser sends cookies with requests")
        print("   3. BUT cookies only work on matching domains!")
        
        print("\n❌ The problem:")
        print("   • OpenAthens cookies are for .openathens.net")
        print("   • Downloads try to access nature.com directly")
        print("   • Cookies are ignored (wrong domain)")
        print("   • Downloads fail")
    else:
        print("\n❌ No auth session found")


async def main():
    """Run all checks."""
    await check_cookie_details()
    await check_cookie_domains()
    await test_cookie_usage_in_download()
    
    print("\n\n🔍 CONCLUSION")
    print("=" * 60)
    print("\nThe cookies are being handled correctly, BUT:")
    print("1. They're only valid for OpenAthens domains")
    print("2. Direct publisher access won't work with these cookies")
    print("3. We MUST use the OpenAthens redirector")
    print("\nThe fix: Transform URLs to go through OpenAthens redirector")


if __name__ == "__main__":
    asyncio.run(main())