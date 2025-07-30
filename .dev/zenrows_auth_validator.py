#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-30 20:50:00 (ywatanabe)"
# File: ./.dev/zenrows_auth_validator.py
# ----------------------------------------
"""Step-by-step implementation: First validate authentication using ZenRows.

Based on the updated suggestions.md, this implements authentication validation
as the first step before attempting to access publisher content.
"""

import asyncio
import json
import aiohttp
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import hashlib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ZenRowsAuthValidator:
    """Validates authentication cookies using ZenRows API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session_dir = Path.home() / ".scitex/scholar/zenrows_sessions"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_session_path(self, email: str) -> Path:
        """Get path for session file based on email hash."""
        email_hash = hashlib.md5(email.encode()).hexdigest()[:8]
        return self.session_dir / f"session_{email_hash}.json"
        
    async def save_cookies(self, email: str, cookies: List[Dict]) -> Path:
        """Save cookies to session file.
        
        Args:
            email: User email for session identification
            cookies: List of cookie dictionaries
            
        Returns:
            Path to saved session file
        """
        session_path = self._get_session_path(email)
        
        session_data = {
            "email": email,
            "timestamp": datetime.now().isoformat(),
            "full_cookies": cookies,
            "cookie_count": len(cookies)
        }
        
        with open(session_path, 'w') as f:
            json.dump(session_data, f, indent=2)
            
        logger.info(f"💾 Saved {len(cookies)} cookies to {session_path}")
        return session_path
        
    async def check_auth_with_zenrows(
        self, 
        cookie_cache_path: Path,
        test_url: str = "https://my.openathens.net/?passiveLogin=false"
    ) -> Tuple[bool, Dict]:
        """Check if saved cookies are valid using ZenRows.
        
        Args:
            cookie_cache_path: Path to JSON file with cookies
            test_url: URL that redirects when authenticated
            
        Returns:
            Tuple of (is_valid, details_dict)
        """
        if not cookie_cache_path.exists():
            return False, {"error": f"Cookie cache not found at: {cookie_cache_path}"}
            
        # Load cookies
        try:
            with open(cookie_cache_path, 'r') as f:
                cache_data = json.load(f)
                
            cookies_list = cache_data.get("full_cookies", [])
            if not cookies_list:
                return False, {"error": "No cookies found in cache file"}
                
            # Format cookies for HTTP header
            cookie_string = "; ".join([
                f"{c['name']}={c['value']}" 
                for c in cookies_list
            ])
            
            logger.info(f"🍪 Loaded {len(cookies_list)} cookies for validation")
            
        except Exception as e:
            return False, {"error": f"Error reading cookie file: {e}"}
            
        # Prepare ZenRows request
        params = {
            "url": test_url,
            "apikey": self.api_key,
            "js_render": "true",
            "premium_proxy": "true",
            "custom_cookies": cookie_string
        }
        
        logger.info(f"🔍 Validating authentication at {test_url}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.zenrows.com/v1/",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=45)
                ) as response:
                    
                    if response.status != 200:
                        return False, {
                            "error": f"ZenRows API failed with status {response.status}"
                        }
                        
                    html_content = await response.text()
                    
                    # Get the final URL from response headers if available
                    final_url = response.headers.get('Zr-Final-Url', test_url)
                    
                    # Check for authentication indicators
                    content_lower = html_content.lower()
                    
                    success_indicators = [
                        "your account", "my account",
                        "log out", "sign out", "logout",
                        "dashboard", "profile"
                    ]
                    
                    failure_indicators = [
                        "sign in", "log in", "login",
                        "enter your email", "enter password",
                        "forgot password"
                    ]
                    
                    has_success = any(
                        indicator in content_lower 
                        for indicator in success_indicators
                    )
                    
                    has_failure = any(
                        indicator in content_lower 
                        for indicator in failure_indicators
                    )
                    
                    # Check URL redirect
                    redirected = final_url != test_url
                    to_account = any(
                        path in final_url 
                        for path in ['/account', '/app', '/dashboard']
                    )
                    
                    is_valid = has_success and not has_failure
                    
                    details = {
                        "is_valid": is_valid,
                        "final_url": final_url,
                        "redirected": redirected,
                        "to_account_page": to_account,
                        "has_success_indicators": has_success,
                        "has_failure_indicators": has_failure,
                        "cookie_count": len(cookies_list),
                        "test_url": test_url
                    }
                    
                    if is_valid:
                        logger.info("✅ Authentication valid - cookies are working")
                    else:
                        logger.warning("❌ Authentication invalid - cookies may be expired")
                        
                    return is_valid, details
                    
        except asyncio.TimeoutError:
            return False, {"error": "Request timed out"}
        except Exception as e:
            return False, {"error": f"Unexpected error: {e}"}
            
    async def validate_for_publisher(
        self,
        cookie_cache_path: Path,
        publisher_url: str
    ) -> Tuple[bool, Dict]:
        """Validate cookies work for a specific publisher.
        
        Args:
            cookie_cache_path: Path to cookie cache
            publisher_url: Publisher URL to test
            
        Returns:
            Tuple of (has_access, details)
        """
        if not cookie_cache_path.exists():
            return False, {"error": "Cookie cache not found"}
            
        # Load cookies
        try:
            with open(cookie_cache_path, 'r') as f:
                cache_data = json.load(f)
                
            cookies_list = cache_data.get("full_cookies", [])
            cookie_string = "; ".join([
                f"{c['name']}={c['value']}" 
                for c in cookies_list
            ])
            
        except Exception as e:
            return False, {"error": f"Error reading cookies: {e}"}
            
        # Test access to publisher
        params = {
            "url": publisher_url,
            "apikey": self.api_key,
            "js_render": "true",
            "premium_proxy": "true",
            "custom_cookies": cookie_string
        }
        
        logger.info(f"🔍 Testing publisher access at {publisher_url}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.zenrows.com/v1/",
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    
                    if response.status != 200:
                        return False, {
                            "error": f"ZenRows returned status {response.status}"
                        }
                        
                    content = await response.text()
                    content_lower = content.lower()
                    
                    # Check for access
                    access_indicators = [
                        "full text", "download pdf", "view pdf",
                        "download article", "read article",
                        "institutional access"
                    ]
                    
                    blocked_indicators = [
                        "access denied", "purchase article",
                        "subscribe", "get access",
                        "paywall", "buy article"
                    ]
                    
                    has_access = any(
                        indicator in content_lower 
                        for indicator in access_indicators
                    )
                    
                    is_blocked = any(
                        indicator in content_lower 
                        for indicator in blocked_indicators
                    )
                    
                    # Save a snippet for debugging
                    snippet_path = self.session_dir / f"publisher_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                    with open(snippet_path, 'w', encoding='utf-8') as f:
                        f.write(content[:5000])  # First 5KB
                        
                    details = {
                        "has_access": has_access and not is_blocked,
                        "has_access_indicators": has_access,
                        "has_blocked_indicators": is_blocked,
                        "content_snippet": snippet_path.as_posix(),
                        "publisher_url": publisher_url
                    }
                    
                    return has_access and not is_blocked, details
                    
        except Exception as e:
            return False, {"error": f"Error testing publisher: {e}"}


async def test_auth_validation():
    """Test the authentication validation flow."""
    
    api_key = os.environ.get("ZENROWS_API_KEY", "822225799f9a4d847163f397ef86bb81b3f5ceb5")
    validator = ZenRowsAuthValidator(api_key)
    
    # For testing, we'll simulate having cookies
    # In real use, these would come from OpenAthens authentication
    test_email = "test@university.edu"
    
    print("\n🧪 ZenRows Authentication Validation Test")
    print("="*60)
    
    # Step 1: Check if we have existing session
    session_path = validator._get_session_path(test_email)
    
    if session_path.exists():
        print(f"📁 Found existing session at: {session_path}")
        
        # Validate existing session
        is_valid, details = await validator.check_auth_with_zenrows(session_path)
        
        print(f"\n📊 Validation Results:")
        print(f"   Valid: {'✅' if is_valid else '❌'}")
        print(f"   Final URL: {details.get('final_url', 'N/A')}")
        print(f"   Success indicators: {details.get('has_success_indicators', False)}")
        print(f"   Failure indicators: {details.get('has_failure_indicators', False)}")
        
        if is_valid:
            # Test with a publisher
            print("\n🔍 Testing publisher access...")
            publisher_url = "https://www.nature.com/articles/nature12373"
            
            has_access, pub_details = await validator.validate_for_publisher(
                session_path, publisher_url
            )
            
            print(f"\n📊 Publisher Access Results:")
            print(f"   Has access: {'✅' if has_access else '❌'}")
            print(f"   Access indicators: {pub_details.get('has_access_indicators', False)}")
            print(f"   Blocked indicators: {pub_details.get('has_blocked_indicators', False)}")
            
    else:
        print(f"❌ No existing session found")
        print(f"   Would need to authenticate first to create session at: {session_path}")
        print("\n💡 In production, this would trigger OpenAthens authentication")
        print("   Then save cookies using validator.save_cookies()")


async def test_with_real_cookies():
    """Test with real cookie data (you need to provide cookies)."""
    
    api_key = os.environ.get("ZENROWS_API_KEY", "822225799f9a4d847163f397ef86bb81b3f5ceb5")
    validator = ZenRowsAuthValidator(api_key)
    
    # Example: If you have cookies from a browser session
    # You would capture these from your authenticated browser
    example_cookies = [
        {
            "name": "session_id",
            "value": "example_session_value",
            "domain": ".openathens.net",
            "path": "/"
        },
        # Add more cookies as captured
    ]
    
    # Save cookies
    email = "your_email@university.edu"
    session_path = await validator.save_cookies(email, example_cookies)
    
    # Validate
    is_valid, details = await validator.check_auth_with_zenrows(session_path)
    print(f"Authentication valid: {is_valid}")
    print(f"Details: {json.dumps(details, indent=2)}")


if __name__ == "__main__":
    # Run the basic test
    asyncio.run(test_auth_validation())
    
    # Uncomment to test with real cookies
    # asyncio.run(test_with_real_cookies())