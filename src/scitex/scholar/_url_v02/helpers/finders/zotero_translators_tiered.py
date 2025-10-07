#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tiered Zotero Translator Runner

Implements a prioritized approach to running Zotero translators based on their
importance and coverage. This ensures the most critical publishers are handled
first with optimized execution strategies.
"""

from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum

from scitex.logging import getLogger

logger = getLogger(__name__)


class TranslatorTier(Enum):
    """Priority tiers for Zotero translators."""
    TIER_1_CORE_GIANTS = 1  # Must-have publishers with massive coverage
    TIER_2_AGGREGATORS = 2  # Major databases and search engines
    TIER_3_HIGH_IMPACT = 3  # Influential individual publishers
    TIER_4_OPEN_ACCESS = 4  # Open access and platform providers
    TIER_5_OTHER = 5       # All other translators


@dataclass
class TranslatorInfo:
    """Information about a Zotero translator."""
    name: str
    filename: str
    tier: TranslatorTier
    description: str
    expected_pattern: str  # 'global', 'object_em', 'object_translator', etc.
    priority: int  # Within tier priority (1 = highest)


class TieredZoteroTranslatorManager:
    """
    Manages Zotero translators in a tiered priority system for optimal coverage.
    
    Based on the analysis showing that ~20-25 translators cover 80% of academic literature.
    """
    
    # Define the tiered translator mappings
    TRANSLATOR_TIERS = {
        TranslatorTier.TIER_1_CORE_GIANTS: [
            Translatorinfo("ScienceDirect", "ScienceDirect.js", 
                          TranslatorTier.TIER_1_CORE_GIANTS,
                          "Elsevier journals - largest scientific publisher",
                          "global", 1),
            Translatorinfo("Springer Link", "Springer Link.js",
                          TranslatorTier.TIER_1_CORE_GIANTS,
                          "Springer content - major scientific publisher", 
                          "global", 2),
            Translatorinfo("Wiley Online Library", "Wiley Online Library.js",
                          TranslatorTier.TIER_1_CORE_GIANTS,
                          "Wiley journals - major multidisciplinary publisher",
                          "global", 3),
            Translatorinfo("Taylor and Francis+NEJM", "Taylor and Francis+NEJM.js",
                          TranslatorTier.TIER_1_CORE_GIANTS,
                          "Taylor & Francis and New England Journal of Medicine",
                          "global", 4),
            Translatorinfo("SAGE Journals", "SAGE Journals.js",
                          TranslatorTier.TIER_1_CORE_GIANTS,
                          "SAGE publications - social sciences and humanities",
                          "global", 5),
        ],
        
        TranslatorTier.TIER_2_AGGREGATORS: [
            Translatorinfo("PubMed", "PubMed.js",
                          TranslatorTier.TIER_2_AGGREGATORS,
                          "Essential biomedical research database",
                          "global", 1),
            Translatorinfo("Google Scholar", "Google Scholar.js",
                          TranslatorTier.TIER_2_AGGREGATORS,
                          "Most widely used academic search engine",
                          "global", 2),
            Translatorinfo("JSTOR", "JSTOR.js",
                          TranslatorTier.TIER_2_AGGREGATORS,
                          "Critical archive for humanities and social sciences",
                          "global", 3),
            Translatorinfo("arXiv.org", "arXiv.org.js",
                          TranslatorTier.TIER_2_AGGREGATORS,
                          "Main preprint server for physics, CS, and math",
                          "global", 4),
            Translatorinfo("Project MUSE", "Project MUSE.js",
                          TranslatorTier.TIER_2_AGGREGATORS,
                          "Key aggregator for humanities and social sciences",
                          "global", 5),
        ],
        
        TranslatorTier.TIER_3_HIGH_IMPACT: [
            Translatorinfo("Nature Publishing Group", "Nature Publishing Group.js",
                          TranslatorTier.TIER_3_HIGH_IMPACT,
                          "Nature and associated high-impact journals",
                          "global", 1),
            Translatorinfo("ACS Publications", "ACS Publications.js",
                          TranslatorTier.TIER_3_HIGH_IMPACT,
                          "American Chemical Society journals",
                          "global", 2),
            Translatorinfo("ACM Digital Library", "ACM Digital Library.js",
                          TranslatorTier.TIER_3_HIGH_IMPACT,
                          "Association for Computing Machinery",
                          "global", 3),
            Translatorinfo("IEEE Xplore", "IEEE Xplore.js",
                          TranslatorTier.TIER_3_HIGH_IMPACT,
                          "Institute of Electrical and Electronics Engineers",
                          "global", 4),
            Translatorinfo("Oxford Academic", "Oxford Academic.js",
                          TranslatorTier.TIER_3_HIGH_IMPACT,
                          "Oxford University Press journals",
                          "global", 5),
            Translatorinfo("Cambridge Core", "Cambridge Core.js",
                          TranslatorTier.TIER_3_HIGH_IMPACT,
                          "Cambridge University Press",
                          "global", 6),
        ],
        
        TranslatorTier.TIER_4_OPEN_ACCESS: [
            Translatorinfo("HighWire 2.0", "HighWire 2.0.js",
                          TranslatorTier.TIER_4_OPEN_ACCESS,
                          "Platform for many societies and bioRxiv",
                          "global", 1),
            Translatorinfo("Atypon Journals", "Atypon Journals.js",
                          TranslatorTier.TIER_4_OPEN_ACCESS,
                          "Large platform provider for many publishers",
                          "global", 2),
            Translatorinfo("BioMed Central", "BioMed Central.js",
                          TranslatorTier.TIER_4_OPEN_ACCESS,
                          "Major open-access publisher",
                          "global", 3),
            Translatorinfo("PLOS Journals", "PLoS Journals.js",
                          TranslatorTier.TIER_4_OPEN_ACCESS,
                          "Public Library of Science open-access journals",
                          "global", 4),
            Translatorinfo("Frontiers", "Frontiers.js",
                          TranslatorTier.TIER_4_OPEN_ACCESS,
                          "Open-access publisher with em object pattern",
                          "object_em", 5),
            Translatorinfo("MDPI", "MDPI.js",
                          TranslatorTier.TIER_4_OPEN_ACCESS,
                          "Multidisciplinary Digital Publishing Institute",
                          "global", 6),
        ],
    }
    
    def __init__(self, translator_dir: Optional[Path] = None):
        """Initialize the tiered translator manager."""
        self.translator_dir = translator_dir or Path(__file__).parent / "zotero_translators"
        self.translators_by_tier = self.TRANSLATOR_TIERS.copy()
        self._load_additional_translators()
        
    def _load_additional_translators(self):
        """Load any additional translators not in the predefined tiers."""
        tier_5_translators = []
        
        # Get all translator files
        all_files = set(self.translator_dir.glob("*.js"))
        
        # Get already mapped files
        mapped_files = set()
        for tier_translators in self.translators_by_tier.values():
            for trans_info in tier_translators:
                mapped_files.add(trans_info.filename)
        
        # Add unmapped translators to Tier 5
        for js_file in all_files:
            if js_file.name not in mapped_files and not js_file.name.startswith("_"):
                tier_5_translators.append(
                    TranslatorInfo(
                        name=js_file.stem,
                        filename=js_file.name,
                        tier=TranslatorTier.TIER_5_OTHER,
                        description="Additional translator",
                        expected_pattern="unknown",
                        priority=99
                    )
                )
        
        if tier_5_translators:
            self.translators_by_tier[TranslatorTier.TIER_5_OTHER] = tier_5_translators
            
    def get_translator_for_url(self, url: str, tier_limit: Optional[TranslatorTier] = None) -> Optional[TranslatorInfo]:
        """
        Find the best translator for a given URL.
        
        Args:
            url: The URL to match
            tier_limit: Only search up to this tier (inclusive)
            
        Returns:
            The best matching TranslatorInfo or None
        """
        import re
        
        # URL to translator mapping patterns
        url_patterns = {
            r"sciencedirect\.com": "ScienceDirect",
            r"link\.springer\.com": "Springer Link",
            r"onlinelibrary\.wiley\.com": "Wiley Online Library",
            r"tandfonline\.com": "Taylor and Francis+NEJM",
            r"nejm\.org": "Taylor and Francis+NEJM",
            r"journals\.sagepub\.com": "SAGE Journals",
            r"pubmed|ncbi\.nlm\.nih\.gov": "PubMed",
            r"scholar\.google": "Google Scholar",
            r"jstor\.org": "JSTOR",
            r"arxiv\.org": "arXiv.org",
            r"muse\.jhu\.edu": "Project MUSE",
            r"nature\.com": "Nature Publishing Group",
            r"pubs\.acs\.org": "ACS Publications",
            r"dl\.acm\.org": "ACM Digital Library",
            r"ieeexplore\.ieee\.org": "IEEE Xplore",
            r"academic\.oup\.com": "Oxford Academic",
            r"cambridge\.org": "Cambridge Core",
            r"highwire|biorxiv|medrxiv": "HighWire 2.0",
            r"biomedcentral\.com": "BioMed Central",
            r"plos\.org|plosone\.org": "PLOS Journals",
            r"frontiersin\.org": "Frontiers",
            r"mdpi\.com": "MDPI",
        }
        
        # Find matching translator name
        matched_name = None
        for pattern, trans_name in url_patterns.items():
            if re.search(pattern, url, re.IGNORECASE):
                matched_name = trans_name
                break
                
        if not matched_name:
            return None
            
        # Search through tiers for the translator
        for tier in sorted(self.translators_by_tier.keys(), key=lambda t: t.value):
            if tier_limit and tier.value > tier_limit.value:
                break
                
            for trans_info in self.translators_by_tier[tier]:
                if trans_info.name == matched_name:
                    return trans_info
                    
        return None
        
    def get_tier_statistics(self) -> Dict:
        """Get statistics about translator coverage by tier."""
        stats = {
            "total_translators": 0,
            "by_tier": {}
        }
        
        for tier, translators in self.translators_by_tier.items():
            count = len(translators)
            stats["total_translators"] += count
            stats["by_tier"][tier.name] = {
                "count": count,
                "translators": [t.name for t in sorted(translators, key=lambda x: x.priority)]
            }
            
        return stats
        
    def run_tiered_extraction(self, url: str, page, max_tier: Optional[TranslatorTier] = None) -> Dict:
        """
        Run translator extraction with tiered priority.
        
        Args:
            url: The URL to extract from
            page: The Playwright page object
            max_tier: Maximum tier to try (inclusive)
            
        Returns:
            Extraction results dictionary
        """
        results = {
            "success": False,
            "translator_used": None,
            "tier": None,
            "urls": [],
            "error": None
        }
        
        # Try to find matching translator
        trans_info = self.get_translator_for_url(url, max_tier)
        
        if not trans_info:
            results["error"] = "No matching translator found"
            return results
            
        logger.info(f"Using {trans_info.tier.name} translator: {trans_info.name}")
        
        # Load and execute the translator
        translator_path = self.translator_dir / trans_info.filename
        
        if not translator_path.exists():
            results["error"] = f"Translator file not found: {trans_info.filename}"
            return results
            
        try:
            # Import the actual runner (would use your existing _ZoteroTranslatorRunner)
            from ._ZoteroTranslatorRunner import ZoteroTranslatorRunner
            
            runner = ZoteroTranslatorRunner()
            urls = runner.extract_urls_pdf_async(page, translator_path)
            
            results["success"] = len(urls) > 0
            results["translator_used"] = trans_info.name
            results["tier"] = trans_info.tier.name
            results["urls"] = urls
            
        except Exception as e:
            results["error"] = str(e)
            logger.error(f"Translator execution failed: {e}")
            
        return results


def demonstrate_tiered_approach():
    """Demonstrate the tiered translator system."""
    manager = TieredZoteroTranslatorManager()
    
    # Show statistics
    stats = manager.get_tier_statistics()
    
    logger.info("Tiered Zotero Translator System")
    logger.info("=" * 60)
    
    for tier_name, tier_data in stats["by_tier"].items():
        logger.info(f"\n{tier_name}: {tier_data['count']} translators")
        for trans in tier_data["translators"][:5]:  # Show first 5
            logger.info(f"  • {trans}")
            
    logger.info(f"\nTotal translators managed: {stats['total_translators']}")
    
    # Test URL matching
    test_urls = [
        "https://www.sciencedirect.com/science/article/pii/S0149763420304668",
        "https://www.nature.com/articles/s41593-018-0209-y",
        "https://ieeexplore.ieee.org/document/1234567",
        "https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2019.00573/full",
        "https://arxiv.org/abs/2101.00001"
    ]
    
    logger.info("\nURL to Translator Matching:")
    logger.info("-" * 40)
    
    for url in test_urls:
        trans_info = manager.get_translator_for_url(url)
        if trans_info:
            logger.success(f"✓ {url[:50]}...")
            logger.info(f"  → {trans_info.tier.name}: {trans_info.name}")
        else:
            logger.warning(f"✗ No translator found for: {url[:50]}...")


if __name__ == "__main__":
    demonstrate_tiered_approach()