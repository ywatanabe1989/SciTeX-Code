#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-18 04:49:15 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/06_parse_bibtex.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/06_parse_bibtex.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

def main():
    from pprint import pprint

    from scitex.scholar.utils import parse_bibtex

    # Parameters
    BIBTEX_OPENACCESS = "./data/openaccess.bib"
    BIBTEX_PAYWALLED = "./data/openaccess.bib"

    # OpenAccess
    parsed = parse_bibtex(BIBTEX_OPENACCESS)
    print(f"# of Sample OpenAccess Papers: {len(parsed)}")  # 10
    pprint(parsed[:3])  # 10

    # Paywalled
    parsed = parse_bibtex(BIBTEX_PAYWALLED)
    print(f"# of Sample Paywalled Papers: {len(parsed)}")  # 10
    print(len(parsed))  # 10
    pprint(parsed[:3])  # 10


main()

# INFO: Parsing ./data/openaccess.bib using bibtexparser...
# INFO: Parsed to 10 entries.
# # of Sample OpenAccess Papers: 10
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
# INFO: Parsing ./data/openaccess.bib using bibtexparser...
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
