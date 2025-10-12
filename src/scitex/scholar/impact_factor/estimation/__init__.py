"""
Legal Impact Factor Calculator

A comprehensive, legally compliant impact factor calculation system using
open APIs from OpenAlex, Crossref, and Semantic Scholar.

This package provides transparent, verifiable impact factor calculations
without relying on proprietary databases or restricted access systems.

Main components:
- ImpactFactorCalculator: Core calculation engine
- JournalMatcher: Advanced journal matching across data sources  
- CacheManager: Efficient caching system
- CLI: Command-line interface

Example usage:
    from impact_factor import ImpactFactorCalculator
    
    calculator = ImpactFactorCalculator()
    result = calculator.calculate_impact_factor("Nature")
    print(f"Impact Factor: {result['impact_factors']['classical_2year']}")
"""

from .core.calculator import ImpactFactorCalculator
from .core.journal_matcher import JournalMatcher
from .core.cache_manager import CacheManager
from .fetchers import OpenAlexFetcher, CrossrefFetcher, SemanticScholarFetcher

__version__ = "1.0.0"
__author__ = "SciTeX Team"
__email__ = "contact@scitex.ai"

__all__ = [
    "ImpactFactorCalculator",
    "JournalMatcher",
    "CacheManager", 
    "OpenAlexFetcher",
    "CrossrefFetcher",
    "SemanticScholarFetcher"
]
