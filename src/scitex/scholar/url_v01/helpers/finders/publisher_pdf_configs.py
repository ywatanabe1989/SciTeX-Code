#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Publisher-specific PDF extraction configurations.

Defines deny patterns, allowed selectors, and other rules for accurately
extracting PDF URLs from different publisher websites.
"""

from typing import Dict, List


class PublisherPDFConfig:
    """Configuration for PDF extraction from specific publishers."""
    
    # Publisher-specific configurations
    CONFIGS = {
        "sciencedirect": {
            "domain_patterns": ["sciencedirect.com", "cell.com", "elsevier.com"],
            "deny_selectors": [
                # Deny supplementary files and figures
                'a[href*="/mmc"]',  # Multimedia components  
                'a[href*="supplementary"]',
                'a[href*="figure"]',
                'a[href*="image"]',
                'a[href*="thumb"]',  # Thumbnails
                'a[href*="gr1"]',    # Graphics
                'a[href*="gr2"]',
                'a[href*="gr3"]',
                'a[href*="fx1"]',    # Supplementary figures
                'a[href*="mmcr"]',   # Multimedia content
                '.recommended-articles a',  # Recommended articles
                '.related-articles a',      # Related articles
                '.reference-list a',         # References
                '.js-related-article a',     # JavaScript loaded related
                '[data-track*="related"]',   # Related content tracking
                '[data-track*="recommend"]', # Recommended content
            ],
            "deny_classes": [
                "thumbnail",
                "figure-download", 
                "supplementary-material",
                "related-article-link",
                "reference-link",
                "recommended-link",
                "ppt-download",  # PowerPoint downloads
                "xls-download",  # Excel downloads
            ],
            "deny_text_patterns": [
                "supplementary",
                "supporting",
                "figure",
                "table",
                "image",
                "cited by",
                "related articles",
                "recommended articles",
                "download all",
                "download zip",
                "powerpoint",
                "excel",
                "video",
                "audio",
            ],
            "allowed_pdf_patterns": [
                # Only allow main article PDFs - be very specific
                r"/pdfft\?",     # Full text PDF endpoint
                r"/piis.*\.pdf", # PII-based PDF URLs
                r"/science/article/pii.*\.pdf",  # Article PDFs
            ],
            "download_selectors": [
                'a[aria-label="Download PDF"]',
                'a.download-pdf-link:not([href*="supplementary"])',
                'button.pdf-download',
                'a[data-track-action="download pdf"]:not([href*="mmc"])'
            ]
        },
        
        "nature": {
            "domain_patterns": ["nature.com"],
            "deny_selectors": [
                'a[href*="figures"]',
                'a[href*="tables"]',
                'a[href*="extended"]',
                '.c-article-references a'
            ],
            "deny_classes": [
                "figure-link",
                "table-link",
                "supplementary-link"
            ],
            "deny_text_patterns": [
                "extended data",
                "supplementary",
                "source data"
            ],
            "allowed_pdf_patterns": [
                r"\.pdf$",
                r"/pdf/"
            ],
            "download_selectors": [
                'a[data-track-action="download pdf"]',
                'a.c-pdf-download__link'
            ]
        },
        
        "wiley": {
            "domain_patterns": ["onlinelibrary.wiley.com"],
            "deny_selectors": [
                'a[href*="supporting"]',
                'a[href*="appendix"]',
                '.article-references a'
            ],
            "deny_classes": [
                "supporting-info",
                "appendix-link"
            ],
            "deny_text_patterns": [
                "supporting information",
                "appendix"
            ],
            "allowed_pdf_patterns": [
                r"/epdf/",
                r"/pdf/",
                r"\.pdf$"
            ],
            "download_selectors": [
                'a[title*="PDF"]',
                'a.pdf-link'
            ]
        },
        
        "springer": {
            "domain_patterns": ["link.springer.com", "springerlink.com"],
            "deny_selectors": [
                'a[href*="supplementary"]',
                'a[href*="figures"]',
                '.c-article-references a'
            ],
            "deny_classes": [
                "supplementary-material",
                "figure-link"
            ],
            "deny_text_patterns": [
                "supplementary",
                "additional file"
            ],
            "allowed_pdf_patterns": [
                r"\.pdf$",
                r"/content/pdf/"
            ],
            "download_selectors": [
                'a.c-pdf-download-link',
                'a[data-track-action="download pdf"]'
            ]
        },
        
        "ieee": {
            "domain_patterns": ["ieeexplore.ieee.org"],
            "deny_selectors": [
                'a[href*="multimedia"]',
                'a[href*="stamp"]'  # Stamp is not the full PDF
            ],
            "deny_classes": [
                "stats-document-abstract-multimedia"
            ],
            "deny_text_patterns": [
                "multimedia",
                "view document"
            ],
            "allowed_pdf_patterns": [
                r"/iel\d+/",  # IEEE Electronic Library
                r"\.pdf$"
            ],
            "download_selectors": [
                'a.pdf-btn-link',
                'xpl-pdf-btn-link'
            ]
        },
        
        "frontiers": {
            "domain_patterns": ["frontiersin.org"],
            "deny_selectors": [
                'a[href*="supplementary"]',
                'a[href*="datasheet"]'
            ],
            "deny_classes": [
                "supplementary-material"
            ],
            "deny_text_patterns": [
                "supplementary",
                "data sheet"
            ],
            "allowed_pdf_patterns": [
                r"/pdf/",
                r"\.pdf$"
            ],
            "download_selectors": [
                'a.download-files-pdf',
                'a[href*="/pdf/"]'
            ]
        },
        
        "plos": {
            "domain_patterns": ["plos.org", "plosone.org"],
            "deny_selectors": [
                'a[href*="supplementary"]',
                'a[href*="figure"]'
            ],
            "deny_classes": [
                "supplementary"
            ],
            "deny_text_patterns": [
                "supporting information"
            ],
            "allowed_pdf_patterns": [
                r"\.pdf$",
                r"/plosone/article/file"
            ],
            "download_selectors": [
                'a#downloadPdf',
                'a[id="downloadPdf"]'
            ]
        },
        
        "default": {
            "domain_patterns": [],
            "deny_selectors": [
                'a[href*="supplementary"]',
                'a[href*="supporting"]',
                'a[href*="figure"]',
                'a[href*="table"]'
            ],
            "deny_classes": [
                "supplementary",
                "figure",
                "table"
            ],
            "deny_text_patterns": [
                "supplementary",
                "supporting",
                "figure",
                "table"
            ],
            "allowed_pdf_patterns": [
                r"\.pdf$",
                r"/pdf/"
            ],
            "download_selectors": [
                'a:has-text("Download PDF")',
                'a[href*=".pdf"]',
                'a[href*="/pdf/"]'
            ]
        }
    }
    
    @classmethod
    def get_config_for_url(cls, url: str) -> Dict:
        """Get the appropriate configuration for a given URL."""
        url_lower = url.lower()
        
        # Check each publisher config
        for publisher, config in cls.CONFIGS.items():
            if publisher == "default":
                continue
                
            for pattern in config.get("domain_patterns", []):
                if pattern in url_lower:
                    return config
        
        # Return default if no match
        return cls.CONFIGS["default"]
    
    @classmethod
    def merge_with_config(cls, url: str, config_deny_selectors: List[str] = None,
                         config_deny_classes: List[str] = None, 
                         config_deny_text_patterns: List[str] = None) -> Dict:
        """
        Merge publisher-specific config with config file deny patterns.
        
        The config file patterns are applied first (base filtering),
        then publisher-specific patterns are added for additional filtering.
        """
        publisher_config = cls.get_config_for_url(url)
        
        # Start with config file patterns
        merged = {
            "deny_selectors": list(config_deny_selectors or []),
            "deny_classes": list(config_deny_classes or []),
            "deny_text_patterns": list(config_deny_text_patterns or []),
            "download_selectors": publisher_config.get("download_selectors", []),
            "allowed_pdf_patterns": publisher_config.get("allowed_pdf_patterns", [])
        }
        
        # Add publisher-specific patterns (these are additional filters)
        merged["deny_selectors"].extend(publisher_config.get("deny_selectors", []))
        merged["deny_classes"].extend(publisher_config.get("deny_classes", []))
        merged["deny_text_patterns"].extend(publisher_config.get("deny_text_patterns", []))
        
        # Remove duplicates while preserving order
        for key in ["deny_selectors", "deny_classes", "deny_text_patterns"]:
            seen = set()
            unique = []
            for item in merged[key]:
                if item not in seen:
                    seen.add(item)
                    unique.append(item)
            merged[key] = unique
        
        return merged
    
    @classmethod
    def is_valid_pdf_url(cls, url: str, pdf_url: str) -> bool:
        """Check if a PDF URL is valid based on publisher rules."""
        import re
        
        config = cls.get_config_for_url(url)
        allowed_patterns = config.get("allowed_pdf_patterns", [])
        
        # Check if URL matches any allowed pattern
        for pattern in allowed_patterns:
            if re.search(pattern, pdf_url):
                return True
        
        return False
    
    @classmethod
    def filter_pdf_urls(cls, page_url: str, pdf_urls: List[str]) -> List[str]:
        """Filter PDF URLs based on publisher-specific rules."""
        import re
        
        config = cls.get_config_for_url(page_url)
        
        # For ScienceDirect, extract the current article's PII from the page URL
        current_pii = None
        if any(domain in page_url.lower() for domain in ["sciencedirect.com", "cell.com", "elsevier.com"]):
            # Extract PII from URL like /pii/S0149763420304668
            pii_match = re.search(r'/pii/([A-Z0-9]+)', page_url)
            if pii_match:
                current_pii = pii_match.group(1)
        
        filtered_urls = []
        for pdf_url in pdf_urls:
            # Check against deny patterns
            should_deny = False
            
            # Check text patterns
            for pattern in config.get("deny_text_patterns", []):
                if pattern.lower() in pdf_url.lower():
                    should_deny = True
                    break
            
            # For ScienceDirect, only allow PDFs matching the current article's PII
            if current_pii:
                # Check if this PDF URL contains the current PII
                if current_pii not in pdf_url:
                    should_deny = True
                # Also deny if it's from a different article (different PII pattern)
                pdf_pii_match = re.search(r'pid=1-s2\.0-([A-Z0-9]+)-', pdf_url)
                if pdf_pii_match:
                    pdf_pii = pdf_pii_match.group(1)
                    if pdf_pii != current_pii:
                        should_deny = True
            
            # If not denied and matches allowed patterns, include it
            if not should_deny and cls.is_valid_pdf_url(page_url, pdf_url):
                filtered_urls.append(pdf_url)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in filtered_urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        return unique_urls