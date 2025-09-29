#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-21 22:02:15 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/06_parse_bibtex.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/06_parse_bibtex.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Functionalities:
- Demonstrates BibTeX parsing utilities in Scholar module
- Shows parsing of different BibTeX file formats (openaccess, paywalled)
- Validates BibTeX entry structure and field extraction
- Displays sample entries with detailed metadata

Dependencies:
- scripts:
  - None
- packages:
  - scitex

Input:
- ./data/scholar/openaccess.bib
- ./data/scholar/paywalled.bib

Output:
- Console output showing parsed BibTeX entries
- Sample entries with authors, titles, journals, and metadata
"""

"""Imports"""
import argparse
from pprint import pprint

import scitex as stx

"""Warnings"""

"""Parameters"""

"""Functions & Classes"""
def demonstrate_bibtex_parsing(
    openaccess_path: str = "./data/scholar/openaccess.bib",
    paywalled_path: str = "./data/scholar/paywalled.bib",
    n_samples: int = 3
) -> dict:
    """Demonstrate BibTeX parsing capabilities.
    
    Parameters
    ----------
    openaccess_path : str, default="./data/scholar/openaccess.bib"
        Path to openaccess BibTeX file
    paywalled_path : str, default="./data/scholar/paywalled.bib"
        Path to paywalled BibTeX file
    n_samples : int, default=3
        Number of sample entries to display
        
    Returns
    -------
    dict
        Parsed BibTeX entries
    """
    from scitex.scholar.utils import parse_bibtex

    results = {}
    
    print(f"📚 Parsing OpenAccess BibTeX file: {openaccess_path}")
    openaccess_parsed = parse_bibtex(openaccess_path)
    print(f"📊 Found {len(openaccess_parsed)} OpenAccess papers")
    
    print(f"\n📋 Sample OpenAccess entries (first {n_samples}):")
    print("=" * 50)
    pprint(openaccess_parsed[:n_samples])
    
    print(f"\n📚 Parsing Paywalled BibTeX file: {paywalled_path}")
    paywalled_parsed = parse_bibtex(paywalled_path)
    print(f"📊 Found {len(paywalled_parsed)} Paywalled papers")
    
    print(f"\n📋 Sample Paywalled entries (first {n_samples}):")
    print("=" * 50)
    pprint(paywalled_parsed[:n_samples])
    
    results = {
        "openaccess": openaccess_parsed,
        "paywalled": paywalled_parsed
    }
    
    return results


def main(args) -> int:
    """Main function to demonstrate BibTeX parsing.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments

    Returns
    -------
    int
        Exit status code (0 for success, 1 for failure)
    """
    print("📚 Scholar BibTeX Parser Demonstration")
    print("=" * 40)
    
    try:
        results = demonstrate_bibtex_parsing(
            openaccess_path=args.openaccess_path,
            paywalled_path=args.paywalled_path,
            n_samples=args.n_samples
        )
        
        total_entries = len(results["openaccess"]) + len(results["paywalled"])
        print(f"\n✅ Successfully parsed {total_entries} total BibTeX entries")
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Demonstrate Scholar BibTeX parsing utilities"
    )
    parser.add_argument(
        "--openaccess_path",
        "-oa",
        type=str,
        default="./data/scholar/openaccess.bib",
        help="Path to openaccess BibTeX file (default: %(default)s)",
    )
    parser.add_argument(
        "--paywalled_path",
        "-pw",
        type=str,
        default="./data/scholar/paywalled.bib",
        help="Path to paywalled BibTeX file (default: %(default)s)",
    )
    parser.add_argument(
        "--n_samples",
        "-n",
        type=int,
        default=3,
        help="Number of sample entries to display (default: %(default)s)",
    )
    args = parser.parse_args()
    stx.str.printc(args, c="yellow")
    return args


def run_main() -> None:
    """Initialize scitex framework, run main function, and cleanup."""
    global CONFIG, CC, sys, plt

    import sys

    import matplotlib.pyplot as plt

    args = parse_args()

    CONFIG, sys.stdout, sys.stderr, plt, CC = stx.session.start(
        sys,
        plt,
        args=args,
        file=__FILE__,
        verbose=False,
        agg=True,
    )

    exit_status = main(args)

    stx.session.close(
        CONFIG,
        verbose=False,
        notify=False,
        message="",
        exit_status=exit_status,
    )


if __name__ == "__main__":
    run_main()

# EOF
# [{'ENTRYTYPE': 'article',
#   'ID': 'Hlsemann2019QuantificationOPA',
#   'author': 'Mareike J. H{\\"u}lsemann and E. Naumann and B. Rasch',
#   'journal': 'Frontiers in Neuroscience',
#   'title': 'Quantification of Phase-Amplitude Coupling in Neuronal '
#            'Oscillations: Comparison of Phase-Locking Value, Mean Vector '
#            'Length, Modulation Index, and '
#            'Generalized-Linear-Modeling-Cross-Frequency-Coupling',
#   'url': 'https://www.ncbi.nlm.nih.gov/pubmed/31275096',
#   'volume': '13',
#   'year': '2019'},
#  {'ENTRYTYPE': 'article',
#   'ID': 'Munia2019TimeFrequencyBPK',
#   'author': 'T. T. Munia and Selin Aviyente',
#   'journal': 'Scientific Reports',
#   'title': 'Time-Frequency Based Phase-Amplitude Coupling Measure For Neuronal '
#            'Oscillations',
#   'url': 'https://api.semanticscholar.org/CorpusID:201651743',
#   'volume': '9',
#   'year': '2019'},
#  {'ENTRYTYPE': 'article',
#   'ID': 'Voytek2010ShiftsIGV',
#   'author': 'Bradley Voytek and R. Canolty and A. Shestyuk and N. Crone and J. '
#             'Parvizi and R. Knight',
#   'journal': 'Frontiers in Human Neuroscience',
#   'title': 'Shifts in Gamma Phase–Amplitude Coupling Frequency from Theta to '
#            'Alpha Over Posterior Cortex During Visual Tasks',
#   'url': 'https://api.semanticscholar.org/CorpusID:7724159',
#   'volume': '4',
#   'year': '2010'}]
# INFO: Parsing ./data/scholar/openaccess.bib using bibtexparser...
# INFO: Parsed to 10 entries.
# # of Sample Paywalled Papers: 10
# 10
# [{'ENTRYTYPE': 'article',
#   'ID': 'Hlsemann2019QuantificationOPA',
#   'author': 'Mareike J. H{\\"u}lsemann and E. Naumann and B. Rasch',
#   'journal': 'Frontiers in Neuroscience',
#   'title': 'Quantification of Phase-Amplitude Coupling in Neuronal '
#            'Oscillations: Comparison of Phase-Locking Value, Mean Vector '
#            'Length, Modulation Index, and '
#            'Generalized-Linear-Modeling-Cross-Frequency-Coupling',
#   'url': 'https://www.ncbi.nlm.nih.gov/pubmed/31275096',
#   'volume': '13',
#   'year': '2019'},
#  {'ENTRYTYPE': 'article',
#   'ID': 'Munia2019TimeFrequencyBPK',
#   'author': 'T. T. Munia and Selin Aviyente',
#   'journal': 'Scientific Reports',
#   'title': 'Time-Frequency Based Phase-Amplitude Coupling Measure For Neuronal '
#            'Oscillations',
#   'url': 'https://api.semanticscholar.org/CorpusID:201651743',
#   'volume': '9',
#   'year': '2019'},
#  {'ENTRYTYPE': 'article',
#   'ID': 'Voytek2010ShiftsIGV',
#   'author': 'Bradley Voytek and R. Canolty and A. Shestyuk and N. Crone and J. '
#             'Parvizi and R. Knight',
#   'journal': 'Frontiers in Human Neuroscience',
#   'title': 'Shifts in Gamma Phase–Amplitude Coupling Frequency from Theta to '
#            'Alpha Over Posterior Cortex During Visual Tasks',
#   'url': 'https://api.semanticscholar.org/CorpusID:7724159',
#   'volume': '4',
#   'year': '2010'}]

# EOF
