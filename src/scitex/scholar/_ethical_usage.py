#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-23 17:17:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/_ethical_usage.py
# ----------------------------------------
import os
__FILE__ = (
    "./src/scitex/scholar/_ethical_usage.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Ethical usage guidelines for Sci-Hub integration.

This module contains the ethical usage text and functions to display it.
"""

ETHICAL_USAGE_NOTICE = """
⚖️  SCI-HUB USAGE NOTICE (PDF Download Only)

IMPORTANT: This notice applies ONLY to the Sci-Hub PDF download feature.
All other SciTeX Scholar features (search, enrichment, citation tracking) are completely legitimate.

The Sci-Hub integration is designed to help researchers access papers through various channels.
Please use this specific feature responsibly and in accordance with your local laws and institutional policies.

✅ Appropriate Uses:
- Open access papers with broken download links
- Papers you have legitimate institutional access to
- Your own published work
- Publicly funded research
- Papers with Creative Commons licenses
- Educational/research purposes with proper authorization

❌ Please Don't Use For:
- Recently published commercial papers under active copyright
- Papers you don't have legitimate access to
- Bulk downloading of entire journal collections
- Commercial redistribution
- Violating publisher terms of service

📚 Alternative Legal Access Methods:
1. Institutional Access
2. Open Access Repositories (PubMed Central, arXiv, bioRxiv)
3. Author Websites
4. ResearchGate/Academia.edu
5. Library Services
6. Contact Authors Directly
7. Unpaywall Browser Extension

See docs/SCIHUB_ETHICAL_USAGE.md for complete guidelines.
"""

ETHICAL_USAGE_FULL = """
# Sci-Hub PDF Download - Ethical Usage Guidelines

## ⚠️ IMPORTANT: This Only Applies to Sci-Hub PDF Downloads

**SciTeX Scholar is a completely legitimate research tool.** All features including:
- ✅ Literature search (PubMed, arXiv, Semantic Scholar)
- ✅ Impact factor enrichment
- ✅ Citation tracking
- ✅ BibTeX management
- ✅ Local PDF indexing

...are 100% ethical and legal.

## ⚖️ Sci-Hub Integration Notice

The Sci-Hub PDF download feature is an optional tool designed to help researchers access papers. 
This specific feature should be used responsibly and in accordance with your local laws and institutional policies.

### ✅ Appropriate Uses:
- **Open access papers** with broken download links on publisher sites
- **Papers you have legitimate institutional access to** when official sites are down
- **Your own published work** when you can't access it through normal channels
- **Publicly funded research** that should be freely available
- **Papers with Creative Commons or similar open licenses**
- **Educational purposes** in accordance with fair use policies
- **Research purposes** where you have proper authorization

### ❌ Please Don't Use For:
- Recently published commercial papers under active copyright
- Papers you don't have legitimate access to
- Bulk downloading of entire journal collections
- Commercial redistribution
- Violating publisher terms of service
- Circumventing paywalls for commercial gain

## 📚 Alternative Legal Access Methods

Before using this tool, consider these legitimate alternatives:

1. **Institutional Access**: Check if your university/organization provides access
2. **Open Access Repositories**: 
   - PubMed Central
   - arXiv
   - bioRxiv
   - PLOS ONE
   - Directory of Open Access Journals (DOAJ)
3. **Author Websites**: Many authors post preprints on personal pages
4. **ResearchGate/Academia.edu**: Authors often share their work
5. **Library Services**: Inter-library loan programs
6. **Contact Authors Directly**: Most researchers are happy to share their work
7. **Unpaywall Browser Extension**: Finds legal open access versions

## 🔒 Privacy and Security

- This tool uses Selenium with headless Chrome
- Your searches may be visible to third-party services
- Use institutional VPNs when appropriate
- Be aware of your organization's policies

## 📝 Legal Disclaimer

This tool is provided for educational and research purposes only. Users are responsible for ensuring their use complies with all applicable laws, regulations, and institutional policies. The developers do not endorse or encourage any illegal activity.

## 🤝 Responsible Research

Support open science by:
- Publishing in open access journals when possible
- Depositing preprints in repositories
- Advocating for fair access to publicly funded research
- Respecting the work of publishers who add value
- Supporting sustainable academic publishing models

---

*Remember: The goal is to advance human knowledge while respecting intellectual property rights and supporting sustainable academic publishing.*
"""


def get_ethical_usage_notice(full: bool = False) -> str:
    """
    Get the ethical usage notice text.
    
    Args:
        full: If True, return the complete guidelines. If False, return the brief notice.
        
    Returns:
        The ethical usage text.
    """
    return ETHICAL_USAGE_FULL if full else ETHICAL_USAGE_NOTICE


def display_ethical_usage(full: bool = False) -> None:
    """
    Display the ethical usage notice.
    
    Args:
        full: If True, display the complete guidelines. If False, display the brief notice.
    """
    print(get_ethical_usage_notice(full))


def check_ethical_usage(acknowledged: bool = None) -> bool:
    """
    Check if ethical usage has been acknowledged.
    
    Args:
        acknowledged: If provided, sets the acknowledgment status. If None, prompts user.
        
    Returns:
        True if acknowledged, False otherwise.
    """
    if acknowledged is not None:
        return acknowledged
        
    # In automated environments, return False by default
    import sys
    if not sys.stdin.isatty():
        return False
        
    print(ETHICAL_USAGE_NOTICE)
    response = input("\nDo you acknowledge and agree to use this feature ethically? (yes/no): ")
    return response.lower() in ['yes', 'y']


# Alias for backward compatibility
ETHICAL_USAGE_MESSAGE = ETHICAL_USAGE_NOTICE


# EOF