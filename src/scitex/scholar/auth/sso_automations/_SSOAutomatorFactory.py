#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-01 04:33:00 (claude)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/sso_automations/_SSOAutomatorFactory.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/sso_automations/_SSOAutomatorFactory.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""Factory for creating SSO automators."""

from typing import Optional, Dict, Any

from scitex import logging
from ._BaseSSOAutomator import BaseSSOAutomator

logger = logging.getLogger(__name__)


class SSOAutomatorFactory:
    """Factory for creating institution-specific SSO automators."""
    
    @classmethod
    def create_from_url(cls, url: str, **kwargs) -> Optional[BaseSSOAutomator]:
        """Auto-detect institution from URL and create appropriate automator.
        
        Args:
            url: URL to analyze for institution detection
            **kwargs: Arguments to pass to automator constructor
            
        Returns:
            Appropriate SSO automator instance, or None if not detected
        """
        url_lower = url.lower()
        
        # University of Melbourne
        if any(indicator in url_lower for indicator in [
            "unimelb",
            "melbourne.edu.au",
            "exlibrisgroup.com/sfxlcl41"  # UniMelb's OpenURL resolver
        ]):
            from ._UniversityOfMelbourneSSOAutomator import UniversityOfMelbourneSSOAutomator
            logger.info("Detected University of Melbourne from URL")
            return UniversityOfMelbourneSSOAutomator(**kwargs)
            
        # Add more institutions here as needed
        # Example:
        # if "harvard" in url_lower:
        #     from ._HarvardSSOAutomator import HarvardSSOAutomator
        #     return HarvardSSOAutomator(**kwargs)
            
        logger.debug(f"No SSO automator found for URL: {url}")
        return None
        
    @classmethod
    def create_by_name(cls, institution_name: str, **kwargs) -> Optional[BaseSSOAutomator]:
        """Create SSO automator by institution name.
        
        Args:
            institution_name: Name of institution (case-insensitive)
            **kwargs: Arguments to pass to automator constructor
            
        Returns:
            Appropriate SSO automator instance, or None if not found
        """
        name_lower = institution_name.lower()
        
        # Map of institution names to automators
        institution_map = {
            "unimelb": "UniversityOfMelbourne",
            "university of melbourne": "UniversityOfMelbourne",
            "melbourne": "UniversityOfMelbourne",
            "melbourne university": "UniversityOfMelbourne",
            # Add more mappings as needed
        }
        
        # Find matching institution
        automator_name = None
        for key, value in institution_map.items():
            if key in name_lower:
                automator_name = value
                break
                
        if not automator_name:
            logger.warning(f"No SSO automator found for institution: {institution_name}")
            return None
            
        # Import and create automator
        try:
            if automator_name == "UniversityOfMelbourne":
                from ._UniversityOfMelbourneSSOAutomator import UniversityOfMelbourneSSOAutomator
                return UniversityOfMelbourneSSOAutomator(**kwargs)
            # Add more elif blocks for other institutions
            
        except ImportError as e:
            logger.error(f"Failed to import automator {automator_name}: {e}")
            return None
            
    @classmethod
    def list_supported_institutions(cls) -> Dict[str, str]:
        """Get list of supported institutions.
        
        Returns:
            Dictionary mapping institution IDs to names
        """
        return {
            "unimelb": "University of Melbourne",
            # Add more as implemented
        }

# EOF