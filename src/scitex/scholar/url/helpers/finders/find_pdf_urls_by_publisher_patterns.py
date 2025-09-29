#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-19 12:00:17 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/url/helpers/finders/find_pdf_urls_by_publisher_patterns.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/url/helpers/finders/find_pdf_urls_by_publisher_patterns.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import re
from typing import List

from scitex import logging

logger = logging.getLogger(__name__)


def find_pdf_urls_by_publisher_patterns(page, url: str) -> List[str]:
    """Generate PDF URLs based on publisher patterns."""

    urls_pdf = []

    # Nature
    if "nature.com" in url and not url.endswith(".pdf"):
        urls_pdf.append(url.rstrip("/") + ".pdf")

    # Science
    elif "science.org" in url and "/doi/10." in url and "/pdf/" not in url:
        urls_pdf.append(url.replace("/doi/", "/doi/pdf/"))

    # Elsevier/ScienceDirect
    elif "sciencedirect.com" in url and "/pii/" in url:
        pii = url.split("/pii/")[-1].split("/")[0].split("?")[0]
        urls_pdf.append(
            f"https://www.sciencedirect.com/science/article/pii/{pii}/pdfft"
        )

    # Wiley
    elif "wiley.com" in url and "/doi/" in url and "/pdfdirect" not in url:
        urls_pdf.append(url.replace("/doi/", "/doi/pdfdirect/"))

    # Frontiers
    elif "frontiersin.org" in url and "/full" in url:
        urls_pdf.append(url.replace("/full", "/pdf"))

    # Springer
    elif (
        "springer.com" in url or "link.springer.com" in url
    ) and "/article/" in url:
        if not url.endswith(".pdf"):
            urls_pdf.append(url.rstrip("/") + ".pdf")

    # IEEE
    elif "ieee.org" in url and "/document/" in url:
        doc_id = url.split("/document/")[-1].split("/")[0]
        urls_pdf.append(
            f"https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber={doc_id}"
        )

    # MDPI
    elif "mdpi.com" in url and "/htm" in url:
        urls_pdf.append(url.replace("/htm", "/pdf"))

    # BMC
    elif "biomedcentral.com" in url and "/articles/" in url:
        urls_pdf.append(url.replace("/articles/", "/track/pdf/"))

    # PLOS
    elif "plos.org" in url and "/article" in url:
        if "?id=" in url:
            article_id = url.split("?id=")[-1].split("&")[0]
            base_url = url.split("/article")[0]
            urls_pdf.append(
                f"{base_url}/article/file?id={article_id}&type=printable"
            )
        elif "/article/" in url:
            urls_pdf.append(
                url.replace("/article/", "/article/file?id=").split("?")[0]
                + "&type=printable"
            )

    # Journal of Neuroscience
    if "jneurosci.org" in url and "/content/" in url:
        # Extract volume/issue/page numbers
        match = re.search(r"/content/(\d+)/(\d+)/(\d+)", url)
        if match:
            vol, issue, page = match.groups()
            urls_pdf.append(
                f"https://www.jneurosci.org/content/jneuro/{vol}/{issue}/{page}.full.pdf"
            )

    # eNeuro
    elif "eneuro.org" in url and "/content/" in url:
        # Pattern: /content/3/6/ENEURO.0334-16.2016
        match = re.search(r"/content/[^/]+/[^/]+/(ENEURO\.[^/]+)", url)
        if match:
            eneuro_id = match.group(1)
            urls_pdf.append(
                f"https://www.eneuro.org/content/eneuro/early/recent/{eneuro_id}.full.pdf"
            )

    # Oxford Academic
    elif "academic.oup.com" in url:
        urls_pdf.append(url.replace("/article/", "/article-pdf/"))

    # Improve preprint handling
    elif "biorxiv.org" in url or "medrxiv.org" in url:
        # Handle versioned URLs better
        if "/v" in url:  # e.g., /v1, /v2
            base_url = url.split("/v")[0]
            urls_pdf.append(f"{base_url}.full.pdf")
        else:
            urls_pdf.append(url + ".full.pdf")

    elif "arxiv.org" in url:
        if "/abs/" in url:
            arxiv_id = url.split("/abs/")[-1]
            urls_pdf.append(f"https://arxiv.org/pdf/{arxiv_id}.pdf")

    if len(urls_pdf) > 0:
        logger.success(
            f"Publisher-specific pattern matching found {len(urls_pdf)} PDF URLs from {url}"
        )
    else:
        logger.warning(
            f"Publisher-specific patterns did not match any PDF URLs from {url}"
        )

    return urls_pdf

# EOF
