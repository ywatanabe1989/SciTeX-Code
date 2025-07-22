#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-11-13 14:30:43 (ywatanabe)"
# File: ./scitex_repo/src/scitex/web/_search_pubmed.py

"""
1. Functionality:
   - Searches PubMed database for scientific articles
   - Retrieves detailed information about matched articles
   - Displays article metadata including title, authors, journal, year, and abstract
2. Input:
   - Search query string (e.g., "epilepsy prediction")
   - Optional parameters for batch size and result limit
3. Output:
   - Formatted article information displayed to stdout
   - BibTeX file with official citations
4. Prerequisites:
   - Internet connection
   - requests package
   - scitex package
"""

"""Imports"""
import argparse
import asyncio
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Union

import aiohttp
import scitex
import pandas as pd
import requests

"""Functions & Classes"""


def _search_pubmed(query: str, retmax: int = 300) -> Dict[str, Any]:
    try:
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        search_url = f"{base_url}esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": retmax,
            "retmode": "json",
            "usehistory": "y",
        }

        response = requests.get(search_url, params=params, timeout=10)
        if not response.ok:
            scitex.str.printc("PubMed API request failed", c="red")
            return {}
        return response.json()
    except requests.exceptions.RequestException as e:
        scitex.str.printc(f"Network error: {e}", c="red")
        return {}


def _fetch_details(
    webenv: str, query_key: str, retstart: int = 0, retmax: int = 100
) -> Dict[str, Any]:
    """Fetches detailed information including abstracts for articles.

    Parameters
    ----------
    [Previous parameters remain the same]

    Returns
    -------
    Dict[str, Any]
        Dictionary containing article details and abstracts
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

    # Fetch abstracts
    efetch_url = f"{base_url}efetch.fcgi"
    efetch_params = {
        "db": "pubmed",
        "query_key": query_key,
        "WebEnv": webenv,
        "retstart": retstart,
        "retmax": retmax,
        "retmode": "xml",
        "rettype": "abstract",
        "field": "abstract,mesh",
    }

    abstract_response = requests.get(efetch_url, params=efetch_params)

    # Fetch metadata
    fetch_url = f"{base_url}esummary.fcgi"
    params = {
        "db": "pubmed",
        "query_key": query_key,
        "WebEnv": webenv,
        "retstart": retstart,
        "retmax": retmax,
        "retmode": "json",
    }

    details_response = requests.get(fetch_url, params=params)

    if not all([abstract_response.ok, details_response.ok]):
        # print(f"Error fetching data")
        return {}

    return {
        "abstracts": abstract_response.text,
        "details": details_response.json(),
    }


def _parse_abstract_xml(xml_text: str) -> Dict[str, tuple]:
    """Parses XML response to extract abstracts.

    Parameters
    ----------
    xml_text : str
        XML response from PubMed

    Returns
    -------
    Dict[str, str]
        Dictionary mapping PMIDs to abstracts
    """
    root = ET.fromstring(xml_text)
    results = {}

    for article in root.findall(".//PubmedArticle"):
        pmid = article.find(".//PMID").text
        abstract_element = article.find(".//Abstract/AbstractText")
        abstract = abstract_element.text if abstract_element is not None else ""

        # DOI
        doi_element = article.find(".//ArticleId[@IdType='doi']")
        doi = doi_element.text if doi_element is not None else ""

        # Get MeSH terms
        keywords = []
        mesh_terms = article.findall(".//MeshHeading/DescriptorName")
        keywords = [term.text for term in mesh_terms if term is not None]

        results[pmid] = (abstract, keywords, doi)

    return results


def _get_citation(pmid: str) -> str:
    """Gets official citation in BibTeX format.

    Parameters
    ----------
    pmid : str
        PubMed ID

    Returns
    -------
    str
        Official BibTeX citation
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    cite_url = f"{base_url}efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": pmid,
        "rettype": "bibtex",
        "retmode": "text",
    }
    response = requests.get(cite_url, params=params)
    return response.text if response.ok else ""


def get_crossref_metrics(doi: str, api_key: Optional[str] = None, email: Optional[str] = None) -> Dict[str, Any]:
    """Get article metrics from CrossRef using DOI."""
    import os
    base_url = "https://api.crossref.org/works/"
    
    # Use provided email or fallback to environment variables
    if not email:
        email = os.getenv("SCITEX_CROSSREF_EMAIL", os.getenv("SCITEX_PUBMED_EMAIL", "research@example.com"))
    headers = {"User-Agent": f"SciTeX/1.0 (mailto:{email})"}
    
    # Add API key as query parameter if provided
    params = {}
    if api_key:
        params['key'] = api_key

    try:
        response = requests.get(f"{base_url}{doi}", headers=headers, params=params, timeout=10)
        if response.ok:
            data = response.json()["message"]
            return {
                "citations": data.get("is-referenced-by-count", 0),
                "type": data.get("type", ""),
                "publisher": data.get("publisher", ""),
                "references": len(data.get("reference", [])),
                "doi": data.get("DOI", ""),
            }
    except Exception as e:
        print(f"CrossRef API error for DOI {doi}: {e}")
    return {}


async def get_crossref_metrics_async(doi: str, api_key: Optional[str] = None, email: Optional[str] = None) -> Dict[str, Any]:
    """Get article metrics from CrossRef using DOI (async version)."""
    import os
    base_url = "https://api.crossref.org/works/"
    
    # Use provided email or fallback to environment variables
    if not email:
        email = os.getenv("SCITEX_CROSSREF_EMAIL", os.getenv("SCITEX_PUBMED_EMAIL", "research@example.com"))
    headers = {"User-Agent": f"SciTeX/1.0 (mailto:{email})"}
    
    # Add API key as query parameter if provided
    params = {}
    if api_key:
        params['key'] = api_key

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}{doi}", headers=headers, params=params, timeout=10) as response:
                if response.ok:
                    data = await response.json()
                    message = data["message"]
                    return {
                        "citations": message.get("is-referenced-by-count", 0),
                        "type": message.get("type", ""),
                        "publisher": message.get("publisher", ""),
                        "references": len(message.get("reference", [])),
                        "doi": message.get("DOI", ""),
                    }
    except Exception as e:
        print(f"CrossRef API error for DOI {doi}: {e}")
    return {}


def save_bibtex(
    papers: Dict[str, Any], abstracts: Dict[str, str], output_file: str
) -> None:
    """Saves paper metadata as BibTeX file with abstracts.

    Parameters
    ----------
    papers : Dict[str, Any]
        Dictionary of paper metadata
    abstracts : Dict[str, str]
        Dictionary of PMIDs to abstracts
    output_file : str
        Output file path
    """
    with open(output_file, "w", encoding="utf-8") as bibtex_file:
        for pmid, paper in papers.items():
            if pmid == "uids":
                continue

            citation = _get_citation(pmid)
            if citation:
                bibtex_file.write(citation)
            else:
                # Use default tuple if pmid not in abstracts
                default_data = ("", [], "")  # abstract, keywords, doi
                bibtex_entry = format_bibtex(
                    paper, pmid, abstracts.get(pmid, default_data)
                )
                bibtex_file.write(bibtex_entry + "\n")
    scitex.str.printc(f"Saved to: {str(bibtex_file)}", c="yellow")


def format_bibtex(paper: Dict[str, Any], pmid: str, abstract_data: tuple) -> str:
    abstract, keywords, doi = abstract_data

    # Get CrossRef and Scimago metrics
    crossref_metrics = get_crossref_metrics(doi) if doi else {}
    journal = paper.get("source", "Unknown Journal")
    # journal_metrics = get_journal_metrics(journal)

    authors = paper.get("authors", [{"name": "Unknown"}])
    author_names = " and ".join(author["name"] for author in authors)
    year = paper.get("pubdate", "").split()[0]
    title = paper.get("title", "No Title")

    # Name formatting
    first_author = authors[0]["name"]
    first_name = first_author.split()[0]
    last_name = first_author.split()[-1]
    clean_first_name = "".join(c for c in first_name if c.isalnum())
    clean_last_name = "".join(c for c in last_name if c.isalnum())

    # Title words
    title_words = title.split()
    first_title_word = "".join(c.lower() for c in title_words[0] if c.isalnum())
    second_title_word = (
        "".join(c.lower() for c in title_words[1] if c.isalnum())
        if len(title_words) > 1
        else ""
    )

    citation_key = f"{clean_first_name}.{clean_last_name}_{year}_{first_title_word}_{second_title_word}"

    entry = f"""@article{{{citation_key},
    author = {{{author_names}}},
    title = {{{title}}},
    journal = {{{journal}}},
    year = {{{year}}},
    pmid = {{{pmid}}},
    doi = {{{doi}}},
    publisher = {{{crossref_metrics.get('publisher', '')}}},
    references = {{{crossref_metrics.get('references', 0)}}},
    keywords = {{{", ".join(keywords)}}},
    abstract = {{{abstract}}}
}}
"""
    return entry


async def fetch_async(
    session: aiohttp.ClientSession, url: str, params: Dict
) -> Union[Dict, str]:
    """Asynchronous fetch helper."""
    async with session.get(url, params=params) as response:
        if response.status == 200:
            if params.get("retmode") == "xml":
                return await response.text()
            elif params.get("retmode") == "json":
                return await response.json()
            return await response.text()
        return {}


async def batch__fetch_details(pmids: List[str], batch_size: int = 20) -> List[Dict]:
    """Fetches details for multiple PMIDs concurrently.

    Parameters
    ----------
    pmids : List[str]
        List of PubMed IDs
    batch_size : int, optional
        Size of each batch for concurrent requests

    Returns
    -------
    List[Dict]
        List of response data
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(0, len(pmids), batch_size):
            batch_pmids = pmids[i : i + batch_size]

            # Fetch both details and citations concurrently
            efetch_params = {
                "db": "pubmed",
                "id": ",".join(batch_pmids),
                "retmode": "xml",
                "rettype": "abstract",
            }

            esummary_params = {
                "db": "pubmed",
                "id": ",".join(batch_pmids),
                "retmode": "json",
            }

            tasks.append(fetch_async(session, f"{base_url}efetch.fcgi", efetch_params))
            tasks.append(
                fetch_async(session, f"{base_url}esummary.fcgi", esummary_params)
            )

        results = await asyncio.gather(*tasks)
        return results


def search_pubmed(query: str, n_entries: int = 10) -> int:
    # query = args.query or "epilepsy prediction"
    # print(f"Using query: {query}")

    search_results = _search_pubmed(query)
    if not search_results:
        # print("No results found or error occurred")
        return 1

    pmids = search_results["esearchresult"]["idlist"]
    count = len(pmids)
    # print(f"Found {count:,} results")

    output_file = f"pubmed_{query.replace(' ', '_')}.bib"
    # print(f"Saving results to: {output_file}")

    # Process in larger batches asynchronously
    results = asyncio.run(batch__fetch_details(pmids[:n_entries]))
    # here, results seems long string

    # Process results and save
    with open(output_file, "w", encoding="utf-8") as f:
        for i in range(0, len(results), 2):
            xml_response = results[i]
            json_response = results[i + 1]

            if isinstance(xml_response, str):
                abstracts = _parse_abstract_xml(xml_response)
                if isinstance(json_response, dict) and "result" in json_response:
                    details = json_response["result"]
                    save_bibtex(details, abstracts, output_file)

    # Process results and save
    temp_bibtex = []
    for i in range(0, len(results), 2):
        xml_response = results[i]
        json_response = results[i + 1]

        if isinstance(xml_response, str):
            abstracts = _parse_abstract_xml(xml_response)
            if isinstance(json_response, dict) and "result" in json_response:
                details = json_response["result"]
                for pmid in details:
                    if pmid != "uids":
                        citation = _get_citation(pmid)
                        if citation:
                            temp_bibtex.append(citation)
                        else:
                            entry = format_bibtex(
                                details[pmid], pmid, abstracts.get(pmid, "")
                            )
                            temp_bibtex.append(entry)

    # Write all entries at once
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(temp_bibtex))

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PubMed article search and retrieval tool"
    )
    parser.add_argument(
        "--query",
        "-q",
        type=str,
        help='Search query (default: "epilepsy prediction")',
    )
    parser.add_argument(
        "--n_entries",
        "-n",
        type=int,
        default=10,
        help='Search query (default: "epilepsy prediction")',
    )
    args = parser.parse_args()
    scitex.str.printc(args, c="yellow")
    return args


def run_main() -> None:
    global CONFIG
    import sys

    import matplotlib.pyplot as plt
    import scitex

    CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(
        sys,
        verbose=False,
    )

    args = parse_args()
    exit_status = search_pubmed(args.query, args.n_entries)

    scitex.gen.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# EOF
