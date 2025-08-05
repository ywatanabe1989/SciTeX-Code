#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-08-01 13:20:00"
# Author: Claude
# File: _MultiInstitutionalResolver.py

"""
Multi-institutional OpenURL resolver with automatic detection and fallback.

This module provides enhanced OpenURL resolution supporting multiple
institutions and automatic resolver detection.
"""

import os
import re
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs

from scitex import logging

from ._OpenURLResolver import OpenURLResolver
from .KNOWN_RESOLVERS import (
    KNOWN_RESOLVERS,
    get_resolver_by_institution,
    validate_resolver_url,
    TEST_DOIS
)

logger = logging.getLogger(__name__)


class MultiInstitutionalResolver(OpenURLResolver):
    """
    Enhanced OpenURL resolver supporting multiple institutions.
    
    Features:
    - Automatic institution detection from environment/config
    - Multiple resolver fallback
    - Resolver validation and testing
    - Support for 50+ institutions worldwide
    """
    
    def __init__(
        self,
        auth_manager=None,
        institution: Optional[str] = None,
        resolver_url: Optional[str] = None,
        auto_detect: bool = True,
        test_resolvers: bool = False,
        **kwargs
    ):
        """
        Initialize multi-institutional resolver.
        
        Args:
            auth_manager: Authentication manager
            institution: Institution name (e.g., "Harvard University")
            resolver_url: Direct resolver URL (overrides institution)
            auto_detect: Try to auto-detect institution from environment
            test_resolvers: Test resolver connectivity on init
            **kwargs: Additional arguments for parent class
        """
        # Try to determine resolver URL
        resolved_url = self._determine_resolver_url(
            institution, resolver_url, auto_detect
        )
        
        if not resolved_url:
            logger.warning(
                "No resolver URL found. Will use University of Melbourne as default."
            )
            resolved_url = KNOWN_RESOLVERS["University of Melbourne"]["url"]
        
        # Initialize parent with resolved URL
        super().__init__(auth_manager, resolved_url, **kwargs)
        
        self.institution = institution
        self.resolver_info = self._get_resolver_info(resolved_url)
        self.tested_resolvers = {}
        
        if test_resolvers and self.resolver_info:
            self._test_resolver_connectivity()
    
    def _determine_resolver_url(
        self,
        institution: Optional[str],
        resolver_url: Optional[str],
        auto_detect: bool
    ) -> Optional[str]:
        """Determine the best resolver URL to use."""
        
        # 1. Direct URL takes precedence
        if resolver_url:
            if validate_resolver_url(resolver_url):
                logger.info(f"Using provided resolver URL: {resolver_url}")
                return resolver_url
            else:
                logger.warning(f"Invalid resolver URL: {resolver_url}")
        
        # 2. Try institution name
        if institution:
            resolver_info = get_resolver_by_institution(institution)
            if resolver_info:
                logger.info(
                    f"Found resolver for {institution}: {resolver_info['url']}"
                )
                return resolver_info['url']
            else:
                logger.warning(f"No resolver found for institution: {institution}")
        
        # 3. Auto-detect from environment
        if auto_detect:
            # Check environment variables
            env_checks = [
                ("SCITEX_SCHOLAR_INSTITUTION", "institution"),
                ("UNIVERSITY_NAME", "institution"),
                ("INSTITUTION_NAME", "institution"),
                ("SCITEX_SCHOLAR_OPENURL_RESOLVER_URL", "url"),
                ("OPENURL_RESOLVER", "url"),
            ]
            
            for env_var, var_type in env_checks:
                value = os.getenv(env_var)
                if value:
                    if var_type == "institution":
                        resolver_info = get_resolver_by_institution(value)
                        if resolver_info:
                            logger.info(
                                f"Auto-detected institution from {env_var}: {value}"
                            )
                            return resolver_info['url']
                    else:  # url
                        if validate_resolver_url(value):
                            logger.info(
                                f"Auto-detected resolver URL from {env_var}"
                            )
                            return value
        
        return None
    
    def _get_resolver_info(self, url: str) -> Optional[Dict[str, str]]:
        """Get resolver information from URL."""
        for name, info in KNOWN_RESOLVERS.items():
            if info['url'] == url:
                return {
                    'name': name,
                    'url': info['url'],
                    'country': info.get('country', 'Unknown'),
                    'vendor': info.get('vendor', 'Unknown')
                }
        return None
    
    def _test_resolver_connectivity(self) -> bool:
        """Test if resolver is accessible."""
        try:
            import asyncio
            
            async def test():
                # Use a test DOI
                test_doi = TEST_DOIS.get("Nature", "10.1038/nature12373")
                result = await self._resolve_single_async(doi=test_doi)
                return result is not None
            
            success = asyncio.run(test())
            self.tested_resolvers[self.resolver_url] = success
            
            if success:
                logger.info(f"Resolver connectivity test passed: {self.resolver_url}")
            else:
                logger.warning(f"Resolver connectivity test failed: {self.resolver_url}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error testing resolver: {e}")
            self.tested_resolvers[self.resolver_url] = False
            return False
    
    def get_alternative_resolvers(
        self,
        country: Optional[str] = None,
        vendor: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Get alternative resolvers based on criteria.
        
        Args:
            country: Filter by country code (e.g., 'US')
            vendor: Filter by vendor (e.g., 'ExLibris')
            
        Returns:
            List of resolver information dicts
        """
        alternatives = []
        
        for name, info in KNOWN_RESOLVERS.items():
            # Skip current resolver
            if info['url'] == self.resolver_url:
                continue
            
            # Apply filters
            if country and info.get('country') != country.upper():
                continue
            if vendor and info.get('vendor', '').lower() != vendor.lower():
                continue
            
            alternatives.append({
                'name': name,
                'url': info['url'],
                'country': info.get('country', 'Unknown'),
                'vendor': info.get('vendor', 'Unknown')
            })
        
        return alternatives
    
    async def resolve_with_fallback_async(
        self,
        doi: str,
        max_attempts: int = 3,
        fallback_countries: Optional[List[str]] = None,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Resolve DOI with automatic fallback to other resolvers.
        
        Args:
            doi: DOI to resolve
            max_attempts: Maximum resolver attempts
            fallback_countries: Preferred fallback countries
            **kwargs: Additional arguments for resolution
            
        Returns:
            Resolution result or None
        """
        attempted_urls = set()
        
        # Try primary resolver
        logger.info(f"Attempting resolution with primary resolver: {self.resolver_url}")
        result = await self._resolve_single_async(doi=doi, **kwargs)
        
        if result and result.get('success'):
            return result
        
        attempted_urls.add(self.resolver_url)
        
        # Get fallback resolvers
        alternatives = self.get_alternative_resolvers()
        
        # Sort by preference
        if fallback_countries:
            # Prioritize by country
            alternatives.sort(
                key=lambda x: (
                    0 if x['country'] in fallback_countries else 1,
                    x['name']
                )
            )
        
        # Try alternatives
        for i, alt in enumerate(alternatives[:max_attempts-1]):
            if alt['url'] in attempted_urls:
                continue
            
            logger.info(
                f"Trying alternative resolver ({i+2}/{max_attempts}): "
                f"{alt['name']} ({alt['country']})"
            )
            
            # Temporarily switch resolver
            original_url = self.resolver_url
            self.resolver_url = alt['url']
            
            try:
                result = await self._resolve_single_async(doi=doi, **kwargs)
                
                if result and result.get('success'):
                    logger.info(f"Success with alternative: {alt['name']}")
                    return result
                    
            except Exception as e:
                logger.error(f"Error with {alt['name']}: {e}")
            finally:
                # Restore original resolver
                self.resolver_url = original_url
            
            attempted_urls.add(alt['url'])
        
        logger.warning(f"All resolver attempts failed for DOI: {doi}")
        return None
    
    def list_supported_institutions(
        self,
        country: Optional[str] = None,
        vendor: Optional[str] = None
    ) -> List[str]:
        """
        List all supported institutions.
        
        Args:
            country: Filter by country code
            vendor: Filter by vendor
            
        Returns:
            List of institution names
        """
        institutions = []
        
        for name, info in KNOWN_RESOLVERS.items():
            if country and info.get('country') != country.upper():
                continue
            if vendor and info.get('vendor', '').lower() != vendor.lower():
                continue
            
            institutions.append(name)
        
        return sorted(institutions)
    
    def get_resolver_stats(self) -> Dict[str, Any]:
        """Get statistics about available resolvers."""
        countries = {}
        vendors = {}
        
        for info in KNOWN_RESOLVERS.values():
            country = info.get('country', 'Unknown')
            vendor = info.get('vendor', 'Unknown')
            
            countries[country] = countries.get(country, 0) + 1
            vendors[vendor] = vendors.get(vendor, 0) + 1
        
        return {
            'total_resolvers': len(KNOWN_RESOLVERS),
            'countries': dict(sorted(countries.items())),
            'vendors': dict(sorted(vendors.items())),
            'current_resolver': self.resolver_info,
            'tested_resolvers': self.tested_resolvers
        }
    
    def __str__(self) -> str:
        """String representation."""
        if self.resolver_info:
            return (
                f"MultiInstitutionalResolver("
                f"{self.resolver_info['name']}, "
                f"{self.resolver_info['country']})"
            )
        else:
            return f"MultiInstitutionalResolver({self.resolver_url})"


# Convenience function for quick setup
def create_resolver(
    institution: Optional[str] = None,
    auth_manager=None,
    **kwargs
) -> MultiInstitutionalResolver:
    """
    Create a multi-institutional resolver with sensible defaults.
    
    Args:
        institution: Institution name or None for auto-detect
        auth_manager: Authentication manager
        **kwargs: Additional arguments
        
    Returns:
        Configured resolver instance
    """
    return MultiInstitutionalResolver(
        auth_manager=auth_manager,
        institution=institution,
        auto_detect=True,
        **kwargs
    )


if __name__ == "__main__":
    # Example usage
    
    # Auto-detect institution
    resolver = create_resolver()
    print(f"Using resolver: {resolver}")
    
    # Specific institution
    harvard_resolver = create_resolver("Harvard University")
    print(f"\nHarvard resolver: {harvard_resolver.resolver_url}")
    
    # List US institutions
    us_institutions = harvard_resolver.list_supported_institutions(country="US")
    print(f"\nUS institutions ({len(us_institutions)}):")
    for inst in us_institutions[:5]:
        print(f"  - {inst}")
    
    # Get stats
    stats = resolver.get_resolver_stats()
    print(f"\nResolver statistics:")
    print(f"  Total resolvers: {stats['total_resolvers']}")
    print(f"  Countries: {len(stats['countries'])}")
    print(f"  Top vendors: {list(stats['vendors'].keys())[:3]}")