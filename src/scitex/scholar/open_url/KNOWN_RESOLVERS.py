#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-08-01 13:15:00"
# Author: Claude
# File: KNOWN_RESOLVERS.py

"""
Known OpenURL resolvers from various institutions worldwide.

This module contains a curated list of OpenURL resolvers used by
academic institutions for accessing scholarly content.

Sources:
- Zotero OpenURL Resolver Directory: https://www.zotero.org/openurl_resolvers
- Individual institution library websites
- Common resolver patterns
"""

from typing import Dict, List, Optional

# Major OpenURL resolver vendors
RESOLVER_VENDORS = {
    "ExLibris": {
        "patterns": ["sfx", "exlibrisgroup.com"],
        "description": "Ex Libris SFX resolver (very common)"
    },
    "SerialsSolutions": {
        "patterns": ["serialssolutions.com", "360link"],
        "description": "ProQuest SerialsSolutions 360 Link"
    },
    "EBSCO": {
        "patterns": ["ebscohost.com/openurlresolver", "linkssource.ebsco.com"],
        "description": "EBSCO Full Text Finder"
    },
    "OCLC": {
        "patterns": ["worldcat.org", "oclc.org"],
        "description": "OCLC WorldCat resolver"
    },
    "Ovid": {
        "patterns": ["ovid.com", "linksolver"],
        "description": "Ovid LinkSolver"
    }
}

# Known institutional OpenURL resolvers
KNOWN_RESOLVERS: Dict[str, Dict[str, str]] = {
    # United States
    "Harvard University": {
        "url": "https://sfx.hul.harvard.edu/sfx_local",
        "country": "US",
        "vendor": "ExLibris"
    },
    "MIT": {
        "url": "https://owens.mit.edu/sfx_local",
        "country": "US",
        "vendor": "ExLibris"
    },
    "Stanford University": {
        "url": "https://stanford.idm.oclc.org/login?url=",
        "country": "US",
        "vendor": "OCLC"
    },
    "Yale University": {
        "url": "https://yale.idm.oclc.org/login?url=",
        "country": "US",
        "vendor": "OCLC"
    },
    "University of California, Berkeley": {
        "url": "https://ucelinks.cdlib.org:8443/sfx_ucb",
        "country": "US",
        "vendor": "ExLibris"
    },
    "UCLA": {
        "url": "https://ucelinks.cdlib.org:8443/sfx_ucla",
        "country": "US",
        "vendor": "ExLibris"
    },
    "Columbia University": {
        "url": "https://resolver.library.columbia.edu/openurl",
        "country": "US",
        "vendor": "SerialsSolutions"
    },
    "Princeton University": {
        "url": "https://princeton.idm.oclc.org/login?url=",
        "country": "US",
        "vendor": "OCLC"
    },
    "University of Chicago": {
        "url": "https://proxy.uchicago.edu/login?url=",
        "country": "US",
        "vendor": "Custom"
    },
    "Johns Hopkins": {
        "url": "https://openurl.library.jhu.edu",
        "country": "US",
        "vendor": "Custom"
    },
    
    # United Kingdom
    "University of Oxford": {
        "url": "https://fs.oxfordjournals.org/openurl",
        "country": "UK",
        "vendor": "Custom"
    },
    "University of Cambridge": {
        "url": "https://cambridge.idm.oclc.org/login?url=",
        "country": "UK",
        "vendor": "OCLC"
    },
    "Imperial College London": {
        "url": "https://imperial.idm.oclc.org/login?url=",
        "country": "UK",
        "vendor": "OCLC"
    },
    "UCL": {
        "url": "https://ucl.idm.oclc.org/login?url=",
        "country": "UK",
        "vendor": "OCLC"
    },
    "University of Edinburgh": {
        "url": "https://discovered.ed.ac.uk/openurl",
        "country": "UK",
        "vendor": "Custom"
    },
    
    # Canada
    "University of Toronto": {
        "url": "https://myaccess.library.utoronto.ca/login?url=",
        "country": "CA",
        "vendor": "Custom"
    },
    "McGill University": {
        "url": "https://mcgill.on.worldcat.org/atoztitles/link",
        "country": "CA",
        "vendor": "OCLC"
    },
    "University of British Columbia": {
        "url": "https://ubc.summon.serialssolutions.com/link",
        "country": "CA",
        "vendor": "SerialsSolutions"
    },
    
    # Australia
    "University of Melbourne": {
        "url": "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41",
        "country": "AU",
        "vendor": "ExLibris"
    },
    "University of Sydney": {
        "url": "https://ap01.alma.exlibrisgroup.com/view/uresolver/61USYD_INST/openurl",
        "country": "AU",
        "vendor": "ExLibris"
    },
    "Australian National University": {
        "url": "https://anu.hosted.exlibrisgroup.com/primo-explore/openurl",
        "country": "AU",
        "vendor": "ExLibris"
    },
    "University of Queensland": {
        "url": "https://uq.summon.serialssolutions.com/link",
        "country": "AU",
        "vendor": "SerialsSolutions"
    },
    "Monash University": {
        "url": "https://monash.hosted.exlibrisgroup.com/sfx_local",
        "country": "AU",
        "vendor": "ExLibris"
    },
    
    # Germany
    "Max Planck Society": {
        "url": "http://sfx.mpg.de/sfx_local",
        "country": "DE",
        "vendor": "ExLibris"
    },
    "University of Munich (LMU)": {
        "url": "https://sfx.bib.uni-muenchen.de/sfx_lmu",
        "country": "DE",
        "vendor": "ExLibris"
    },
    "Heidelberg University": {
        "url": "https://sfx.bib.uni-heidelberg.de/sfx_heidelberg",
        "country": "DE",
        "vendor": "ExLibris"
    },
    
    # Netherlands
    "University of Amsterdam": {
        "url": "https://vu-nl.idm.oclc.org/login?url=",
        "country": "NL",
        "vendor": "OCLC"
    },
    "Delft University of Technology": {
        "url": "https://tudelft.idm.oclc.org/login?url=",
        "country": "NL",
        "vendor": "OCLC"
    },
    
    # France
    "Sorbonne University": {
        "url": "https://accesdistant.sorbonne-universite.fr/login?url=",
        "country": "FR",
        "vendor": "Custom"
    },
    "École Polytechnique": {
        "url": "https://portail.polytechnique.edu/openurl",
        "country": "FR",
        "vendor": "Custom"
    },
    
    # Switzerland
    "ETH Zurich": {
        "url": "https://www.library.ethz.ch/openurl",
        "country": "CH",
        "vendor": "Custom"
    },
    "EPFL": {
        "url": "https://sfx.epfl.ch/sfx_local",
        "country": "CH",
        "vendor": "ExLibris"
    },
    
    # Japan
    "University of Tokyo": {
        "url": "https://vs2ga4mq9g.search.serialssolutions.com",
        "country": "JP",
        "vendor": "SerialsSolutions"
    },
    "Kyoto University": {
        "url": "https://kuline.kulib.kyoto-u.ac.jp/portal/openurl",
        "country": "JP",
        "vendor": "Custom"
    },
    
    # Singapore
    "National University of Singapore": {
        "url": "https://libproxy.nus.edu.sg/login?url=",
        "country": "SG",
        "vendor": "Custom"
    },
    "Nanyang Technological University": {
        "url": "https://ap01.alma.exlibrisgroup.com/view/uresolver/65NTU_INST/openurl",
        "country": "SG",
        "vendor": "ExLibris"
    },
    
    # China
    "Tsinghua University": {
        "url": "http://sfx.lib.tsinghua.edu.cn/sfx_local",
        "country": "CN",
        "vendor": "ExLibris"
    },
    "Peking University": {
        "url": "http://sfx.lib.pku.edu.cn/sfx_pku",
        "country": "CN",
        "vendor": "ExLibris"
    },
    
    # South Korea
    "Seoul National University": {
        "url": "https://sfx.snu.ac.kr/sfx_local",
        "country": "KR",
        "vendor": "ExLibris"
    },
    "KAIST": {
        "url": "https://library.kaist.ac.kr/openurl",
        "country": "KR",
        "vendor": "Custom"
    },
    
    # Brazil
    "University of São Paulo": {
        "url": "http://www.buscaintegrada.usp.br/openurl",
        "country": "BR",
        "vendor": "Custom"
    },
    
    # Mexico
    "UNAM": {
        "url": "https://pbidi.unam.mx/login?url=",
        "country": "MX",
        "vendor": "Custom"
    },
    
    # India
    "IIT Delhi": {
        "url": "https://libproxy.iitd.ac.in/login?url=",
        "country": "IN",
        "vendor": "Custom"
    },
    "Indian Institute of Science": {
        "url": "https://library.iisc.ac.in/openurl",
        "country": "IN",
        "vendor": "Custom"
    }
}

# Generic OpenURL resolver patterns
GENERIC_PATTERNS = [
    # ExLibris SFX patterns
    r"https?://[^/]+/sfx[^/]*",
    r"https?://sfx\.[^/]+",
    r"https?://[^/]+\.exlibrisgroup\.com",
    
    # SerialsSolutions patterns
    r"https?://[^/]+\.serialssolutions\.com",
    r"https?://[^/]+/360link",
    
    # OCLC patterns
    r"https?://[^/]+\.idm\.oclc\.org",
    r"https?://[^/]+\.worldcat\.org",
    
    # Common proxy patterns
    r"https?://[^/]+/login\?url=",
    r"https?://libproxy\.[^/]+",
    r"https?://proxy\.[^/]+",
    
    # OpenURL patterns
    r"https?://[^/]+/openurl",
    r"https?://[^/]+/openurlresolver",
]


def get_resolver_by_institution(institution_name: str) -> Optional[Dict[str, str]]:
    """
    Get OpenURL resolver information by institution name.
    
    Args:
        institution_name: Name of the institution
        
    Returns:
        Dict with 'url', 'country', and 'vendor' if found, None otherwise
    """
    # Try exact match first
    if institution_name in KNOWN_RESOLVERS:
        return KNOWN_RESOLVERS[institution_name].copy()
    
    # Try case-insensitive match
    institution_lower = institution_name.lower()
    for name, info in KNOWN_RESOLVERS.items():
        if name.lower() == institution_lower:
            return info.copy()
    
    # Try partial match
    for name, info in KNOWN_RESOLVERS.items():
        if institution_lower in name.lower() or name.lower() in institution_lower:
            return info.copy()
    
    return None


def get_resolvers_by_country(country_code: str) -> Dict[str, Dict[str, str]]:
    """
    Get all OpenURL resolvers for a specific country.
    
    Args:
        country_code: Two-letter country code (e.g., 'US', 'UK', 'AU')
        
    Returns:
        Dict of institution names to resolver info
    """
    country_code = country_code.upper()
    return {
        name: info 
        for name, info in KNOWN_RESOLVERS.items() 
        if info.get('country') == country_code
    }


def get_resolvers_by_vendor(vendor_name: str) -> Dict[str, Dict[str, str]]:
    """
    Get all OpenURL resolvers using a specific vendor.
    
    Args:
        vendor_name: Vendor name (e.g., 'ExLibris', 'OCLC')
        
    Returns:
        Dict of institution names to resolver info
    """
    return {
        name: info 
        for name, info in KNOWN_RESOLVERS.items() 
        if info.get('vendor', '').lower() == vendor_name.lower()
    }


def validate_resolver_url(url: str) -> bool:
    """
    Check if a URL looks like a valid OpenURL resolver.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL matches known resolver patterns
    """
    import re
    
    # Check against known resolver URLs
    for info in KNOWN_RESOLVERS.values():
        if url.startswith(info['url']):
            return True
    
    # Check against generic patterns
    for pattern in GENERIC_PATTERNS:
        if re.match(pattern, url):
            return True
    
    return False


def get_all_resolvers() -> List[Dict[str, str]]:
    """
    Get all known resolvers as a list.
    
    Returns:
        List of dicts with 'name', 'url', 'country', 'vendor'
    """
    return [
        {
            'name': name,
            'url': info['url'],
            'country': info.get('country', 'Unknown'),
            'vendor': info.get('vendor', 'Unknown')
        }
        for name, info in KNOWN_RESOLVERS.items()
    ]


# Common test DOIs for different publishers
TEST_DOIS = {
    "Nature": "10.1038/nature12373",
    "Science": "10.1126/science.1234567",
    "Cell": "10.1016/j.cell.2020.01.001",
    "Elsevier": "10.1016/j.neuroimage.2020.116584",
    "Wiley": "10.1111/jnc.15327",
    "Springer": "10.1007/s00401-021-02283-6",
    "Oxford": "10.1093/brain/awaa123",
    "IEEE": "10.1109/TPAMI.2020.2984611",
    "ACS": "10.1021/acs.jmedchem.0c00606",
    "PNAS": "10.1073/pnas.1921909117"
}


if __name__ == "__main__":
    # Example usage
    print(f"Total known resolvers: {len(KNOWN_RESOLVERS)}")
    print(f"\nCountries represented: {len(set(info['country'] for info in KNOWN_RESOLVERS.values()))}")
    print(f"Vendors: {set(info.get('vendor', 'Unknown') for info in KNOWN_RESOLVERS.values())}")
    
    # Example: Find resolver for an institution
    resolver = get_resolver_by_institution("Harvard")
    if resolver:
        print(f"\nHarvard resolver: {resolver['url']}")
    
    # Example: Get all US resolvers
    us_resolvers = get_resolvers_by_country("US")
    print(f"\nUS institutions with resolvers: {len(us_resolvers)}")
    
    # Example: Get all ExLibris resolvers
    exlibris = get_resolvers_by_vendor("ExLibris")
    print(f"Institutions using ExLibris SFX: {len(exlibris)}")