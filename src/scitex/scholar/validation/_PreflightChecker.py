#!/usr/bin/env python3
"""Pre-flight checks for Scholar PDF downloads.

This module performs comprehensive checks before attempting downloads
to fail fast with clear error messages and reduce debugging time.
"""

import asyncio
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import warnings

try:
    import aiohttp
except ImportError:
    aiohttp = None

try:
    from playwright.async_api import async_playwright
except ImportError:
    async_playwright = None

from ...errors import ScholarError, SciTeXWarning


class PreflightChecker:
    """Perform pre-flight checks before PDF downloads."""
    
    def __init__(self):
        self.checks_passed = {}
        self.warnings = []
        self.errors = []
    
    async def run_all_checks_async(
        self,
        download_dir: Optional[Path] = None,
        use_translators: bool = True,
        use_playwright: bool = True,
        use_openathens: bool = False,
        zenrows_api_key: Optional[str] = None,
        openurl_resolver: Optional[str] = None,
    ) -> Dict[str, Union[bool, str, List[str]]]:
        """Run all pre-flight checks.
        
        Returns:
            Dictionary with check results and recommendations
        """
        # Reset state
        self.checks_passed = {}
        self.warnings = []
        self.errors = []
        
        # Run checks
        await self._check_python_version_async()
        await self._check_required_packages_async()
        await self._check_optional_features_async(
            use_translators, use_playwright, use_openathens, zenrows_api_key
        )
        await self._check_download_directory_async(download_dir)
        await self._check_network_connectivity_async()
        await self._check_authentication_status_async(use_openathens, zenrows_api_key)
        await self._check_system_resources_async()
        
        # Compile results
        all_passed = all(self.checks_passed.values())
        
        return {
            'all_passed': all_passed,
            'checks': self.checks_passed,
            'warnings': self.warnings,
            'errors': self.errors,
            'recommendations': self._get_recommendations()
        }
    
    async def _check_python_version_async(self):
        """Check Python version compatibility."""
        version = sys.version_info
        is_compatible = version >= (3, 8)
        
        self.checks_passed['python_version'] = is_compatible
        
        if not is_compatible:
            self.errors.append(
                f"Python {version.major}.{version.minor} detected. "
                f"SciTeX Scholar requires Python 3.8+"
            )
        
        return is_compatible
    
    async def _check_required_packages_async(self):
        """Check if required packages are installed."""
        required = {
            'aiohttp': aiohttp,
            'pandas': None,  # Check by import
            'numpy': None,
            'scipy': None,
        }
        
        missing = []
        
        for package, module in required.items():
            if module is None:
                try:
                    __import__(package)
                except ImportError:
                    missing.append(package)
            elif module is None:
                missing.append(package)
        
        self.checks_passed['required_packages'] = len(missing) == 0
        
        if missing:
            self.errors.append(
                f"Missing required packages: {', '.join(missing)}. "
                f"Install with: pip install {' '.join(missing)}"
            )
        
        return len(missing) == 0
    
    async def _check_optional_features_async(
        self,
        use_translators: bool,
        use_playwright: bool,
        use_openathens: bool,
        zenrows_api_key: Optional[str]
    ):
        """Check optional feature dependencies."""
        
        # Check Playwright
        if use_playwright or use_openathens:
            if async_playwright is None:
                self.warnings.append(
                    "Playwright not installed. JavaScript-heavy sites may fail. "
                    "Install with: pip install playwright && playwright install"
                )
                self.checks_passed['playwright'] = False
            else:
                # Check if browsers are installed
                try:
                    result = subprocess.run(
                        ['playwright', 'install', '--dry-run'],
                        capture_output=True,
                        text=True
                    )
                    if "already installed" not in result.stdout:
                        self.warnings.append(
                            "Playwright browsers not installed. "
                            "Run: playwright install"
                        )
                        self.checks_passed['playwright_browsers'] = False
                    else:
                        self.checks_passed['playwright_browsers'] = True
                except:
                    self.checks_passed['playwright_browsers'] = False
        
        # Check Zotero translators
        if use_translators:
            translator_dir = Path.home() / '.scitex' / 'scholar' / 'zotero_translators'
            if not translator_dir.exists() or not any(translator_dir.glob('*.js')):
                self.warnings.append(
                    f"Zotero translators not found at {translator_dir}. "
                    f"Some publishers may not work optimally."
                )
                self.checks_passed['zotero_translators'] = False
            else:
                translator_count = len(list(translator_dir.glob('*.js')))
                self.checks_passed['zotero_translators'] = True
                self.checks_passed['translator_count'] = translator_count
        
        # Check ZenRows
        if zenrows_api_key:
            if not zenrows_api_key.startswith('afe7'):
                self.warnings.append(
                    "ZenRows API key format looks incorrect. "
                    "Keys should start with 'afe7'"
                )
                self.checks_passed['zenrows_key_format'] = False
            else:
                self.checks_passed['zenrows_key_format'] = True
    
    async def _check_download_directory_async(self, download_dir: Optional[Path]):
        """Check download directory permissions."""
        if download_dir is None:
            download_dir = Path.home() / '.scitex' / 'scholar' / 'pdfs'
        
        try:
            download_dir.mkdir(parents=True, exist_ok=True)
            
            # Test write permissions
            test_file = download_dir / '.write_test'
            test_file.write_text('test')
            test_file.unlink()
            
            self.checks_passed['download_directory'] = True
            
            # Check disk space
            import shutil
            stats = shutil.disk_usage(download_dir)
            free_gb = stats.free / (1024**3)
            
            if free_gb < 1:
                self.warnings.append(
                    f"Low disk space: {free_gb:.1f} GB free at {download_dir}"
                )
                self.checks_passed['disk_space'] = False
            else:
                self.checks_passed['disk_space'] = True
                
        except Exception as e:
            self.errors.append(
                f"Cannot write to download directory {download_dir}: {e}"
            )
            self.checks_passed['download_directory'] = False
    
    async def _check_network_connectivity_async(self):
        """Check network connectivity to key services."""
        test_urls = {
            'internet': 'https://www.google.com',
            'crossref': 'https://api.crossref.org/works',
            'unpaywall': 'https://api.unpaywall.org',
            'pubmed': 'https://pubmed.ncbi.nlm.nih.gov/',
        }
        
        if aiohttp is None:
            self.checks_passed['network'] = False
            self.errors.append("aiohttp not installed, cannot check network")
            return
        
        async with aiohttp.ClientSession() as session:
            for service, url in test_urls.items():
                try:
                    async with session.get(url, timeout=5) as response:
                        if response.status < 500:
                            self.checks_passed[f'network_{service}'] = True
                        else:
                            self.warnings.append(
                                f"{service} returned status {response.status}"
                            )
                            self.checks_passed[f'network_{service}'] = False
                except Exception as e:
                    self.warnings.append(
                        f"Cannot reach {service} ({url}): {type(e).__name__}"
                    )
                    self.checks_passed[f'network_{service}'] = False
    
    async def _check_authentication_status_async(
        self,
        use_openathens: bool,
        zenrows_api_key: Optional[str]
    ):
        """Check authentication configurations."""
        
        # Check OpenAthens
        if use_openathens:
            session_dir = Path.home() / '.scitex' / 'scholar' / 'openathens_sessions'
            if session_dir.exists() and any(session_dir.glob('*.enc')):
                self.checks_passed['openathens_session'] = True
            else:
                self.warnings.append(
                    "OpenAthens enabled but no active sessions found. "
                    "You may need to authenticate_async."
                )
                self.checks_passed['openathens_session'] = False
        
        # Check ZenRows credits (if possible)
        if zenrows_api_key and aiohttp:
            try:
                # ZenRows doesn't have a direct credit check API
                # but we can test with a simple request
                async with aiohttp.ClientSession() as session:
                    test_url = 'https://httpbin.org/headers'
                    api_url = f"https://api.zenrows.com/v1/?apikey={zenrows_api_key}&url={test_url}"
                    
                    async with session.get(api_url, timeout=10) as response:
                        if response.status == 200:
                            self.checks_passed['zenrows_credits'] = True
                        elif response.status == 422:
                            self.errors.append(
                                "ZenRows API key appears to be invalid or out of credits"
                            )
                            self.checks_passed['zenrows_credits'] = False
                        else:
                            self.warnings.append(
                                f"ZenRows test returned status {response.status}"
                            )
                            self.checks_passed['zenrows_credits'] = False
            except Exception as e:
                self.warnings.append(
                    f"Could not verify ZenRows API key: {type(e).__name__}"
                )
                self.checks_passed['zenrows_credits'] = False
    
    async def _check_system_resources_async(self):
        """Check system resources."""
        try:
            import psutil
            
            # Check memory
            memory = psutil.virtual_memory()
            if memory.available < 1e9:  # Less than 1GB
                self.warnings.append(
                    f"Low memory: {memory.available / 1e9:.1f} GB available"
                )
                self.checks_passed['memory'] = False
            else:
                self.checks_passed['memory'] = True
            
            # Check CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 90:
                self.warnings.append(
                    f"High CPU usage: {cpu_percent}%"
                )
                self.checks_passed['cpu'] = False
            else:
                self.checks_passed['cpu'] = True
                
        except ImportError:
            # psutil not installed, skip resource checks
            pass
    
    def _get_recommendations(self) -> List[str]:
        """Get recommendations based on check results."""
        recommendations = []
        
        # Python version
        if not self.checks_passed.get('python_version', True):
            recommendations.append(
                "Upgrade Python: conda create -n scitex python=3.11"
            )
        
        # Required packages
        if not self.checks_passed.get('required_packages', True):
            recommendations.append(
                "Install requirements: pip install -r requirements.txt"
            )
        
        # Playwright
        if not self.checks_passed.get('playwright_browsers', True):
            recommendations.append(
                "Install browsers: playwright install chromium"
            )
        
        # Translators
        if not self.checks_passed.get('zotero_translators', True):
            recommendations.append(
                "Download translators: python -m scitex.scholar.download.setup_translators"
            )
        
        # Network
        if not self.checks_passed.get('network_internet', True):
            recommendations.append(
                "Check internet connection or proxy settings"
            )
        
        # Disk space
        if not self.checks_passed.get('disk_space', True):
            recommendations.append(
                "Free up disk space (need at least 1GB for PDFs)"
            )
        
        # Memory
        if not self.checks_passed.get('memory', True):
            recommendations.append(
                "Close other applications to free up memory"
            )
        
        return recommendations


async def run_preflight_checks_async(**kwargs) -> Dict[str, Any]:
    """Convenience function to run pre-flight checks.
    
    Returns:
        Dictionary with check results
    
    Raises:
        ScholarError: If critical checks fail
    """
    checker = PreflightChecker()
    results = await checker.run_all_checks_async(**kwargs)
    
    if not results['all_passed']:
        # Issue warnings for non-critical failures
        for warning in results['warnings']:
            warnings.warn(warning, SciTeXWarning)
        
        # Raise error for critical failures
        if results['errors']:
            error_msg = "Pre-flight checks failed:\n" + "\n".join(results['errors'])
            if results['recommendations']:
                error_msg += "\n\nRecommendations:\n" + "\n".join(results['recommendations'])
            raise ScholarError(error_msg)
    
    return results