#!/usr/bin/env python3
"""
Enhanced PDF Downloader Design - Separating Authentication from Discovery

This demonstrates the proper architecture where:
1. Authentication methods (OpenAthens, EZProxy, etc.) provide access
2. Discovery engines (Zotero, patterns, etc.) find PDFs
3. They work together for reliable downloads
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from pathlib import Path


class AuthenticationProvider(ABC):
    """Base class for authentication providers."""
    
    @abstractmethod
    async def is_authenticated(self) -> bool:
        """Check if currently authenticated."""
        pass
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """Perform authentication."""
        pass
    
    @abstractmethod
    async def get_authenticated_session(self) -> Any:
        """Get session/cookies for authenticated requests."""
        pass


class OpenAthensAuth(AuthenticationProvider):
    """OpenAthens authentication provider."""
    
    async def is_authenticated(self) -> bool:
        # Check cookies and do live verification
        pass
    
    async def authenticate(self) -> bool:
        # Open browser for manual login
        pass
    
    async def get_authenticated_session(self) -> Dict[str, Any]:
        # Return cookies/headers for requests
        pass


class EZProxyAuth(AuthenticationProvider):
    """EZProxy authentication provider."""
    # Future implementation
    pass


class ShibbolethAuth(AuthenticationProvider):
    """Shibboleth authentication provider."""
    # Future implementation
    pass


class PDFDiscoveryEngine(ABC):
    """Base class for PDF discovery engines."""
    
    @abstractmethod
    async def find_pdf_url(self, url: str, doi: str) -> Optional[str]:
        """Find PDF URL on a webpage."""
        pass
    
    @abstractmethod
    def supports_url(self, url: str) -> bool:
        """Check if this engine supports the URL."""
        pass


class ZoteroTranslatorEngine(PDFDiscoveryEngine):
    """Uses Zotero translators to find PDFs."""
    
    def __init__(self):
        from _ZoteroTranslatorRunner import ZoteroTranslatorRunner
        self.runner = ZoteroTranslatorRunner()
    
    def supports_url(self, url: str) -> bool:
        # Check if we have a translator for this site
        return self.runner.find_translator_for_url(url) is not None
    
    async def find_pdf_url(self, url: str, doi: str) -> Optional[str]:
        # Use translator to find PDF
        pdf_urls = await self.runner.extract_pdf_urls(url)
        return pdf_urls[0] if pdf_urls else None


class DirectPatternEngine(PDFDiscoveryEngine):
    """Uses URL patterns to construct PDF URLs."""
    
    PATTERNS = {
        "nature.com": lambda doi: f"https://www.nature.com/articles/{doi.split('/')[-1]}.pdf",
        "science.org": lambda doi: f"https://www.science.org/doi/pdf/{doi}",
        "cell.com": lambda doi: f"https://www.cell.com/action/showPdf?pii={doi}",
        # ... more patterns
    }
    
    def supports_url(self, url: str) -> bool:
        return any(domain in url for domain in self.PATTERNS)
    
    async def find_pdf_url(self, url: str, doi: str) -> Optional[str]:
        for domain, pattern in self.PATTERNS.items():
            if domain in url:
                return pattern(doi)
        return None


class PlaywrightScraperEngine(PDFDiscoveryEngine):
    """Uses Playwright to find PDF links on pages."""
    
    async def find_pdf_url(self, url: str, doi: str) -> Optional[str]:
        # Use Playwright to scrape for PDF links
        # This is the fallback for sites without specific support
        pass


class EnhancedPDFDownloader:
    """
    Enhanced PDF downloader with proper separation of concerns.
    
    Key improvements:
    1. Authentication is separate from discovery
    2. Multiple auth providers can be registered
    3. Discovery engines are tried in order of reliability
    4. Authentication is applied to all download attempts
    """
    
    def __init__(self):
        # Authentication providers
        self.auth_providers: List[AuthenticationProvider] = []
        
        # Discovery engines (in priority order)
        self.discovery_engines: List[PDFDiscoveryEngine] = [
            DirectPatternEngine(),      # Fastest
            ZoteroTranslatorEngine(),   # Most reliable
            PlaywrightScraperEngine(),  # Fallback
        ]
        
        # Download settings
        self.timeout = 30
        self.max_retries = 3
    
    def add_auth_provider(self, provider: AuthenticationProvider):
        """Add an authentication provider."""
        self.auth_providers.append(provider)
    
    async def download_pdf(
        self,
        doi: str,
        url: str,
        output_path: Path
    ) -> Optional[Path]:
        """
        Download PDF with authentication + discovery.
        
        Flow:
        1. Ensure authentication (if any providers registered)
        2. Try each discovery engine to find PDF URL
        3. Download with authenticated session
        """
        
        # Step 1: Ensure authentication
        auth_session = None
        for provider in self.auth_providers:
            if await provider.is_authenticated():
                auth_session = await provider.get_authenticated_session()
                print(f"✓ Authenticated with {provider.__class__.__name__}")
                break
            else:
                print(f"Authenticating with {provider.__class__.__name__}...")
                if await provider.authenticate():
                    auth_session = await provider.get_authenticated_session()
                    print("✓ Authentication successful")
                    break
        
        # Step 2: Find PDF URL using discovery engines
        pdf_url = None
        used_engine = None
        
        for engine in self.discovery_engines:
            if engine.supports_url(url):
                print(f"Trying {engine.__class__.__name__}...")
                pdf_url = await engine.find_pdf_url(url, doi)
                if pdf_url:
                    used_engine = engine.__class__.__name__
                    print(f"✓ Found PDF URL: {pdf_url}")
                    break
        
        if not pdf_url:
            print("✗ No engine could find PDF URL")
            return None
        
        # Step 3: Download with authentication
        headers = {}
        cookies = {}
        
        if auth_session:
            headers.update(auth_session.get('headers', {}))
            cookies.update(auth_session.get('cookies', {}))
        
        # Actual download logic here...
        print(f"Downloading from {pdf_url} using {used_engine}")
        if auth_session:
            print("  with authenticated session")
        
        # Return path if successful
        return output_path


# Example usage
async def example_usage():
    """Show how the enhanced downloader works."""
    
    downloader = EnhancedPDFDownloader()
    
    # Add authentication if needed
    openathens = OpenAthensAuth()
    downloader.add_auth_provider(openathens)
    
    # Download a paper
    doi = "10.1038/s41586-021-03819-2"
    url = "https://www.nature.com/articles/s41586-021-03819-2"
    output = Path("./paper.pdf")
    
    result = await downloader.download_pdf(doi, url, output)
    
    if result:
        print(f"✓ Downloaded to {result}")
    else:
        print("✗ Download failed")


# Benefits of this architecture:
print("""
Benefits of Separating Authentication from Discovery:

1. Modularity:
   - Easy to add new auth methods (EZProxy, Shibboleth)
   - Easy to add new discovery engines
   - Each component has a single responsibility

2. Flexibility:
   - Can use multiple auth providers
   - Discovery engines work with any auth method
   - Graceful fallbacks at each level

3. Reliability:
   - Zotero Translators know exact PDF locations
   - Authentication ensures access
   - Combined = very high success rate

4. Performance:
   - Try fast methods first (direct patterns)
   - Only use slow methods if needed
   - Authentication cached across downloads

5. Future-proof:
   - New publishers? Add translator or pattern
   - New auth system? Add provider
   - No need to rewrite core logic
""")