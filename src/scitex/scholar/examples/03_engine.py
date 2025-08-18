#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-18 07:13:59 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/03_engine.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/03_engine.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio
import time
from pprint import pprint

from scitex.scholar import ScholarEngine


async def main_async():
    # Query
    TITLE = "Attention is All You Need"
    DOI = "10.1038/nature14539"

    # Example: Unified Engine
    engine = ScholarEngine(use_cache=False)
    outputs = {}

    # Search by Title
    outputs["metadata_by_title"] = await engine.search_async(
        title=TITLE,
    )

    # Search by DOI
    outputs["metadata_by_doi"] = await engine.search_async(
        doi=DOI,
    )

    for k, v in outputs.items():
        print("----------------------------------------")
        print(k)
        print("----------------------------------------")
        pprint(v)
        time.sleep(1)

    # Semantic_Scholar returned title: Attention is All you Need
    # CrossRef returned title: Is Attention All You Need?
    # OpenAlex returned title: Attention Is All You Need
    # arXiv returned title: Attention Is All You Need
    # WARNING: Semantic Scholar DOI search error: 404 Client Error: Not Found for url: https://api.semanticscholar.org/graph/v1/paper/10.1038/nature14539?fields=title%2Cyear%2Cauthors%2CexternalIds%2Curl%2Cvenue%2Cabstract
    # URL returned title: None
    # CrossRef returned title: Deep learning
    # OpenAlex returned title: Deep learning
    # PubMed returned title: Deep learning
    # ----------------------------------------
    # metadata_by_title
    # ----------------------------------------
    # OrderedDict([('id',
    #               OrderedDict([('doi', '10.48550/arxiv.1706.03762'),
    #                            ('doi_engines', ['OpenAlex']),
    #                            ('arxiv_id', '1706.03762'),
    #                            ('arxiv_id_engines', ['arXiv']),
    #                            ('pmid', None),
    #                            ('pmid_engines', None),
    #                            ('scholar_id', None),
    #                            ('scholar_id_engines', None),
    #                            ('corpus_id', 13756489),
    #                            ('corpus_id_engines', ['Semantic_Scholar'])])),
    #              ('basic',
    #               OrderedDict([('title', 'Attention Is All You Need'),
    #                            ('title_engines', ['OpenAlex', 'arXiv']),
    #                            ('authors',
    #                             ['Ashish Vaswani',
    #                              'Noam Shazeer',
    #                              'Niki Parmar',
    #                              'Jakob Uszkoreit',
    #                              'Llion Jones',
    #                              'Aidan N. Gomez',
    #                              'Łukasz Kaiser',
    #                              'Illia Polosukhin']),
    #                            ('authors_engines', ['OpenAlex']),
    #                            ('year', 2017),
    #                            ('year_engines', ['OpenAlex']),
    #                            ('abstract',
    #                             'The dominant sequence transduction models are '
    #                             'based on complex recurrent or convolutional '
    #                             'neural networks in an encoder-decoder '
    #                             'configuration. The best performing models also '
    #                             'connect the encoder and decoder through an '
    #                             'attention mechanism. We propose a new simple '
    #                             'network architecture, the Transformer, based '
    #                             'solely on attention mechanisms, dispensing with '
    #                             'recurrence and convolutions entirely. Experiments '
    #                             'on two machine translation tasks show these '
    #                             'models to be superior in quality while being more '
    #                             'parallelizable and requiring significantly less '
    #                             'time to train. Our model achieves 28.4 BLEU on '
    #                             'the WMT 2014 English-to-German translation task, '
    #                             'improving over the existing best results, '
    #                             'including ensembles by over 2 BLEU. On the WMT '
    #                             '2014 English-to-French translation task, our '
    #                             'model establishes a new single-model '
    #                             'state-of-the-art BLEU score of 41.8 after '
    #                             'training for 3.5 days on eight GPUs, a small '
    #                             'fraction of the training costs of the best models '
    #                             'from the literature. We show that the Transformer '
    #                             'generalizes well to other tasks by applying it '
    #                             'successfully to English constituency parsing both '
    #                             'with large and limited training data.'),
    #                            ('abstract_engines', ['Semantic_Scholar', 'arXiv']),
    #                            ('keywords', ['BLEU', 'Parallelizable manifold']),
    #                            ('keywords_engines', ['OpenAlex']),
    #                            ('type', 'preprint'),
    #                            ('type_engines', ['OpenAlex'])])),
    #              ('citation_count',
    #               OrderedDict([('total', 60613),
    #                            ('total_engines', ['OpenAlex']),
    #                            ('2025', 4813),
    #                            ('2025_engines', ['OpenAlex']),
    #                            ('2024', 14667),
    #                            ('2024_engines', ['OpenAlex']),
    #                            ('2023', 17061),
    #                            ('2023_engines', ['OpenAlex']),
    #                            ('2022', 9854),
    #                            ('2022_engines', ['OpenAlex']),
    #                            ('2021', 7303),
    #                            ('2021_engines', ['OpenAlex']),
    #                            ('2020', 3895),
    #                            ('2020_engines', ['OpenAlex']),
    #                            ('2019', 2012),
    #                            ('2019_engines', ['OpenAlex']),
    #                            ('2018', 458),
    #                            ('2018_engines', ['OpenAlex']),
    #                            ('2017', 10),
    #                            ('2017_engines', ['OpenAlex']),
    #                            ('2016', 2),
    #                            ('2016_engines', ['OpenAlex']),
    #                            ('2015', None),
    #                            ('2015_engines', None),
    #                            ('2013_engines', ['OpenAlex']),
    #                            ('2013', 1)])),
    #              ('publication',
    #               OrderedDict([('journal', 'arXiv (Cornell University)'),
    #                            ('journal_engines', ['OpenAlex']),
    #                            ('short_journal', None),
    #                            ('short_journal_engines', None),
    #                            ('impact_factor', None),
    #                            ('impact_factor_engines', None),
    #                            ('issn', None),
    #                            ('issn_engines', None),
    #                            ('volume', None),
    #                            ('volume_engines', None),
    #                            ('issue', None),
    #                            ('issue_engines', None),
    #                            ('first_page', None),
    #                            ('first_page_engines', None),
    #                            ('last_page', None),
    #                            ('last_page_engines', None),
    #                            ('publisher', 'Cornell University'),
    #                            ('publisher_engines', ['OpenAlex'])])),
    #              ('url',
    #               OrderedDict([('doi', 'https://doi.org/10.48550/arxiv.1706.03762'),
    #                            ('doi_engines', ['OpenAlex']),
    #                            ('publisher', 'http://arxiv.org/abs/1706.03762v7'),
    #                            ('publisher_engines', ['arXiv']),
    #                            ('openurl_query', None),
    #                            ('openurl_engines', None),
    #                            ('openurl_resolved', []),
    #                            ('openurl_resolved_engines', []),
    #                            ('pdfs', []),
    #                            ('pdfs_engines', []),
    #                            ('supplementary_files', []),
    #                            ('supplementary_files_engines', []),
    #                            ('additional_files', []),
    #                            ('additional_files_engines', [])])),
    #              ('path',
    #               OrderedDict([('pdfs', []),
    #                            ('pdfs_engines', []),
    #                            ('supplementary_files', []),
    #                            ('supplementary_files_engines', []),
    #                            ('additional_files', []),
    #                            ('additional_files_engines', [])])),
    #              ('system',
    #               OrderedDict([('searched_by_arXiv', True),
    #                            ('searched_by_CrossRef', False),
    #                            ('searched_by_OpenAlex', True),
    #                            ('searched_by_PubMed', False),
    #                            ('searched_by_Semantic_Scholar', True),
    #                            ('searched_by_URL', False)]))])
    # ----------------------------------------
    # metadata_by_doi
    # ----------------------------------------
    # OrderedDict([('id',
    #               OrderedDict([('doi', '10.1038/nature14539'),
    #                            ('doi_engines',
    #                             ['URL', 'CrossRef', 'OpenAlex', 'PubMed']),
    #                            ('arxiv_id', None),
    #                            ('arxiv_id_engines', None),
    #                            ('pmid', '26017442'),
    #                            ('pmid_engines', ['OpenAlex', 'PubMed']),
    #                            ('scholar_id', None),
    #                            ('scholar_id_engines', None)])),
    #              ('basic',
    #               OrderedDict([('title', 'Deep learning'),
    #                            ('title_engines',
    #                             ['CrossRef', 'OpenAlex', 'PubMed']),
    #                            ('authors',
    #                             ['Yann LeCun', 'Yoshua Bengio', 'Geoffrey Hinton']),
    #                            ('authors_engines', ['CrossRef', 'PubMed']),
    #                            ('year', 2015),
    #                            ('year_engines', ['CrossRef', 'OpenAlex', 'PubMed']),
    #                            ('abstract',
    #                             'Deep learning allows computational models that '
    #                             'are composed of multiple processing layers to '
    #                             'learn representations of data with multiple '
    #                             'levels of abstraction. These methods have '
    #                             'dramatically improved the state-of-the-art in '
    #                             'speech recognition, visual object recognition, '
    #                             'object detection and many other domains such as '
    #                             'drug discovery and genomics. Deep learning '
    #                             'discovers intricate structure in large data sets '
    #                             'by using the backpropagation algorithm to '
    #                             'indicate how a machine should change its internal '
    #                             'parameters that are used to compute the '
    #                             'representation in each layer from the '
    #                             'representation in the previous layer. Deep '
    #                             'convolutional nets have brought about '
    #                             'breakthroughs in processing images, video, speech '
    #                             'and audio, whereas recurrent nets have shone '
    #                             'light on sequential data such as text and '
    #                             'speech.'),
    #                            ('abstract_engines', ['PubMed']),
    #                            ('keywords',
    #                             ['Abstraction',
    #                              'Representation',
    #                              'Backpropagation',
    #                              'Feature Learning']),
    #                            ('keywords_engines', ['OpenAlex']),
    #                            ('type', 'review'),
    #                            ('type_engines', ['OpenAlex'])])),
    #              ('citation_count',
    #               OrderedDict([('total', 70108),
    #                            ('total_engines', ['OpenAlex']),
    #                            ('2025', 4278),
    #                            ('2025_engines', ['OpenAlex']),
    #                            ('2024', 8754),
    #                            ('2024_engines', ['OpenAlex']),
    #                            ('2023', 9137),
    #                            ('2023_engines', ['OpenAlex']),
    #                            ('2022', 9234),
    #                            ('2022_engines', ['OpenAlex']),
    #                            ('2021', 10149),
    #                            ('2021_engines', ['OpenAlex']),
    #                            ('2020', 9699),
    #                            ('2020_engines', ['OpenAlex']),
    #                            ('2019', 8467),
    #                            ('2019_engines', ['OpenAlex']),
    #                            ('2018', 5708),
    #                            ('2018_engines', ['OpenAlex']),
    #                            ('2017', 3100),
    #                            ('2017_engines', ['OpenAlex']),
    #                            ('2016', 1210),
    #                            ('2016_engines', ['OpenAlex']),
    #                            ('2015', 184),
    #                            ('2015_engines', ['OpenAlex']),
    #                            ('2014_engines', ['OpenAlex']),
    #                            ('2014', 15),
    #                            ('2013_engines', ['OpenAlex']),
    #                            ('2013', 4),
    #                            ('2012_engines', ['OpenAlex']),
    #                            ('2012', 6)])),
    #              ('publication',
    #               OrderedDict([('journal', 'Nature'),
    #                            ('journal_engines', ['CrossRef', 'PubMed']),
    #                            ('short_journal', 'Nature'),
    #                            ('short_journal_engines', ['CrossRef', 'PubMed']),
    #                            ('impact_factor', None),
    #                            ('impact_factor_engines', None),
    #                            ('issn', '0028-0836'),
    #                            ('issn_engines', ['CrossRef']),
    #                            ('volume', '521'),
    #                            ('volume_engines',
    #                             ['CrossRef', 'OpenAlex', 'PubMed']),
    #                            ('issue', '7553'),
    #                            ('issue_engines',
    #                             ['CrossRef', 'OpenAlex', 'PubMed']),
    #                            ('first_page', '436'),
    #                            ('first_page_engines', ['OpenAlex']),
    #                            ('last_page', '444'),
    #                            ('last_page_engines', ['OpenAlex']),
    #                            ('publisher',
    #                             'Springer Science and Business Media LLC'),
    #                            ('publisher_engines', ['CrossRef'])])),
    #              ('url',
    #               OrderedDict([('doi', 'https://doi.org/10.1038/nature14539'),
    #                            ('doi_engines',
    #                             ['URL', 'CrossRef', 'OpenAlex', 'PubMed']),
    #                            ('publisher', 'https://doi.org/10.1038/nature14539'),
    #                            ('publisher_engines', ['OpenAlex']),
    #                            ('openurl_query', None),
    #                            ('openurl_engines', None),
    #                            ('openurl_resolved', []),
    #                            ('openurl_resolved_engines', []),
    #                            ('pdfs', []),
    #                            ('pdfs_engines', []),
    #                            ('supplementary_files', []),
    #                            ('supplementary_files_engines', []),
    #                            ('additional_files', []),
    #                            ('additional_files_engines', [])])),
    #              ('path',
    #               OrderedDict([('pdfs', []),
    #                            ('pdfs_engines', []),
    #                            ('supplementary_files', []),
    #                            ('supplementary_files_engines', []),
    #                            ('additional_files', []),
    #                            ('additional_files_engines', [])])),
    #              ('system',
    #               OrderedDict([('searched_by_arXiv', False),
    #                            ('searched_by_CrossRef', True),
    #                            ('searched_by_OpenAlex', True),
    #                            ('searched_by_PubMed', True),
    #                            ('searched_by_Semantic_Scholar', False),
    #                            ('searched_by_URL', True)]))])


asyncio.run(main_async())

# EOF
