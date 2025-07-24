#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-25 00:06:09 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex_repo/dev.py
# ----------------------------------------
import os
__FILE__ = (
    "./dev.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from scitex.scholar import Scholar, ScholarConfig

# Main Entry
scholar = Scholar()

# # Configuration (optional)
# config = ScholarConfig(
#     semantic_scholar_api_key=os.getenv("SCITEX_SCHOLAR_SEMANTIC_SCHOLAR_API_KEY"),
#     enable_auto_enrich=True,  # Auto-enrich with IF & citations. False for faster search.
#     use_impact_factor_package=True,  # Use real 2024 JCR data
#     default_search_limit=50,
#     pdf_dir="~/.scitex/scholar",  # Where to store PDFs
#     acknowledge_scihub_ethical_usage=False,
# )
# scholar = Scholar(config)

# Papers
papers = scholar.search(
    query="epilepsy detection machine learning",
    limit=10,
    sources=[
        "pubmed"
    ],  # or ["pubmed", "semantic_scholar", "google_scholar", "crossref", "arxiv"]
    year_min=2020,
    year_max=2024,
)
# Searching papers...
# Query: epilepsy detection machine learning
#   Limit: 10
#   Sources: ['pubmed']
#   Year min: 2020
#   Year max: 2024

papers_df = papers.to_dataframe()

print(papers_df.columns)
# Index(['title', 'first_author', 'num_authors', 'year', 'journal',
#        'citation_count', 'citation_count_source', 'impact_factor',
#        'impact_factor_source', 'quartile', 'quartile_source', 'doi', 'pmid',
#        'arxiv_id', 'source', 'has_pdf', 'num_keywords', 'abstract_word_count',
#        'abstract'],
#       dtype='object')

print(papers_df)
#                                                title  ...                                           abstract
# 0                      Ambulatory seizure detection.  ...  To review recent advances in the field of seiz...
# 1               Artificial Intelligence in Epilepsy.  ...  The study of seizure patterns in electroenceph...
# 2  Editorial: Seizure Forecasting and Detection: ...  ...                                                N/A
# 3         Deep learning in neuroimaging of epilepsy.  ...  In recent years, artificial intelligence, part...
# 4  Epileptic Seizure Detection Using Machine Lear...  ...  Epilepsy is a life-threatening neurological br...
# 5  Magnetoencephalography-based approaches to epi...  ...  Epilepsy is a chronic central nervous system d...
# 6  Machine Learning and Artificial Intelligence A...  ...  Machine Learning (ML) and Artificial Intellige...
# 7  An overview of machine learning and deep learn...  ...  Epilepsy is a neurological disorder (the third...
# 8  Artificial intelligence/machine learning for e...  ...  Accurate seizure and epilepsy diagnosis remain...
#
# [9 rows x 19 columns]

# Filtering
filted_papers = papers.filter(min_citations=3)

# Download PDFs
downloaded_papers = scholar.download_pdfs(
    filted_papers
)  # Shows progress with methods being tried

import scitex as stx

# stx.io.save(filted_papers.to_dataframe(), "./downloaded_papers.csv")
# stx.io.save(downloaded_papers.to_dataframe(), "./downloaded_papers.csv")
stx.io.save(filted_papers, "./filted_papers.csv")
stx.io.save(downloaded_papers, "./downloaded_papers.csv")

# EOF
