#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-18 16:22:54 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/99_fullpipeline-for-bibtex.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/scitex/scholar/examples/99_fullpipeline-for-bibtex.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import asyncio


async def main_async():
    from pathlib import Path
    from pprint import pprint

    import numpy as np

    from scitex.scholar import (
        ScholarAuthManager,
        ScholarBrowserManager,
        ScholarConfig,
        ScholarEngine,
        ScholarPDFDownloader,
        ScholarURLFinder,
    )
    from scitex.scholar.utils import parse_bibtex

    # Parameters
    USE_CACHE = True
    N_SAMPLES = None
    BROWSER_MODE = ["interactive", "stealth"][1]

    # Data
    BIBTEX_OPENACCESS = "./data/openaccess.bib"
    BIBTEX_PAYWALLED = "./data/paywalled.bib"
    BIBTEX_PAC = "./data/papers.bib"
    ENTRIES = parse_bibtex(BIBTEX_PAC)
    ENTRIES = np.random.permutation(ENTRIES)[:N_SAMPLES].tolist()
    QUERY_TITLES = [entry.get("title") for entry in ENTRIES]
    pprint(QUERY_TITLES)

    # Config
    config = ScholarConfig()

    # Initialize browser with authentication
    browser_manager = ScholarBrowserManager(
        chrome_profile_name="system",
        browser_mode=BROWSER_MODE,
        auth_manager=ScholarAuthManager(config=config),
        config=config,
    )
    browser, context = (
        await browser_manager.get_authenticated_browser_and_context_async()
    )

    # Initialize components
    engine = ScholarEngine(config=config, use_cache=USE_CACHE)
    url_finder = ScholarURLFinder(
        context,
        config=config,
        use_cache=False,
    )
    # pdf_downloader = ScholarPDFDownloader(context, config=config)

    # 1. Search for metadata
    print("----------------------------------------")
    print("1. Searching for metadata...")
    print("----------------------------------------")
    batched_metadata = await engine.search_batch_async(titles=QUERY_TITLES)
    pprint(batched_metadata)

    # 2. Find URLs
    print("----------------------------------------")
    print("2. Finding URLs...")
    print("----------------------------------------")
    dois = [
        metadata.get("id", {}).get("doi")
        for metadata in batched_metadata
        if metadata and metadata.get("id")
    ]
    batched_urls = await url_finder.find_urls_batch(dois=dois)
    __import__("ipdb").set_trace()
    # pprint(batched_urls)

    # 3. Download PDFs
    print("----------------------------------------")
    print("3. Downloading PDFs...")
    print("----------------------------------------")

    batched_urls_pdf = [
        url_and_source["url"]
        for urls in batched_urls
        for url_and_source in urls.get("urls_pdf", [])
    ]

    downloaded_paths = []
    for idx_url, pdf_url in enumerate(batched_urls_pdf):
        output_path = (
            Path("/tmp/scholar_pipeline") / f"paper_{idx_url:02d}.pdf"
        )
        print(pdf_url)
        if pdf_url:

            # # This fails; I think the shared context between url_finder and pdf_downloader might cause problem
            # browser_manager = ScholarBrowserManager(
            #     chrome_profile_name="system",
            #     browser_mode=BROWSER_MODE,
            #     auth_manager=ScholarAuthManager(config=config),
            #     config=config,
            # )
            # browser, context = (
            #     await browser_manager.get_authenticated_browser_and_context_async()
            # )

            pdf_downloader = ScholarPDFDownloader(context, config=config)
            is_downloaded = await pdf_downloader.download_from_url(
                pdf_url, output_path
            )
            if is_downloaded:
                downloaded_paths.append(output_path)


asyncio.run(main_async())

# (.env-3.11) (wsl) scholar $ /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/99_fullpipeline-for-bibtex.py
# INFO: Parsing ./data/openaccess.bib using bibtexparser...
# INFO: Parsed to 10 entries.
# INFO: Parsing ./data/openaccess.bib using bibtexparser...
# INFO: Parsed to 10 entries.
# ['The Detection of Phase Amplitude Coupling during Sensory Processing',
#  'Theta-gamma phase amplitude coupling in a hippocampal CA1 microcircuit',
#  'Phase–Amplitude Coupling, Mental Health and Cognition: Implications for '
#  'Adolescence',
#  'Tensorpac: An open-source Python toolbox for tensor-based phase-amplitude '
#  'coupling measurement in electrophysiological brain signals',
#  'Quantification of Phase-Amplitude Coupling in Neuronal Oscillations: '
#  'Comparison of Phase-Locking Value, Mean Vector Length, Modulation Index, and '
#  'Generalized-Linear-Modeling-Cross-Frequency-Coupling',
#  'A Canonical Circuit for Generating Phase-Amplitude Coupling',
#  'Phase–Amplitude Coupling, Mental Health and Cognition: Implications for '
#  'Adolescence',
#  'Cross-frequency coupling within and between the human thalamus and neocortex',
#  'A Canonical Circuit for Generating Phase-Amplitude Coupling',
#  'Tensorpac: An open-source Python toolbox for tensor-based phase-amplitude '
#  'coupling measurement in electrophysiological brain signals',
#  'Cross-frequency coupling within and between the human thalamus and neocortex',
#  'Quantification of Phase-Amplitude Coupling in Neuronal Oscillations: '
#  'Comparison of Phase-Locking Value, Mean Vector Length, Modulation Index, and '
#  'Generalized-Linear-Modeling-Cross-Frequency-Coupling',
#  'Time-Frequency Based Phase-Amplitude Coupling Measure For Neuronal '
#  'Oscillations',
#  'The Detection of Phase Amplitude Coupling during Sensory Processing',
#  'Topology, Cross-Frequency, and Same-Frequency Band Interactions Shape the '
#  'Generation of Phase-Amplitude Coupling in a Neural Mass Model of a Cortical '
#  'Column',
#  'Theta-gamma phase amplitude coupling in a hippocampal CA1 microcircuit',
#  'Topology, Cross-Frequency, and Same-Frequency Band Interactions Shape the '
#  'Generation of Phase-Amplitude Coupling in a Neural Mass Model of a Cortical '
#  'Column',
#  'Time-Frequency Based Phase-Amplitude Coupling Measure For Neuronal '
#  'Oscillations',
#  'Shifts in Gamma Phase–Amplitude Coupling Frequency from Theta to Alpha Over '
#  'Posterior Cortex During Visual Tasks']
# INFO: ScholarConfig object configured with: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/config/default.yaml
# INFO: scholar_dir resolved as /home/ywatanabe/.scitex/
# INFO: openathens_email resolved as Yusuke.Watanabe@unimelb.edu.au
# INFO: debug_mode resolved as True
# INFO: openathens_email resolved as Yusuke.Watanabe@unimelb.edu.au
# INFO: sso_username resolved as yusukew
# INFO: sso_password resolved as ZA****************************Qv
# INFO: ScholarConfig object configured with: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/config/default.yaml
# INFO: scholar_dir resolved as /home/ywatanabe/.scitex/
# INFO: sso_username resolved as yusukew
# INFO: sso_password resolved as ZA****************************Qv
# INFO: from_email_address resolved as agent@scitex.ai
# INFO: from_email_password resolved as Wl****************************zC
# INFO: from_email_smtp_server resolved as mail1030.onamae.ne.jp
# INFO: from_email_smtp_port resolved as 587
# INFO: from_email_sender_mail resolved as SciTeX Scholar
# INFO: to_email_address resolved as ywata1989@gmail.com
# INFO: Registered authentication provider: openathens
# INFO: browser_mode resolved as stealth
# INFO: Browser initialized:
# INFO: headless: False
# INFO: spoof_dimension: True
# INFO: viewport_size: (1920, 1080)
# SUCCESS: Loaded session from cache (/home/ywatanabe/.scitex/scholar/cache/auth/openathens.json): 14 cookies (expires in 4h 28m)
# SUCCESS: Verified live authentication at https://my.openathens.net/account
# SUCCESS: Zotero Connector (ekhagklcjbdpajgpjgmbionohlpdbjgc) is installed
# SUCCESS: Lean Library (hghakoefmnkhamdhenpbogkeopjlkpoa) is installed
# SUCCESS: Pop-up Blocker (bkkbcggnhapdmkeljlodobbkopceiche) is installed
# SUCCESS: Accept all cookies (ofpnikijgfhlmmjlpkfaifhhdonchhoi) is installed
# SUCCESS: 2Captcha Solver (ifibfemgeogfhoebkmokieepdoobkbpo) is installed
# SUCCESS: CAPTCHA Solver (hlifkpholllijblknnmbfagnkjneagid) is installed
# SUCCESS: All 6/6 extensions installed
# SUCCESS: Xvfb display :99 is running
# INFO: Invisible mode: Window set to 1x1 at position 0,0 (off-screen)
# INFO: Browser window configuration: Invisible (1x1)
# INFO: Loading 6 extensions from /home/ywatanabe/.scitex/scholar/cache/chrome/system
# INFO: Stealth window args: ['--window-size=1,1', '--window-position=0,0', '--window-size=1920,1080']
# INFO: Closed unwanted page: chrome-extension://ifibfemgeogfhoebkmokieepdoobkbpo/options/options.html
# INFO: Closed unwanted page: chrome-extension://hghakoefmnkhamdhenpbogkeopjlkpoa/options.html
# INFO: Closed unwanted page: https://app.pbapi.xyz/dashboard?originSource=EXTENSION&onboarding=1
# INFO: Extension cleanup completed
# INFO: stealth_manager.get_dimension_spoofing_script called.
# INFO: Filtered to 4 essential cookies for openathens
# SUCCESS: Loaded 4 authentication cookies into persistent browser context
# SUCCESS: Using persistent context with profile and extensions
# INFO: engines resolved as ['URL', 'Semantic_Scholar', 'CrossRef', 'OpenAlex', 'PubMed', 'arXiv']
# INFO: use_cache_search resolved as False
# INFO: openurl_resolver_url resolved as https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# INFO: use_cache_url_finder resolved as False
# 1. Searching for metadata...
# INFO: Extension cleanup completed
# Semantic_Scholar returned title: The Detection of Phase Amplitude Coupling during Sensory Processing
# CrossRef returned title: The Detection of Phase Amplitude Coupling During Sensory Processing
# OpenAlex returned title: The Detection of Phase Amplitude Coupling during Sensory Processing
# PubMed returned title: The Detection of Phase Amplitude Coupling during Sensory Processing
# Semantic_Scholar returned title: Theta-gamma phase amplitude coupling in a hippocampal CA1 microcircuit
# CrossRef returned title: Theta-gamma phase amplitude coupling in a hippocampal CA1 microcircuit
# OpenAlex returned title: Theta-gamma phase amplitude coupling in a hippocampal CA1 microcircuit
# Semantic_Scholar returned title: Phase–Amplitude Coupling, Mental Health and Cognition: Implications for Adolescence
# CrossRef returned title: Phase–Amplitude Coupling, Mental Health and Cognition: Implications for Adolescence
# OpenAlex returned title: Phase–Amplitude Coupling, Mental Health and Cognition: Implications for Adolescence
# Semantic_Scholar returned title: Tensorpac: An open-source Python toolbox for tensor-based phase-amplitude coupling measurement in electrophysiological brain signals
# CrossRef returned title: Tensorpac : an open-source Python toolbox for tensor-based Phase-Amplitude Coupling measurement in electrophysiological brain signals
# OpenAlex returned title: Tensorpac: An open-source Python toolbox for tensor-based phase-amplitude coupling measurement in electrophysiological brain signals
# PubMed returned title: Tensorpac: An open-source Python toolbox for tensor-based phase-amplitude coupling measurement in electrophysiological brain signals
# Semantic_Scholar returned title: Quantification of Phase-Amplitude Coupling in Neuronal Oscillations: Comparison of Phase-Locking Value, Mean Vector Length, Modulation Index, and Generalized-Linear-Modeling-Cross-Frequency-Coupling
# CrossRef returned title: Quantification of Phase-Amplitude Coupling in Neuronal Oscillations: Comparison of Phase-Locking Value, Mean Vector Length, Modulation Index, and Generalized-Linear-Modeling-Cross-Frequency-Coupling
# OpenAlex returned title: Quantification of Phase-Amplitude Coupling in Neuronal Oscillations: Comparison of Phase-Locking Value, Mean Vector Length, Modulation Index, and Generalized-Linear-Modeling-Cross-Frequency-Coupling
# PubMed returned title: Quantification of Phase-Amplitude Coupling in Neuronal Oscillations: Comparison of Phase-Locking Value, Mean Vector Length, Modulation Index, and Generalized-Linear-Modeling-Cross-Frequency-Coupling
# Semantic_Scholar returned title: A Canonical Circuit for Generating Phase-Amplitude Coupling
# CrossRef returned title: A Canonical Circuit for Generating Phase-Amplitude Coupling
# OpenAlex returned title: A Canonical Circuit for Generating Phase-Amplitude Coupling
# PubMed returned title: A canonical circuit for generating phase-amplitude coupling
# Semantic_Scholar returned title: Phase–Amplitude Coupling, Mental Health and Cognition: Implications for Adolescence
# CrossRef returned title: Phase–Amplitude Coupling, Mental Health and Cognition: Implications for Adolescence
# OpenAlex returned title: Phase–Amplitude Coupling, Mental Health and Cognition: Implications for Adolescence
# Semantic_Scholar returned title: Cross-frequency coupling within and between the human thalamus and neocortex
# CrossRef returned title: Cross-frequency coupling within and between the human thalamus and neocortex
# OpenAlex returned title: Cross-frequency coupling within and between the human thalamus and neocortex
# PubMed returned title: Cross-frequency coupling within and between the human thalamus and neocortex
# Semantic_Scholar returned title: A Canonical Circuit for Generating Phase-Amplitude Coupling
# CrossRef returned title: A Canonical Circuit for Generating Phase-Amplitude Coupling
# OpenAlex returned title: A Canonical Circuit for Generating Phase-Amplitude Coupling
# PubMed returned title: A canonical circuit for generating phase-amplitude coupling
# Semantic_Scholar returned title: Tensorpac: An open-source Python toolbox for tensor-based phase-amplitude coupling measurement in electrophysiological brain signals
# CrossRef returned title: Tensorpac : an open-source Python toolbox for tensor-based Phase-Amplitude Coupling measurement in electrophysiological brain signals
# OpenAlex returned title: Tensorpac: An open-source Python toolbox for tensor-based phase-amplitude coupling measurement in electrophysiological brain signals
# PubMed returned title: Tensorpac: An open-source Python toolbox for tensor-based phase-amplitude coupling measurement in electrophysiological brain signals
# Semantic_Scholar returned title: Cross-frequency coupling within and between the human thalamus and neocortex
# CrossRef returned title: Cross-frequency coupling within and between the human thalamus and neocortex
# OpenAlex returned title: Cross-frequency coupling within and between the human thalamus and neocortex
# PubMed returned title: Cross-frequency coupling within and between the human thalamus and neocortex
# Semantic_Scholar returned title: Quantification of Phase-Amplitude Coupling in Neuronal Oscillations: Comparison of Phase-Locking Value, Mean Vector Length, Modulation Index, and Generalized-Linear-Modeling-Cross-Frequency-Coupling
# CrossRef returned title: Quantification of Phase-Amplitude Coupling in Neuronal Oscillations: Comparison of Phase-Locking Value, Mean Vector Length, Modulation Index, and Generalized-Linear-Modeling-Cross-Frequency-Coupling
# OpenAlex returned title: Quantification of Phase-Amplitude Coupling in Neuronal Oscillations: Comparison of Phase-Locking Value, Mean Vector Length, Modulation Index, and Generalized-Linear-Modeling-Cross-Frequency-Coupling
# PubMed returned title: Quantification of Phase-Amplitude Coupling in Neuronal Oscillations: Comparison of Phase-Locking Value, Mean Vector Length, Modulation Index, and Generalized-Linear-Modeling-Cross-Frequency-Coupling
# Semantic_Scholar returned title: Time-Frequency Based Phase-Amplitude Coupling Measure For Neuronal Oscillations
# CrossRef returned title: Time-Frequency Based Phase-Amplitude Coupling Measure For Neuronal Oscillations
# OpenAlex returned title: Time-Frequency Based Phase-Amplitude Coupling Measure For Neuronal Oscillations
# PubMed returned title: Time-Frequency Based Phase-Amplitude Coupling Measure For Neuronal Oscillations
# Semantic_Scholar returned title: The Detection of Phase Amplitude Coupling during Sensory Processing
# CrossRef returned title: The Detection of Phase Amplitude Coupling During Sensory Processing
# OpenAlex returned title: The Detection of Phase Amplitude Coupling during Sensory Processing
# PubMed returned title: The Detection of Phase Amplitude Coupling during Sensory Processing
# Semantic_Scholar returned title: Topology, Cross-Frequency, and Same-Frequency Band Interactions Shape the Generation of Phase-Amplitude Coupling in a Neural Mass Model of a Cortical Column
# CrossRef returned title: Topology, cross-frequency, and same-frequency band interactions shape the generation of phase-amplitude coupling in a neural mass model of a cortical column
# OpenAlex returned title: Topology, Cross-Frequency, and Same-Frequency Band Interactions Shape the Generation of Phase-Amplitude Coupling in a Neural Mass Model of a Cortical Column
# Semantic_Scholar returned title: Theta-gamma phase amplitude coupling in a hippocampal CA1 microcircuit
# CrossRef returned title: Theta-gamma phase amplitude coupling in a hippocampal CA1 microcircuit
# OpenAlex returned title: Theta-gamma phase amplitude coupling in a hippocampal CA1 microcircuit
# Semantic_Scholar returned title: Topology, Cross-Frequency, and Same-Frequency Band Interactions Shape the Generation of Phase-Amplitude Coupling in a Neural Mass Model of a Cortical Column
# CrossRef returned title: Topology, cross-frequency, and same-frequency band interactions shape the generation of phase-amplitude coupling in a neural mass model of a cortical column
# OpenAlex returned title: Topology, Cross-Frequency, and Same-Frequency Band Interactions Shape the Generation of Phase-Amplitude Coupling in a Neural Mass Model of a Cortical Column
# Semantic_Scholar returned title: Time-Frequency Based Phase-Amplitude Coupling Measure For Neuronal Oscillations
# CrossRef returned title: Time-Frequency Based Phase-Amplitude Coupling Measure For Neuronal Oscillations
# OpenAlex returned title: Time-Frequency Based Phase-Amplitude Coupling Measure For Neuronal Oscillations
# PubMed returned title: Time-Frequency Based Phase-Amplitude Coupling Measure For Neuronal Oscillations
# Semantic_Scholar returned title: Shifts in Gamma Phase–Amplitude Coupling Frequency from Theta to Alpha Over Posterior Cortex During Visual Tasks
# CrossRef returned title: Shifts in gamma phase–amplitude coupling frequency from theta to alpha over posterior cortex during visual tasks
# OpenAlex returned title: Shifts in gamma phase–amplitude coupling frequency from theta to alpha over posterior cortex during visual tasks
# [OrderedDict([('id',
#                OrderedDict([('doi', '10.3389/fnins.2017.00487'),
#                             ('doi_engines', ['OpenAlex', 'PubMed']),
#                             ('arxiv_id', None),
#                             ('arxiv_id_engines', None),
#                             ('pmid', '28919850'),
#                             ('pmid_engines', ['OpenAlex', 'PubMed']),
#                             ('scholar_id', None),
#                             ('scholar_id_engines', None),
#                             ('corpus_id', 19922713),
#                             ('corpus_id_engines', ['Semantic_Scholar'])])),
#               ('basic',
#                OrderedDict([('title',
#                              'The Detection of Phase Amplitude Coupling During '
#                              'Sensory Processing'),
#                             ('title_engines', ['CrossRef']),
#                             ('authors',
#                              ['R.A Seymour', 'G. Rippon', 'K. Kessler']),
#                             ('authors_engines', ['CrossRef']),
#                             ('year', 2017),
#                             ('year_engines', ['OpenAlex', 'PubMed']),
#                             ('abstract',
#                              '<jats:label>1.</jats:label><jats:title>Abstract</jats:title><jats:p>There '
#                              'is increasing interest in understanding how the '
#                              'phase and amplitude of distinct neural '
#                              'oscillations might interact to support dynamic '
#                              'communication within the brain. In particular, '
#                              'previous work has demonstrated a coupling '
#                              'between the phase of low frequency oscillations '
#                              'and the amplitude (or power) of high frequency '
#                              'oscillations during certain tasks, termed phase '
#                              'amplitude coupling (PAC). For instance, during '
#                              'visual processing in humans, PAC has been '
#                              'reliably observed between ongoing alpha (8-13Hz) '
#                              'and gamma-band (&gt;40Hz) activity. However, the '
#                              'application of PAC metrics to '
#                              'electrophysiological data can be challenging due '
#                              'to numerous methodological issues and lack of '
#                              'coherent approaches within the field. Therefore, '
#                              'in this article we outline the various analysis '
#                              'steps involved in detecting PAC, using an openly '
#                              'available MEG dataset from 16 participants '
#                              'performing an interactive visual task. Firstly, '
#                              'we localised gamma and alpha-band power using '
#                              'the Fieldtrip toolbox, and extracted time '
#                              'courses from area V1, defined using a multimodal '
#                              'parcellation scheme. These V1 responses were '
#                              'analysed for changes in alpha-gamma PAC, using '
#                              'four common algorithms. Results showed an '
#                              'increase in gamma (40-100Hz) - alpha (7-13Hz) '
#                              'PAC in response to the visual grating stimulus, '
#                              'though specific patterns of coupling were '
#                              'somewhat dependent upon the algorithm employed. '
#                              'Additionally, post-hoc analyses showed that '
#                              'these results were not driven by the presence of '
#                              'non-sinusoidal oscillations, and that trial '
#                              'length was sufficient to obtain reliable PAC '
#                              'estimates. Finally, throughout the article, '
#                              'methodological issues and practical guidelines '
#                              'for ongoing PAC research will be '
#                              'discussed.</jats:p>'),
#                             ('abstract_engines', ['CrossRef']),
#                             ('keywords',
#                              ['Toolbox',
#                               'Local field potential',
#                               'Sensory Processing',
#                               'Stimulus (psychology)']),
#                             ('keywords_engines', ['OpenAlex']),
#                             ('type', 'article'),
#                             ('type_engines', ['OpenAlex'])])),
#               ('citation_count',
#                OrderedDict([('total', 76),
#                             ('total_engines', ['OpenAlex']),
#                             ('2025', 7),
#                             ('2025_engines', ['OpenAlex']),
#                             ('2024', 7),
#                             ('2024_engines', ['OpenAlex']),
#                             ('2023', 6),
#                             ('2023_engines', ['OpenAlex']),
#                             ('2022', 9),
#                             ('2022_engines', ['OpenAlex']),
#                             ('2021', 17),
#                             ('2021_engines', ['OpenAlex']),
#                             ('2020', 14),
#                             ('2020_engines', ['OpenAlex']),
#                             ('2019', 9),
#                             ('2019_engines', ['OpenAlex']),
#                             ('2018', 6),
#                             ('2018_engines', ['OpenAlex']),
#                             ('2017', None),
#                             ('2017_engines', None),
#                             ('2016', None),
#                             ('2016_engines', None),
#                             ('2015', None),
#                             ('2015_engines', None)])),
#               ('publication',
#                OrderedDict([('journal', 'Frontiers in neuroscience'),
#                             ('journal_engines', ['PubMed']),
#                             ('short_journal', 'Front Neurosci'),
#                             ('short_journal_engines', ['PubMed']),
#                             ('impact_factor', None),
#                             ('impact_factor_engines', None),
#                             ('issn', '1662-4548'),
#                             ('issn_engines', ['PubMed']),
#                             ('volume', '11'),
#                             ('volume_engines', ['OpenAlex', 'PubMed']),
#                             ('issue', None),
#                             ('issue_engines', None),
#                             ('first_page', None),
#                             ('first_page_engines', None),
#                             ('last_page', None),
#                             ('last_page_engines', None),
#                             ('publisher', 'Cold Spring Harbor Laboratory'),
#                             ('publisher_engines', ['CrossRef'])])),
#               ('url',
#                OrderedDict([('doi', 'https://doi.org/10.3389/fnins.2017.00487'),
#                             ('doi_engines', ['OpenAlex', 'PubMed']),
#                             ('publisher',
#                              'https://doi.org/10.3389/fnins.2017.00487'),
#                             ('publisher_engines', ['OpenAlex']),
#                             ('openurl_query', None),
#                             ('openurl_engines', None),
#                             ('openurl_resolved', []),
#                             ('openurl_resolved_engines', []),
#                             ('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('path',
#                OrderedDict([('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('system',
#                OrderedDict([('searched_by_arXiv', False),
#                             ('searched_by_CrossRef', True),
#                             ('searched_by_OpenAlex', True),
#                             ('searched_by_PubMed', True),
#                             ('searched_by_Semantic_Scholar', True),
#                             ('searched_by_URL', False)]))]),
#  OrderedDict([('id',
#                OrderedDict([('doi', '10.1371/journal.pcbi.1010942'),
#                             ('doi_engines', ['CrossRef', 'OpenAlex']),
#                             ('arxiv_id', None),
#                             ('arxiv_id_engines', None),
#                             ('pmid', '36952558'),
#                             ('pmid_engines', ['OpenAlex']),
#                             ('scholar_id', None),
#                             ('scholar_id_engines', None),
#                             ('corpus_id', 257717129),
#                             ('corpus_id_engines', ['Semantic_Scholar'])])),
#               ('basic',
#                OrderedDict([('title',
#                              'Theta-gamma phase amplitude coupling in a '
#                              'hippocampal CA1 microcircuit'),
#                             ('title_engines', ['CrossRef', 'OpenAlex']),
#                             ('authors',
#                              ['Adam Ponzi',
#                               'Salvador Dura-Bernal',
#                               'Michele Migliore']),
#                             ('authors_engines', ['CrossRef']),
#                             ('year', 2023),
#                             ('year_engines', ['CrossRef', 'OpenAlex']),
#                             ('abstract',
#                              '<jats:p>Phase amplitude coupling (PAC) between '
#                              'slow and fast oscillations is found throughout '
#                              'the brain and plays important functional roles. '
#                              'Its neural origin remains unclear. Experimental '
#                              'findings are often puzzling and sometimes '
#                              'contradictory. Most computational models rely on '
#                              'pairs of pacemaker neurons or neural populations '
#                              'tuned at different frequencies to produce PAC. '
#                              'Here, using a data-driven model of a hippocampal '
#                              'microcircuit, we demonstrate that PAC can '
#                              'naturally emerge from a single feedback '
#                              'mechanism involving an inhibitory and excitatory '
#                              'neuron population, which interplay to generate '
#                              'theta frequency periodic bursts of higher '
#                              'frequency gamma. The model suggests the '
#                              'conditions under which a CA1 microcircuit can '
#                              'operate to elicit theta-gamma PAC, and '
#                              'highlights the modulatory role of OLM and PVBC '
#                              'cells, recurrent connectivity, and short term '
#                              'synaptic plasticity. Surprisingly, the results '
#                              'suggest the experimentally testable prediction '
#                              'that the generation of the slow population '
#                              'oscillation requires the fast one and cannot '
#                              'occur without it.</jats:p>'),
#                             ('abstract_engines', ['CrossRef']),
#                             ('keywords', ['Oscillation (cell signaling)']),
#                             ('keywords_engines', ['OpenAlex']),
#                             ('type', 'article'),
#                             ('type_engines', ['OpenAlex'])])),
#               ('citation_count',
#                OrderedDict([('total', 18),
#                             ('total_engines', ['OpenAlex']),
#                             ('2025', 3),
#                             ('2025_engines', ['OpenAlex']),
#                             ('2024', 12),
#                             ('2024_engines', ['OpenAlex']),
#                             ('2023', 3),
#                             ('2023_engines', ['OpenAlex']),
#                             ('2022', None),
#                             ('2022_engines', None),
#                             ('2021', None),
#                             ('2021_engines', None),
#                             ('2020', None),
#                             ('2020_engines', None),
#                             ('2019', None),
#                             ('2019_engines', None),
#                             ('2018', None),
#                             ('2018_engines', None),
#                             ('2017', None),
#                             ('2017_engines', None),
#                             ('2016', None),
#                             ('2016_engines', None),
#                             ('2015', None),
#                             ('2015_engines', None)])),
#               ('publication',
#                OrderedDict([('journal', 'PLOS Computational Biology'),
#                             ('journal_engines', ['CrossRef']),
#                             ('short_journal', 'PLoS Comput Biol'),
#                             ('short_journal_engines', ['CrossRef']),
#                             ('impact_factor', None),
#                             ('impact_factor_engines', None),
#                             ('issn', '1553-7358'),
#                             ('issn_engines', ['CrossRef']),
#                             ('volume', '19'),
#                             ('volume_engines', ['CrossRef', 'OpenAlex']),
#                             ('issue', '3'),
#                             ('issue_engines', ['CrossRef', 'OpenAlex']),
#                             ('first_page', 'e1010942'),
#                             ('first_page_engines', ['OpenAlex']),
#                             ('last_page', 'e1010942'),
#                             ('last_page_engines', ['OpenAlex']),
#                             ('publisher', 'Public Library of Science (PLoS)'),
#                             ('publisher_engines', ['CrossRef'])])),
#               ('url',
#                OrderedDict([('doi',
#                              'https://doi.org/10.1371/journal.pcbi.1010942'),
#                             ('doi_engines', ['CrossRef', 'OpenAlex']),
#                             ('publisher',
#                              'https://doi.org/10.1371/journal.pcbi.1010942'),
#                             ('publisher_engines', ['OpenAlex']),
#                             ('openurl_query', None),
#                             ('openurl_engines', None),
#                             ('openurl_resolved', []),
#                             ('openurl_resolved_engines', []),
#                             ('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('path',
#                OrderedDict([('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('system',
#                OrderedDict([('searched_by_arXiv', False),
#                             ('searched_by_CrossRef', True),
#                             ('searched_by_OpenAlex', True),
#                             ('searched_by_PubMed', False),
#                             ('searched_by_Semantic_Scholar', True),
#                             ('searched_by_URL', False)]))]),
#  OrderedDict([('id',
#                OrderedDict([('doi', '10.3389/fnhum.2021.622313'),
#                             ('doi_engines', ['CrossRef', 'OpenAlex']),
#                             ('arxiv_id', None),
#                             ('arxiv_id_engines', None),
#                             ('pmid', '33841115'),
#                             ('pmid_engines', ['OpenAlex']),
#                             ('scholar_id', None),
#                             ('scholar_id_engines', None),
#                             ('corpus_id', 232358612),
#                             ('corpus_id_engines', ['Semantic_Scholar'])])),
#               ('basic',
#                OrderedDict([('title',
#                              'Phase–Amplitude Coupling, Mental Health and '
#                              'Cognition: Implications for Adolescence'),
#                             ('title_engines', ['CrossRef', 'OpenAlex']),
#                             ('authors',
#                              ['Dashiell D. Sacks',
#                               'Paul E. Schwenn',
#                               'Larisa T. McLoughlin',
#                               'Jim Lagopoulos',
#                               'Daniel F. Hermens']),
#                             ('authors_engines', ['CrossRef']),
#                             ('year', 2021),
#                             ('year_engines', ['CrossRef', 'OpenAlex']),
#                             ('abstract',
#                              '<jats:p>Identifying biomarkers of developing '
#                              'mental disorder is crucial to improving early '
#                              'identification and treatment—a key strategy for '
#                              'reducing the burden of mental disorders. '
#                              'Cross-frequency coupling between two different '
#                              'frequencies of neural oscillations is one such '
#                              'promising measure, believed to reflect '
#                              'synchronization between local and global '
#                              'networks in the brain. Specifically, in adults '
#                              'phase–amplitude coupling (PAC) has been shown to '
#                              'be involved in a range of cognitive processes, '
#                              'including working and long-term memory, '
#                              'attention, language, and fluid intelligence. '
#                              'Evidence suggests that increased PAC mediates '
#                              'both temporary and lasting improvements in '
#                              'working memory elicited by transcranial '
#                              'direct-current stimulation and reductions in '
#                              'depressive symptoms after transcranial magnetic '
#                              'stimulation. Moreover, research has shown that '
#                              'abnormal patterns of PAC are associated with '
#                              'depression and schizophrenia in adults. PAC is '
#                              'believed to be closely related to '
#                              'cortico-cortico white matter (WM) '
#                              'microstructure, which is well established in the '
#                              'literature as a structural mechanism underlying '
#                              'mental health. Some cognitive findings have been '
#                              'replicated in adolescents and abnormal patterns '
#                              'of PAC have also been linked to ADHD in young '
#                              'people. However, currently most research has '
#                              'focused on cross-sectional adult samples. '
#                              'Whereas initial hypotheses suggested that PAC '
#                              'was a state-based measure due to an early focus '
#                              'on cognitive, task-based research, current '
#                              'evidence suggests that PAC has both state-based '
#                              'and stable components. Future longitudinal '
#                              'research focusing on PAC throughout adolescent '
#                              'development could further our understanding of '
#                              'the relationship between mental health and '
#                              'cognition and facilitate the development of new '
#                              'methods for the identification and treatment of '
#                              'youth mental health.</jats:p>'),
#                             ('abstract_engines', ['CrossRef']),
#                             ('keywords', None),
#                             ('keywords_engines', None),
#                             ('type', 'review'),
#                             ('type_engines', ['OpenAlex'])])),
#               ('citation_count',
#                OrderedDict([('total', 19),
#                             ('total_engines', ['OpenAlex']),
#                             ('2025', 7),
#                             ('2025_engines', ['OpenAlex']),
#                             ('2024', 6),
#                             ('2024_engines', ['OpenAlex']),
#                             ('2023', 4),
#                             ('2023_engines', ['OpenAlex']),
#                             ('2022', 1),
#                             ('2022_engines', ['OpenAlex']),
#                             ('2021', 1),
#                             ('2021_engines', ['OpenAlex']),
#                             ('2020', None),
#                             ('2020_engines', None),
#                             ('2019', None),
#                             ('2019_engines', None),
#                             ('2018', None),
#                             ('2018_engines', None),
#                             ('2017', None),
#                             ('2017_engines', None),
#                             ('2016', None),
#                             ('2016_engines', None),
#                             ('2015', None),
#                             ('2015_engines', None)])),
#               ('publication',
#                OrderedDict([('journal', 'Frontiers in Human Neuroscience'),
#                             ('journal_engines', ['CrossRef']),
#                             ('short_journal', 'Front. Hum. Neurosci.'),
#                             ('short_journal_engines', ['CrossRef']),
#                             ('impact_factor', None),
#                             ('impact_factor_engines', None),
#                             ('issn', '1662-5161'),
#                             ('issn_engines', ['CrossRef']),
#                             ('volume', '15'),
#                             ('volume_engines', ['CrossRef', 'OpenAlex']),
#                             ('issue', None),
#                             ('issue_engines', None),
#                             ('first_page', None),
#                             ('first_page_engines', None),
#                             ('last_page', None),
#                             ('last_page_engines', None),
#                             ('publisher', 'Frontiers Media SA'),
#                             ('publisher_engines', ['CrossRef'])])),
#               ('url',
#                OrderedDict([('doi',
#                              'https://doi.org/10.3389/fnhum.2021.622313'),
#                             ('doi_engines', ['CrossRef', 'OpenAlex']),
#                             ('publisher',
#                              'https://doi.org/10.3389/fnhum.2021.622313'),
#                             ('publisher_engines', ['OpenAlex']),
#                             ('openurl_query', None),
#                             ('openurl_engines', None),
#                             ('openurl_resolved', []),
#                             ('openurl_resolved_engines', []),
#                             ('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('path',
#                OrderedDict([('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('system',
#                OrderedDict([('searched_by_arXiv', False),
#                             ('searched_by_CrossRef', True),
#                             ('searched_by_OpenAlex', True),
#                             ('searched_by_PubMed', False),
#                             ('searched_by_Semantic_Scholar', True),
#                             ('searched_by_URL', False)]))]),
#  OrderedDict([('id',
#                OrderedDict([('doi', '10.1371/journal.pcbi.1008302'),
#                             ('doi_engines', ['OpenAlex', 'PubMed']),
#                             ('arxiv_id', None),
#                             ('arxiv_id_engines', None),
#                             ('pmid', '33119593'),
#                             ('pmid_engines', ['OpenAlex', 'PubMed']),
#                             ('scholar_id', None),
#                             ('scholar_id_engines', None),
#                             ('corpus_id', 216071804),
#                             ('corpus_id_engines', ['Semantic_Scholar'])])),
#               ('basic',
#                OrderedDict([('title',
#                              'Tensorpac : an open-source Python toolbox for '
#                              'tensor-based Phase-Amplitude Coupling '
#                              'measurement in electrophysiological brain '
#                              'signals'),
#                             ('title_engines', ['CrossRef']),
#                             ('authors',
#                              ['Etienne Combrisson',
#                               'Timothy Nest',
#                               'Andrea Brovelli',
#                               'Robin A.A. Ince',
#                               'Juan LP Soto',
#                               'Aymeric Guillot',
#                               'Karim Jerbi']),
#                             ('authors_engines', ['CrossRef']),
#                             ('year', 2020),
#                             ('year_engines', ['OpenAlex', 'PubMed']),
#                             ('abstract',
#                              '<jats:title>Abstract</jats:title><jats:p>Despite '
#                              'being the focus of a thriving field of research, '
#                              'the biological mechanisms that underlie '
#                              'information integration in the brain are not yet '
#                              'fully understood. A theory that has gained a lot '
#                              'of traction in recent years suggests that '
#                              'multi-scale integration is regulated by a '
#                              'hierarchy of mutually interacting neural '
#                              'oscillations. In particular, there is '
#                              'accumulating evidence that phase-amplitude '
#                              'coupling (PAC), a specific form of '
#                              'cross-frequency interaction, plays a key role in '
#                              'numerous cognitive processes. Current research '
#                              'in the field is not only hampered by the absence '
#                              'of a gold standard for PAC analysis, but also by '
#                              'the computational costs of running exhaustive '
#                              'computations on large and high-dimensional '
#                              'electrophysiological brain signals. In addition, '
#                              'various signal properties and analyses '
#                              'parameters can lead to spurious PAC. Here, we '
#                              'present Tensorpac, an open-source Python toolbox '
#                              'dedicated to PAC analysis of neurophysiological '
#                              'data. The advantages of Tensorpac include (1) '
#                              'higher computational efficiency thanks to '
#                              'software design that combines tensor '
#                              'computations and parallel computing, (2) the '
#                              'implementation of all most widely used PAC '
#                              'methods in one package, (3) the statistical '
#                              'analysis of PAC measures, and (4) extended PAC '
#                              'visualization capabilities. Tensorpac is '
#                              'distributed under a BSD-3-Clause license and can '
#                              'be launched on any operating system (Linux, OSX '
#                              'and Windows). It can be installed directly via '
#                              'pip or downloaded from Github (<jats:ext-link '
#                              'xmlns:xlink="http://www.w3.org/1999/xlink" '
#                              'ext-link-type="uri" '
#                              'xlink:href="https://github.com/EtienneCmb/tensorpac">https://github.com/EtienneCmb/tensorpac</jats:ext-link>). '
#                              'By making Tensorpac available, we aim to enhance '
#                              'the reproducibility and quality of PAC research, '
#                              'and provide open tools that will accelerate '
#                              'future method development in '
#                              'neuroscience.</jats:p>'),
#                             ('abstract_engines', ['CrossRef']),
#                             ('keywords',
#                              ['Python',
#                               'Toolbox',
#                               'Spurious relationship',
#                               'Computational neuroscience']),
#                             ('keywords_engines', ['OpenAlex']),
#                             ('type', 'article'),
#                             ('type_engines', ['OpenAlex'])])),
#               ('citation_count',
#                OrderedDict([('total', 62),
#                             ('total_engines', ['OpenAlex']),
#                             ('2025', 12),
#                             ('2025_engines', ['OpenAlex']),
#                             ('2024', 16),
#                             ('2024_engines', ['OpenAlex']),
#                             ('2023', 11),
#                             ('2023_engines', ['OpenAlex']),
#                             ('2022', 10),
#                             ('2022_engines', ['OpenAlex']),
#                             ('2021', 9),
#                             ('2021_engines', ['OpenAlex']),
#                             ('2020', 1),
#                             ('2020_engines', ['OpenAlex']),
#                             ('2019', None),
#                             ('2019_engines', None),
#                             ('2018', None),
#                             ('2018_engines', None),
#                             ('2017', None),
#                             ('2017_engines', None),
#                             ('2016', None),
#                             ('2016_engines', None),
#                             ('2015', None),
#                             ('2015_engines', None)])),
#               ('publication',
#                OrderedDict([('journal', 'PLoS computational biology'),
#                             ('journal_engines', ['PubMed']),
#                             ('short_journal', 'PLoS Comput Biol'),
#                             ('short_journal_engines', ['PubMed']),
#                             ('impact_factor', None),
#                             ('impact_factor_engines', None),
#                             ('issn', '1553-7358'),
#                             ('issn_engines', ['PubMed']),
#                             ('volume', '16'),
#                             ('volume_engines', ['OpenAlex', 'PubMed']),
#                             ('issue', '10'),
#                             ('issue_engines', ['OpenAlex', 'PubMed']),
#                             ('first_page', 'e1008302'),
#                             ('first_page_engines', ['OpenAlex']),
#                             ('last_page', 'e1008302'),
#                             ('last_page_engines', ['OpenAlex']),
#                             ('publisher', 'Cold Spring Harbor Laboratory'),
#                             ('publisher_engines', ['CrossRef'])])),
#               ('url',
#                OrderedDict([('doi',
#                              'https://doi.org/10.1371/journal.pcbi.1008302'),
#                             ('doi_engines', ['OpenAlex', 'PubMed']),
#                             ('publisher',
#                              'https://doi.org/10.1371/journal.pcbi.1008302'),
#                             ('publisher_engines', ['OpenAlex']),
#                             ('openurl_query', None),
#                             ('openurl_engines', None),
#                             ('openurl_resolved', []),
#                             ('openurl_resolved_engines', []),
#                             ('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('path',
#                OrderedDict([('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('system',
#                OrderedDict([('searched_by_arXiv', False),
#                             ('searched_by_CrossRef', True),
#                             ('searched_by_OpenAlex', True),
#                             ('searched_by_PubMed', True),
#                             ('searched_by_Semantic_Scholar', True),
#                             ('searched_by_URL', False)]))]),
#  OrderedDict([('id',
#                OrderedDict([('doi', '10.3389/fnins.2019.00573'),
#                             ('doi_engines', ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('arxiv_id', None),
#                             ('arxiv_id_engines', None),
#                             ('pmid', '31275096'),
#                             ('pmid_engines', ['OpenAlex', 'PubMed']),
#                             ('scholar_id', None),
#                             ('scholar_id_engines', None),
#                             ('corpus_id', 182003214),
#                             ('corpus_id_engines', ['Semantic_Scholar'])])),
#               ('basic',
#                OrderedDict([('title',
#                              'Quantification of Phase-Amplitude Coupling in '
#                              'Neuronal Oscillations: Comparison of '
#                              'Phase-Locking Value, Mean Vector Length, '
#                              'Modulation Index, and '
#                              'Generalized-Linear-Modeling-Cross-Frequency-Coupling'),
#                             ('title_engines',
#                              ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('authors',
#                              ['Mareike J. Hülsemann',
#                               'Ewald Naumann',
#                               'Björn Rasch']),
#                             ('authors_engines', ['CrossRef', 'OpenAlex']),
#                             ('year', 2019),
#                             ('year_engines',
#                              ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('abstract',
#                              'Phase-amplitude coupling is a promising '
#                              'construct to study cognitive processes in '
#                              'electroencephalography (EEG) and '
#                              'magnetencephalography (MEG). Due to the novelty '
#                              'of the concept, various measures are used in the '
#                              'literature to calculate phase-amplitude '
#                              'coupling. Here, performance of the three most '
#                              'widely used phase-amplitude coupling measures – '
#                              'phase-locking value (PLV), mean vector length '
#                              '(MVL), and modulation index (MI) – and of the '
#                              'generalized linear modeling cross-frequency '
#                              'coupling (GLM-CFC) method is thoroughly compared '
#                              'with the help of simulated data. We combine '
#                              'advantages of previous reviews and use a '
#                              'realistic data simulation, examine moderators '
#                              'and provide inferential statistics for the '
#                              'comparison of all four indices of '
#                              'phase-amplitude coupling. Our analyses show that '
#                              'all four indices successfully differentiate '
#                              'coupling strength and coupling width when '
#                              'monophasic coupling is present. While the MVL '
#                              'was most sensitive to modulations in coupling '
#                              'strengths and width, only the MI and GLM-CFC can '
#                              'detect biphasic coupling. Coupling values of all '
#                              'four indices were influenced by moderators '
#                              'including data length, signal-to-noise-ratio, '
#                              'and sampling rate when approaching Nyquist '
#                              'frequencies. The MI was most robust against '
#                              'confounding influences of these moderators. '
#                              'Based on our analyses, we recommend the MI for '
#                              'noisy and short data epochs with unknown forms '
#                              'of coupling. For high quality and long data '
#                              'epochs with monophasic coupling and a high '
#                              'signal-to-noise ratio, the use of the MVL is '
#                              'recommended. Ideally, both indices are reported '
#                              'simultaneously for one data set.'),
#                             ('abstract_engines', ['Semantic_Scholar']),
#                             ('keywords', None),
#                             ('keywords_engines', None),
#                             ('type', 'article'),
#                             ('type_engines', ['OpenAlex'])])),
#               ('citation_count',
#                OrderedDict([('total', 158),
#                             ('total_engines', ['OpenAlex']),
#                             ('2025', 21),
#                             ('2025_engines', ['OpenAlex']),
#                             ('2024', 30),
#                             ('2024_engines', ['OpenAlex']),
#                             ('2023', 29),
#                             ('2023_engines', ['OpenAlex']),
#                             ('2022', 29),
#                             ('2022_engines', ['OpenAlex']),
#                             ('2021', 31),
#                             ('2021_engines', ['OpenAlex']),
#                             ('2020', 12),
#                             ('2020_engines', ['OpenAlex']),
#                             ('2019', 3),
#                             ('2019_engines', ['OpenAlex']),
#                             ('2018', 1),
#                             ('2018_engines', ['OpenAlex']),
#                             ('2017', None),
#                             ('2017_engines', None),
#                             ('2016', None),
#                             ('2016_engines', None),
#                             ('2015', None),
#                             ('2015_engines', None)])),
#               ('publication',
#                OrderedDict([('journal', 'Frontiers in Neuroscience'),
#                             ('journal_engines', ['CrossRef']),
#                             ('short_journal', 'Front. Neurosci.'),
#                             ('short_journal_engines', ['CrossRef']),
#                             ('impact_factor', None),
#                             ('impact_factor_engines', None),
#                             ('issn', '1662-453X'),
#                             ('issn_engines', ['CrossRef']),
#                             ('volume', '13'),
#                             ('volume_engines',
#                              ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('issue', None),
#                             ('issue_engines', None),
#                             ('first_page', None),
#                             ('first_page_engines', None),
#                             ('last_page', None),
#                             ('last_page_engines', None),
#                             ('publisher', 'Frontiers Media SA'),
#                             ('publisher_engines', ['CrossRef'])])),
#               ('url',
#                OrderedDict([('doi', 'https://doi.org/10.3389/fnins.2019.00573'),
#                             ('doi_engines', ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('publisher',
#                              'https://doi.org/10.3389/fnins.2019.00573'),
#                             ('publisher_engines', ['OpenAlex']),
#                             ('openurl_query', None),
#                             ('openurl_engines', None),
#                             ('openurl_resolved', []),
#                             ('openurl_resolved_engines', []),
#                             ('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('path',
#                OrderedDict([('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('system',
#                OrderedDict([('searched_by_arXiv', False),
#                             ('searched_by_CrossRef', True),
#                             ('searched_by_OpenAlex', True),
#                             ('searched_by_PubMed', True),
#                             ('searched_by_Semantic_Scholar', True),
#                             ('searched_by_URL', False)]))]),
#  OrderedDict([('id',
#                OrderedDict([('doi', '10.1371/journal.pone.0102591'),
#                             ('doi_engines', ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('arxiv_id', None),
#                             ('arxiv_id_engines', None),
#                             ('pmid', '25136855'),
#                             ('pmid_engines', ['OpenAlex', 'PubMed']),
#                             ('scholar_id', None),
#                             ('scholar_id_engines', None),
#                             ('corpus_id', 157901),
#                             ('corpus_id_engines', ['Semantic_Scholar'])])),
#               ('basic',
#                OrderedDict([('title',
#                              'A Canonical Circuit for Generating '
#                              'Phase-Amplitude Coupling'),
#                             ('title_engines', ['CrossRef', 'OpenAlex']),
#                             ('authors',
#                              ['Angela C. E. Onslow',
#                               'Matthew W. Jones',
#                               'Rafal Bogacz']),
#                             ('authors_engines', ['CrossRef']),
#                             ('year', 2014),
#                             ('year_engines',
#                              ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('abstract',
#                              '‘Phase amplitude coupling’ (PAC) in oscillatory '
#                              'neural activity describes a phenomenon whereby '
#                              'the amplitude of higher frequency activity is '
#                              'modulated by the phase of lower frequency '
#                              'activity. Such coupled oscillatory activity – '
#                              'also referred to as ‘cross-frequency coupling’ '
#                              'or ‘nested rhythms’ – has been shown to occur in '
#                              'a number of brain regions and at behaviorally '
#                              'relevant time points during cognitive tasks; '
#                              'this suggests functional relevance, but the '
#                              'circuit mechanisms of PAC generation remain '
#                              'unclear. In this paper we present a model of a '
#                              'canonical circuit for generating PAC activity, '
#                              'showing how interconnected excitatory and '
#                              'inhibitory neural populations can be '
#                              'periodically shifted in to and out of '
#                              'oscillatory firing patterns by afferent drive, '
#                              'hence generating higher frequency oscillations '
#                              'phase-locked to a lower frequency, oscillating '
#                              'input signal. Since many brain regions contain '
#                              'mutually connected excitatory-inhibitory '
#                              'populations receiving oscillatory input, the '
#                              'simplicity of the mechanism generating PAC in '
#                              'such networks may explain the ubiquity of PAC '
#                              'across diverse neural systems and behaviors. '
#                              'Analytic treatment of this circuit as a '
#                              'nonlinear dynamical system demonstrates how '
#                              'connection strengths and inputs to the '
#                              'populations can be varied in order to change the '
#                              'extent and nature of PAC activity, importantly '
#                              'which phase of the lower frequency rhythm the '
#                              'higher frequency activity is locked to. '
#                              'Consequently, this model can inform attempts to '
#                              'associate distinct types of PAC with different '
#                              'network topologies and physiologies in real '
#                              'data.'),
#                             ('abstract_engines', ['Semantic_Scholar']),
#                             ('keywords', ['Biological neural network']),
#                             ('keywords_engines', ['OpenAlex']),
#                             ('type', 'article'),
#                             ('type_engines', ['OpenAlex'])])),
#               ('citation_count',
#                OrderedDict([('total', 83),
#                             ('total_engines', ['OpenAlex']),
#                             ('2025', 1),
#                             ('2025_engines', ['OpenAlex']),
#                             ('2024', 5),
#                             ('2024_engines', ['OpenAlex']),
#                             ('2023', 8),
#                             ('2023_engines', ['OpenAlex']),
#                             ('2022', 5),
#                             ('2022_engines', ['OpenAlex']),
#                             ('2021', 13),
#                             ('2021_engines', ['OpenAlex']),
#                             ('2020', 13),
#                             ('2020_engines', ['OpenAlex']),
#                             ('2019', 13),
#                             ('2019_engines', ['OpenAlex']),
#                             ('2018', 5),
#                             ('2018_engines', ['OpenAlex']),
#                             ('2017', 8),
#                             ('2017_engines', ['OpenAlex']),
#                             ('2016', 5),
#                             ('2016_engines', ['OpenAlex']),
#                             ('2015', 7),
#                             ('2015_engines', ['OpenAlex'])])),
#               ('publication',
#                OrderedDict([('journal', 'PLoS ONE'),
#                             ('journal_engines', ['CrossRef']),
#                             ('short_journal', 'PLoS ONE'),
#                             ('short_journal_engines', ['CrossRef']),
#                             ('impact_factor', None),
#                             ('impact_factor_engines', None),
#                             ('issn', '1932-6203'),
#                             ('issn_engines', ['CrossRef', 'PubMed']),
#                             ('volume', '9'),
#                             ('volume_engines',
#                              ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('issue', '8'),
#                             ('issue_engines',
#                              ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('first_page', 'e102591'),
#                             ('first_page_engines', ['OpenAlex']),
#                             ('last_page', 'e102591'),
#                             ('last_page_engines', ['OpenAlex']),
#                             ('publisher', 'Public Library of Science (PLoS)'),
#                             ('publisher_engines', ['CrossRef'])])),
#               ('url',
#                OrderedDict([('doi',
#                              'https://doi.org/10.1371/journal.pone.0102591'),
#                             ('doi_engines', ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('publisher',
#                              'https://doi.org/10.1371/journal.pone.0102591'),
#                             ('publisher_engines', ['OpenAlex']),
#                             ('openurl_query', None),
#                             ('openurl_engines', None),
#                             ('openurl_resolved', []),
#                             ('openurl_resolved_engines', []),
#                             ('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('path',
#                OrderedDict([('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('system',
#                OrderedDict([('searched_by_arXiv', False),
#                             ('searched_by_CrossRef', True),
#                             ('searched_by_OpenAlex', True),
#                             ('searched_by_PubMed', True),
#                             ('searched_by_Semantic_Scholar', True),
#                             ('searched_by_URL', False)]))]),
#  OrderedDict([('id',
#                OrderedDict([('doi', '10.3389/fnhum.2021.622313'),
#                             ('doi_engines', ['CrossRef', 'OpenAlex']),
#                             ('arxiv_id', None),
#                             ('arxiv_id_engines', None),
#                             ('pmid', '33841115'),
#                             ('pmid_engines', ['OpenAlex']),
#                             ('scholar_id', None),
#                             ('scholar_id_engines', None),
#                             ('corpus_id', 232358612),
#                             ('corpus_id_engines', ['Semantic_Scholar'])])),
#               ('basic',
#                OrderedDict([('title',
#                              'Phase–Amplitude Coupling, Mental Health and '
#                              'Cognition: Implications for Adolescence'),
#                             ('title_engines', ['CrossRef', 'OpenAlex']),
#                             ('authors',
#                              ['Dashiell D. Sacks',
#                               'Paul E. Schwenn',
#                               'Larisa T. McLoughlin',
#                               'Jim Lagopoulos',
#                               'Daniel F. Hermens']),
#                             ('authors_engines', ['CrossRef']),
#                             ('year', 2021),
#                             ('year_engines', ['CrossRef', 'OpenAlex']),
#                             ('abstract',
#                              '<jats:p>Identifying biomarkers of developing '
#                              'mental disorder is crucial to improving early '
#                              'identification and treatment—a key strategy for '
#                              'reducing the burden of mental disorders. '
#                              'Cross-frequency coupling between two different '
#                              'frequencies of neural oscillations is one such '
#                              'promising measure, believed to reflect '
#                              'synchronization between local and global '
#                              'networks in the brain. Specifically, in adults '
#                              'phase–amplitude coupling (PAC) has been shown to '
#                              'be involved in a range of cognitive processes, '
#                              'including working and long-term memory, '
#                              'attention, language, and fluid intelligence. '
#                              'Evidence suggests that increased PAC mediates '
#                              'both temporary and lasting improvements in '
#                              'working memory elicited by transcranial '
#                              'direct-current stimulation and reductions in '
#                              'depressive symptoms after transcranial magnetic '
#                              'stimulation. Moreover, research has shown that '
#                              'abnormal patterns of PAC are associated with '
#                              'depression and schizophrenia in adults. PAC is '
#                              'believed to be closely related to '
#                              'cortico-cortico white matter (WM) '
#                              'microstructure, which is well established in the '
#                              'literature as a structural mechanism underlying '
#                              'mental health. Some cognitive findings have been '
#                              'replicated in adolescents and abnormal patterns '
#                              'of PAC have also been linked to ADHD in young '
#                              'people. However, currently most research has '
#                              'focused on cross-sectional adult samples. '
#                              'Whereas initial hypotheses suggested that PAC '
#                              'was a state-based measure due to an early focus '
#                              'on cognitive, task-based research, current '
#                              'evidence suggests that PAC has both state-based '
#                              'and stable components. Future longitudinal '
#                              'research focusing on PAC throughout adolescent '
#                              'development could further our understanding of '
#                              'the relationship between mental health and '
#                              'cognition and facilitate the development of new '
#                              'methods for the identification and treatment of '
#                              'youth mental health.</jats:p>'),
#                             ('abstract_engines', ['CrossRef']),
#                             ('keywords', None),
#                             ('keywords_engines', None),
#                             ('type', 'review'),
#                             ('type_engines', ['OpenAlex'])])),
#               ('citation_count',
#                OrderedDict([('total', 19),
#                             ('total_engines', ['OpenAlex']),
#                             ('2025', 7),
#                             ('2025_engines', ['OpenAlex']),
#                             ('2024', 6),
#                             ('2024_engines', ['OpenAlex']),
#                             ('2023', 4),
#                             ('2023_engines', ['OpenAlex']),
#                             ('2022', 1),
#                             ('2022_engines', ['OpenAlex']),
#                             ('2021', 1),
#                             ('2021_engines', ['OpenAlex']),
#                             ('2020', None),
#                             ('2020_engines', None),
#                             ('2019', None),
#                             ('2019_engines', None),
#                             ('2018', None),
#                             ('2018_engines', None),
#                             ('2017', None),
#                             ('2017_engines', None),
#                             ('2016', None),
#                             ('2016_engines', None),
#                             ('2015', None),
#                             ('2015_engines', None)])),
#               ('publication',
#                OrderedDict([('journal', 'Frontiers in Human Neuroscience'),
#                             ('journal_engines', ['CrossRef']),
#                             ('short_journal', 'Front. Hum. Neurosci.'),
#                             ('short_journal_engines', ['CrossRef']),
#                             ('impact_factor', None),
#                             ('impact_factor_engines', None),
#                             ('issn', '1662-5161'),
#                             ('issn_engines', ['CrossRef']),
#                             ('volume', '15'),
#                             ('volume_engines', ['CrossRef', 'OpenAlex']),
#                             ('issue', None),
#                             ('issue_engines', None),
#                             ('first_page', None),
#                             ('first_page_engines', None),
#                             ('last_page', None),
#                             ('last_page_engines', None),
#                             ('publisher', 'Frontiers Media SA'),
#                             ('publisher_engines', ['CrossRef'])])),
#               ('url',
#                OrderedDict([('doi',
#                              'https://doi.org/10.3389/fnhum.2021.622313'),
#                             ('doi_engines', ['CrossRef', 'OpenAlex']),
#                             ('publisher',
#                              'https://doi.org/10.3389/fnhum.2021.622313'),
#                             ('publisher_engines', ['OpenAlex']),
#                             ('openurl_query', None),
#                             ('openurl_engines', None),
#                             ('openurl_resolved', []),
#                             ('openurl_resolved_engines', []),
#                             ('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('path',
#                OrderedDict([('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('system',
#                OrderedDict([('searched_by_arXiv', False),
#                             ('searched_by_CrossRef', True),
#                             ('searched_by_OpenAlex', True),
#                             ('searched_by_PubMed', False),
#                             ('searched_by_Semantic_Scholar', True),
#                             ('searched_by_URL', False)]))]),
#  OrderedDict([('id',
#                OrderedDict([('doi', '10.3389/fnhum.2013.00084'),
#                             ('doi_engines', ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('arxiv_id', None),
#                             ('arxiv_id_engines', None),
#                             ('pmid', '23532592'),
#                             ('pmid_engines', ['OpenAlex', 'PubMed']),
#                             ('scholar_id', None),
#                             ('scholar_id_engines', None),
#                             ('corpus_id', 14588601),
#                             ('corpus_id_engines', ['Semantic_Scholar'])])),
#               ('basic',
#                OrderedDict([('title',
#                              'Cross-frequency coupling within and between the '
#                              'human thalamus and neocortex'),
#                             ('title_engines',
#                              ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('authors',
#                              ['Thomas H B Fitzgerald',
#                               'Antonio Valentin',
#                               'Richard Selway',
#                               'Mark P Richardson']),
#                             ('authors_engines', ['PubMed']),
#                             ('year', 2013),
#                             ('year_engines',
#                              ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('abstract',
#                              'There is currently growing interest in, and '
#                              'increasing evidence for, cross-frequency '
#                              'interactions between electrical field '
#                              'oscillations in the brains of various organisms. '
#                              'A number of theories have linked such '
#                              'interactions to crucial features of neuronal '
#                              'function and cognition. In mammals, these '
#                              'interactions have mostly been reported in the '
#                              'neocortex and hippocampus, and it remains '
#                              'unexplored whether similar patterns of activity '
#                              'occur in the thalamus, and between the thalamus '
#                              'and neocortex. Here we use data recorded from '
#                              'patients undergoing thalamic deep-brain '
#                              'stimulation for epilepsy to demonstrate the '
#                              'existence and prevalence, across a range of '
#                              'frequencies, of both phase–amplitude (PAC) and '
#                              'amplitude–amplitude coupling (AAC) both within '
#                              'the thalamus and prefrontal cortex (PFC), and '
#                              'between them. These cross-frequency interactions '
#                              'may play an important role in local processing '
#                              'within the thalamus and neocortex, as well as '
#                              'information transfer between them.'),
#                             ('abstract_engines', ['Semantic_Scholar']),
#                             ('keywords',
#                              ['Neocortex', 'Local field potential']),
#                             ('keywords_engines', ['OpenAlex']),
#                             ('type', 'article'),
#                             ('type_engines', ['OpenAlex'])])),
#               ('citation_count',
#                OrderedDict([('total', 62),
#                             ('total_engines', ['OpenAlex']),
#                             ('2025', 1),
#                             ('2025_engines', ['OpenAlex']),
#                             ('2024', 8),
#                             ('2024_engines', ['OpenAlex']),
#                             ('2023', 3),
#                             ('2023_engines', ['OpenAlex']),
#                             ('2022', 3),
#                             ('2022_engines', ['OpenAlex']),
#                             ('2021', 5),
#                             ('2021_engines', ['OpenAlex']),
#                             ('2020', 4),
#                             ('2020_engines', ['OpenAlex']),
#                             ('2019', 4),
#                             ('2019_engines', ['OpenAlex']),
#                             ('2018', 6),
#                             ('2018_engines', ['OpenAlex']),
#                             ('2017', 8),
#                             ('2017_engines', ['OpenAlex']),
#                             ('2016', 9),
#                             ('2016_engines', ['OpenAlex']),
#                             ('2015', 3),
#                             ('2015_engines', ['OpenAlex']),
#                             ('2014_engines', ['OpenAlex']),
#                             ('2014', 6),
#                             ('2013_engines', ['OpenAlex']),
#                             ('2013', 2)])),
#               ('publication',
#                OrderedDict([('journal', 'Frontiers in Human Neuroscience'),
#                             ('journal_engines', ['CrossRef']),
#                             ('short_journal', 'Front. Hum. Neurosci.'),
#                             ('short_journal_engines', ['CrossRef']),
#                             ('impact_factor', None),
#                             ('impact_factor_engines', None),
#                             ('issn', '1662-5161'),
#                             ('issn_engines', ['CrossRef', 'PubMed']),
#                             ('volume', '7'),
#                             ('volume_engines',
#                              ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('issue', None),
#                             ('issue_engines', None),
#                             ('first_page', None),
#                             ('first_page_engines', None),
#                             ('last_page', None),
#                             ('last_page_engines', None),
#                             ('publisher', 'Frontiers Media SA'),
#                             ('publisher_engines', ['CrossRef'])])),
#               ('url',
#                OrderedDict([('doi', 'https://doi.org/10.3389/fnhum.2013.00084'),
#                             ('doi_engines', ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('publisher',
#                              'https://doi.org/10.3389/fnhum.2013.00084'),
#                             ('publisher_engines', ['OpenAlex']),
#                             ('openurl_query', None),
#                             ('openurl_engines', None),
#                             ('openurl_resolved', []),
#                             ('openurl_resolved_engines', []),
#                             ('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('path',
#                OrderedDict([('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('system',
#                OrderedDict([('searched_by_arXiv', False),
#                             ('searched_by_CrossRef', True),
#                             ('searched_by_OpenAlex', True),
#                             ('searched_by_PubMed', True),
#                             ('searched_by_Semantic_Scholar', True),
#                             ('searched_by_URL', False)]))]),
#  OrderedDict([('id',
#                OrderedDict([('doi', '10.1371/journal.pone.0102591'),
#                             ('doi_engines', ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('arxiv_id', None),
#                             ('arxiv_id_engines', None),
#                             ('pmid', '25136855'),
#                             ('pmid_engines', ['OpenAlex', 'PubMed']),
#                             ('scholar_id', None),
#                             ('scholar_id_engines', None),
#                             ('corpus_id', 157901),
#                             ('corpus_id_engines', ['Semantic_Scholar'])])),
#               ('basic',
#                OrderedDict([('title',
#                              'A Canonical Circuit for Generating '
#                              'Phase-Amplitude Coupling'),
#                             ('title_engines', ['CrossRef', 'OpenAlex']),
#                             ('authors',
#                              ['Angela C. E. Onslow',
#                               'Matthew W. Jones',
#                               'Rafal Bogacz']),
#                             ('authors_engines', ['CrossRef']),
#                             ('year', 2014),
#                             ('year_engines',
#                              ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('abstract',
#                              '‘Phase amplitude coupling’ (PAC) in oscillatory '
#                              'neural activity describes a phenomenon whereby '
#                              'the amplitude of higher frequency activity is '
#                              'modulated by the phase of lower frequency '
#                              'activity. Such coupled oscillatory activity – '
#                              'also referred to as ‘cross-frequency coupling’ '
#                              'or ‘nested rhythms’ – has been shown to occur in '
#                              'a number of brain regions and at behaviorally '
#                              'relevant time points during cognitive tasks; '
#                              'this suggests functional relevance, but the '
#                              'circuit mechanisms of PAC generation remain '
#                              'unclear. In this paper we present a model of a '
#                              'canonical circuit for generating PAC activity, '
#                              'showing how interconnected excitatory and '
#                              'inhibitory neural populations can be '
#                              'periodically shifted in to and out of '
#                              'oscillatory firing patterns by afferent drive, '
#                              'hence generating higher frequency oscillations '
#                              'phase-locked to a lower frequency, oscillating '
#                              'input signal. Since many brain regions contain '
#                              'mutually connected excitatory-inhibitory '
#                              'populations receiving oscillatory input, the '
#                              'simplicity of the mechanism generating PAC in '
#                              'such networks may explain the ubiquity of PAC '
#                              'across diverse neural systems and behaviors. '
#                              'Analytic treatment of this circuit as a '
#                              'nonlinear dynamical system demonstrates how '
#                              'connection strengths and inputs to the '
#                              'populations can be varied in order to change the '
#                              'extent and nature of PAC activity, importantly '
#                              'which phase of the lower frequency rhythm the '
#                              'higher frequency activity is locked to. '
#                              'Consequently, this model can inform attempts to '
#                              'associate distinct types of PAC with different '
#                              'network topologies and physiologies in real '
#                              'data.'),
#                             ('abstract_engines', ['Semantic_Scholar']),
#                             ('keywords', ['Biological neural network']),
#                             ('keywords_engines', ['OpenAlex']),
#                             ('type', 'article'),
#                             ('type_engines', ['OpenAlex'])])),
#               ('citation_count',
#                OrderedDict([('total', 83),
#                             ('total_engines', ['OpenAlex']),
#                             ('2025', 1),
#                             ('2025_engines', ['OpenAlex']),
#                             ('2024', 5),
#                             ('2024_engines', ['OpenAlex']),
#                             ('2023', 8),
#                             ('2023_engines', ['OpenAlex']),
#                             ('2022', 5),
#                             ('2022_engines', ['OpenAlex']),
#                             ('2021', 13),
#                             ('2021_engines', ['OpenAlex']),
#                             ('2020', 13),
#                             ('2020_engines', ['OpenAlex']),
#                             ('2019', 13),
#                             ('2019_engines', ['OpenAlex']),
#                             ('2018', 5),
#                             ('2018_engines', ['OpenAlex']),
#                             ('2017', 8),
#                             ('2017_engines', ['OpenAlex']),
#                             ('2016', 5),
#                             ('2016_engines', ['OpenAlex']),
#                             ('2015', 7),
#                             ('2015_engines', ['OpenAlex'])])),
#               ('publication',
#                OrderedDict([('journal', 'PLoS ONE'),
#                             ('journal_engines', ['CrossRef']),
#                             ('short_journal', 'PLoS ONE'),
#                             ('short_journal_engines', ['CrossRef']),
#                             ('impact_factor', None),
#                             ('impact_factor_engines', None),
#                             ('issn', '1932-6203'),
#                             ('issn_engines', ['CrossRef', 'PubMed']),
#                             ('volume', '9'),
#                             ('volume_engines',
#                              ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('issue', '8'),
#                             ('issue_engines',
#                              ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('first_page', 'e102591'),
#                             ('first_page_engines', ['OpenAlex']),
#                             ('last_page', 'e102591'),
#                             ('last_page_engines', ['OpenAlex']),
#                             ('publisher', 'Public Library of Science (PLoS)'),
#                             ('publisher_engines', ['CrossRef'])])),
#               ('url',
#                OrderedDict([('doi',
#                              'https://doi.org/10.1371/journal.pone.0102591'),
#                             ('doi_engines', ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('publisher',
#                              'https://doi.org/10.1371/journal.pone.0102591'),
#                             ('publisher_engines', ['OpenAlex']),
#                             ('openurl_query', None),
#                             ('openurl_engines', None),
#                             ('openurl_resolved', []),
#                             ('openurl_resolved_engines', []),
#                             ('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('path',
#                OrderedDict([('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('system',
#                OrderedDict([('searched_by_arXiv', False),
#                             ('searched_by_CrossRef', True),
#                             ('searched_by_OpenAlex', True),
#                             ('searched_by_PubMed', True),
#                             ('searched_by_Semantic_Scholar', True),
#                             ('searched_by_URL', False)]))]),
#  OrderedDict([('id',
#                OrderedDict([('doi', '10.1371/journal.pcbi.1008302'),
#                             ('doi_engines', ['OpenAlex', 'PubMed']),
#                             ('arxiv_id', None),
#                             ('arxiv_id_engines', None),
#                             ('pmid', '33119593'),
#                             ('pmid_engines', ['OpenAlex', 'PubMed']),
#                             ('scholar_id', None),
#                             ('scholar_id_engines', None),
#                             ('corpus_id', 216071804),
#                             ('corpus_id_engines', ['Semantic_Scholar'])])),
#               ('basic',
#                OrderedDict([('title',
#                              'Tensorpac : an open-source Python toolbox for '
#                              'tensor-based Phase-Amplitude Coupling '
#                              'measurement in electrophysiological brain '
#                              'signals'),
#                             ('title_engines', ['CrossRef']),
#                             ('authors',
#                              ['Etienne Combrisson',
#                               'Timothy Nest',
#                               'Andrea Brovelli',
#                               'Robin A.A. Ince',
#                               'Juan LP Soto',
#                               'Aymeric Guillot',
#                               'Karim Jerbi']),
#                             ('authors_engines', ['CrossRef']),
#                             ('year', 2020),
#                             ('year_engines', ['OpenAlex', 'PubMed']),
#                             ('abstract',
#                              '<jats:title>Abstract</jats:title><jats:p>Despite '
#                              'being the focus of a thriving field of research, '
#                              'the biological mechanisms that underlie '
#                              'information integration in the brain are not yet '
#                              'fully understood. A theory that has gained a lot '
#                              'of traction in recent years suggests that '
#                              'multi-scale integration is regulated by a '
#                              'hierarchy of mutually interacting neural '
#                              'oscillations. In particular, there is '
#                              'accumulating evidence that phase-amplitude '
#                              'coupling (PAC), a specific form of '
#                              'cross-frequency interaction, plays a key role in '
#                              'numerous cognitive processes. Current research '
#                              'in the field is not only hampered by the absence '
#                              'of a gold standard for PAC analysis, but also by '
#                              'the computational costs of running exhaustive '
#                              'computations on large and high-dimensional '
#                              'electrophysiological brain signals. In addition, '
#                              'various signal properties and analyses '
#                              'parameters can lead to spurious PAC. Here, we '
#                              'present Tensorpac, an open-source Python toolbox '
#                              'dedicated to PAC analysis of neurophysiological '
#                              'data. The advantages of Tensorpac include (1) '
#                              'higher computational efficiency thanks to '
#                              'software design that combines tensor '
#                              'computations and parallel computing, (2) the '
#                              'implementation of all most widely used PAC '
#                              'methods in one package, (3) the statistical '
#                              'analysis of PAC measures, and (4) extended PAC '
#                              'visualization capabilities. Tensorpac is '
#                              'distributed under a BSD-3-Clause license and can '
#                              'be launched on any operating system (Linux, OSX '
#                              'and Windows). It can be installed directly via '
#                              'pip or downloaded from Github (<jats:ext-link '
#                              'xmlns:xlink="http://www.w3.org/1999/xlink" '
#                              'ext-link-type="uri" '
#                              'xlink:href="https://github.com/EtienneCmb/tensorpac">https://github.com/EtienneCmb/tensorpac</jats:ext-link>). '
#                              'By making Tensorpac available, we aim to enhance '
#                              'the reproducibility and quality of PAC research, '
#                              'and provide open tools that will accelerate '
#                              'future method development in '
#                              'neuroscience.</jats:p>'),
#                             ('abstract_engines', ['CrossRef']),
#                             ('keywords',
#                              ['Python',
#                               'Toolbox',
#                               'Spurious relationship',
#                               'Computational neuroscience']),
#                             ('keywords_engines', ['OpenAlex']),
#                             ('type', 'article'),
#                             ('type_engines', ['OpenAlex'])])),
#               ('citation_count',
#                OrderedDict([('total', 62),
#                             ('total_engines', ['OpenAlex']),
#                             ('2025', 12),
#                             ('2025_engines', ['OpenAlex']),
#                             ('2024', 16),
#                             ('2024_engines', ['OpenAlex']),
#                             ('2023', 11),
#                             ('2023_engines', ['OpenAlex']),
#                             ('2022', 10),
#                             ('2022_engines', ['OpenAlex']),
#                             ('2021', 9),
#                             ('2021_engines', ['OpenAlex']),
#                             ('2020', 1),
#                             ('2020_engines', ['OpenAlex']),
#                             ('2019', None),
#                             ('2019_engines', None),
#                             ('2018', None),
#                             ('2018_engines', None),
#                             ('2017', None),
#                             ('2017_engines', None),
#                             ('2016', None),
#                             ('2016_engines', None),
#                             ('2015', None),
#                             ('2015_engines', None)])),
#               ('publication',
#                OrderedDict([('journal', 'PLoS computational biology'),
#                             ('journal_engines', ['PubMed']),
#                             ('short_journal', 'PLoS Comput Biol'),
#                             ('short_journal_engines', ['PubMed']),
#                             ('impact_factor', None),
#                             ('impact_factor_engines', None),
#                             ('issn', '1553-7358'),
#                             ('issn_engines', ['PubMed']),
#                             ('volume', '16'),
#                             ('volume_engines', ['OpenAlex', 'PubMed']),
#                             ('issue', '10'),
#                             ('issue_engines', ['OpenAlex', 'PubMed']),
#                             ('first_page', 'e1008302'),
#                             ('first_page_engines', ['OpenAlex']),
#                             ('last_page', 'e1008302'),
#                             ('last_page_engines', ['OpenAlex']),
#                             ('publisher', 'Cold Spring Harbor Laboratory'),
#                             ('publisher_engines', ['CrossRef'])])),
#               ('url',
#                OrderedDict([('doi',
#                              'https://doi.org/10.1371/journal.pcbi.1008302'),
#                             ('doi_engines', ['OpenAlex', 'PubMed']),
#                             ('publisher',
#                              'https://doi.org/10.1371/journal.pcbi.1008302'),
#                             ('publisher_engines', ['OpenAlex']),
#                             ('openurl_query', None),
#                             ('openurl_engines', None),
#                             ('openurl_resolved', []),
#                             ('openurl_resolved_engines', []),
#                             ('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('path',
#                OrderedDict([('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('system',
#                OrderedDict([('searched_by_arXiv', False),
#                             ('searched_by_CrossRef', True),
#                             ('searched_by_OpenAlex', True),
#                             ('searched_by_PubMed', True),
#                             ('searched_by_Semantic_Scholar', True),
#                             ('searched_by_URL', False)]))]),
#  OrderedDict([('id',
#                OrderedDict([('doi', '10.3389/fnhum.2013.00084'),
#                             ('doi_engines', ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('arxiv_id', None),
#                             ('arxiv_id_engines', None),
#                             ('pmid', '23532592'),
#                             ('pmid_engines', ['OpenAlex', 'PubMed']),
#                             ('scholar_id', None),
#                             ('scholar_id_engines', None),
#                             ('corpus_id', 14588601),
#                             ('corpus_id_engines', ['Semantic_Scholar'])])),
#               ('basic',
#                OrderedDict([('title',
#                              'Cross-frequency coupling within and between the '
#                              'human thalamus and neocortex'),
#                             ('title_engines',
#                              ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('authors',
#                              ['Thomas H B Fitzgerald',
#                               'Antonio Valentin',
#                               'Richard Selway',
#                               'Mark P Richardson']),
#                             ('authors_engines', ['PubMed']),
#                             ('year', 2013),
#                             ('year_engines',
#                              ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('abstract',
#                              'There is currently growing interest in, and '
#                              'increasing evidence for, cross-frequency '
#                              'interactions between electrical field '
#                              'oscillations in the brains of various organisms. '
#                              'A number of theories have linked such '
#                              'interactions to crucial features of neuronal '
#                              'function and cognition. In mammals, these '
#                              'interactions have mostly been reported in the '
#                              'neocortex and hippocampus, and it remains '
#                              'unexplored whether similar patterns of activity '
#                              'occur in the thalamus, and between the thalamus '
#                              'and neocortex. Here we use data recorded from '
#                              'patients undergoing thalamic deep-brain '
#                              'stimulation for epilepsy to demonstrate the '
#                              'existence and prevalence, across a range of '
#                              'frequencies, of both phase–amplitude (PAC) and '
#                              'amplitude–amplitude coupling (AAC) both within '
#                              'the thalamus and prefrontal cortex (PFC), and '
#                              'between them. These cross-frequency interactions '
#                              'may play an important role in local processing '
#                              'within the thalamus and neocortex, as well as '
#                              'information transfer between them.'),
#                             ('abstract_engines', ['Semantic_Scholar']),
#                             ('keywords',
#                              ['Neocortex', 'Local field potential']),
#                             ('keywords_engines', ['OpenAlex']),
#                             ('type', 'article'),
#                             ('type_engines', ['OpenAlex'])])),
#               ('citation_count',
#                OrderedDict([('total', 62),
#                             ('total_engines', ['OpenAlex']),
#                             ('2025', 1),
#                             ('2025_engines', ['OpenAlex']),
#                             ('2024', 8),
#                             ('2024_engines', ['OpenAlex']),
#                             ('2023', 3),
#                             ('2023_engines', ['OpenAlex']),
#                             ('2022', 3),
#                             ('2022_engines', ['OpenAlex']),
#                             ('2021', 5),
#                             ('2021_engines', ['OpenAlex']),
#                             ('2020', 4),
#                             ('2020_engines', ['OpenAlex']),
#                             ('2019', 4),
#                             ('2019_engines', ['OpenAlex']),
#                             ('2018', 6),
#                             ('2018_engines', ['OpenAlex']),
#                             ('2017', 8),
#                             ('2017_engines', ['OpenAlex']),
#                             ('2016', 9),
#                             ('2016_engines', ['OpenAlex']),
#                             ('2015', 3),
#                             ('2015_engines', ['OpenAlex']),
#                             ('2014_engines', ['OpenAlex']),
#                             ('2014', 6),
#                             ('2013_engines', ['OpenAlex']),
#                             ('2013', 2)])),
#               ('publication',
#                OrderedDict([('journal', 'Frontiers in Human Neuroscience'),
#                             ('journal_engines', ['CrossRef']),
#                             ('short_journal', 'Front. Hum. Neurosci.'),
#                             ('short_journal_engines', ['CrossRef']),
#                             ('impact_factor', None),
#                             ('impact_factor_engines', None),
#                             ('issn', '1662-5161'),
#                             ('issn_engines', ['CrossRef', 'PubMed']),
#                             ('volume', '7'),
#                             ('volume_engines',
#                              ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('issue', None),
#                             ('issue_engines', None),
#                             ('first_page', None),
#                             ('first_page_engines', None),
#                             ('last_page', None),
#                             ('last_page_engines', None),
#                             ('publisher', 'Frontiers Media SA'),
#                             ('publisher_engines', ['CrossRef'])])),
#               ('url',
#                OrderedDict([('doi', 'https://doi.org/10.3389/fnhum.2013.00084'),
#                             ('doi_engines', ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('publisher',
#                              'https://doi.org/10.3389/fnhum.2013.00084'),
#                             ('publisher_engines', ['OpenAlex']),
#                             ('openurl_query', None),
#                             ('openurl_engines', None),
#                             ('openurl_resolved', []),
#                             ('openurl_resolved_engines', []),
#                             ('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('path',
#                OrderedDict([('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('system',
#                OrderedDict([('searched_by_arXiv', False),
#                             ('searched_by_CrossRef', True),
#                             ('searched_by_OpenAlex', True),
#                             ('searched_by_PubMed', True),
#                             ('searched_by_Semantic_Scholar', True),
#                             ('searched_by_URL', False)]))]),
#  OrderedDict([('id',
#                OrderedDict([('doi', '10.3389/fnins.2019.00573'),
#                             ('doi_engines', ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('arxiv_id', None),
#                             ('arxiv_id_engines', None),
#                             ('pmid', '31275096'),
#                             ('pmid_engines', ['OpenAlex', 'PubMed']),
#                             ('scholar_id', None),
#                             ('scholar_id_engines', None),
#                             ('corpus_id', 182003214),
#                             ('corpus_id_engines', ['Semantic_Scholar'])])),
#               ('basic',
#                OrderedDict([('title',
#                              'Quantification of Phase-Amplitude Coupling in '
#                              'Neuronal Oscillations: Comparison of '
#                              'Phase-Locking Value, Mean Vector Length, '
#                              'Modulation Index, and '
#                              'Generalized-Linear-Modeling-Cross-Frequency-Coupling'),
#                             ('title_engines',
#                              ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('authors',
#                              ['Mareike J. Hülsemann',
#                               'Ewald Naumann',
#                               'Björn Rasch']),
#                             ('authors_engines', ['CrossRef', 'OpenAlex']),
#                             ('year', 2019),
#                             ('year_engines',
#                              ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('abstract',
#                              'Phase-amplitude coupling is a promising '
#                              'construct to study cognitive processes in '
#                              'electroencephalography (EEG) and '
#                              'magnetencephalography (MEG). Due to the novelty '
#                              'of the concept, various measures are used in the '
#                              'literature to calculate phase-amplitude '
#                              'coupling. Here, performance of the three most '
#                              'widely used phase-amplitude coupling measures – '
#                              'phase-locking value (PLV), mean vector length '
#                              '(MVL), and modulation index (MI) – and of the '
#                              'generalized linear modeling cross-frequency '
#                              'coupling (GLM-CFC) method is thoroughly compared '
#                              'with the help of simulated data. We combine '
#                              'advantages of previous reviews and use a '
#                              'realistic data simulation, examine moderators '
#                              'and provide inferential statistics for the '
#                              'comparison of all four indices of '
#                              'phase-amplitude coupling. Our analyses show that '
#                              'all four indices successfully differentiate '
#                              'coupling strength and coupling width when '
#                              'monophasic coupling is present. While the MVL '
#                              'was most sensitive to modulations in coupling '
#                              'strengths and width, only the MI and GLM-CFC can '
#                              'detect biphasic coupling. Coupling values of all '
#                              'four indices were influenced by moderators '
#                              'including data length, signal-to-noise-ratio, '
#                              'and sampling rate when approaching Nyquist '
#                              'frequencies. The MI was most robust against '
#                              'confounding influences of these moderators. '
#                              'Based on our analyses, we recommend the MI for '
#                              'noisy and short data epochs with unknown forms '
#                              'of coupling. For high quality and long data '
#                              'epochs with monophasic coupling and a high '
#                              'signal-to-noise ratio, the use of the MVL is '
#                              'recommended. Ideally, both indices are reported '
#                              'simultaneously for one data set.'),
#                             ('abstract_engines', ['Semantic_Scholar']),
#                             ('keywords', None),
#                             ('keywords_engines', None),
#                             ('type', 'article'),
#                             ('type_engines', ['OpenAlex'])])),
#               ('citation_count',
#                OrderedDict([('total', 158),
#                             ('total_engines', ['OpenAlex']),
#                             ('2025', 21),
#                             ('2025_engines', ['OpenAlex']),
#                             ('2024', 30),
#                             ('2024_engines', ['OpenAlex']),
#                             ('2023', 29),
#                             ('2023_engines', ['OpenAlex']),
#                             ('2022', 29),
#                             ('2022_engines', ['OpenAlex']),
#                             ('2021', 31),
#                             ('2021_engines', ['OpenAlex']),
#                             ('2020', 12),
#                             ('2020_engines', ['OpenAlex']),
#                             ('2019', 3),
#                             ('2019_engines', ['OpenAlex']),
#                             ('2018', 1),
#                             ('2018_engines', ['OpenAlex']),
#                             ('2017', None),
#                             ('2017_engines', None),
#                             ('2016', None),
#                             ('2016_engines', None),
#                             ('2015', None),
#                             ('2015_engines', None)])),
#               ('publication',
#                OrderedDict([('journal', 'Frontiers in Neuroscience'),
#                             ('journal_engines', ['CrossRef']),
#                             ('short_journal', 'Front. Neurosci.'),
#                             ('short_journal_engines', ['CrossRef']),
#                             ('impact_factor', None),
#                             ('impact_factor_engines', None),
#                             ('issn', '1662-453X'),
#                             ('issn_engines', ['CrossRef']),
#                             ('volume', '13'),
#                             ('volume_engines',
#                              ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('issue', None),
#                             ('issue_engines', None),
#                             ('first_page', None),
#                             ('first_page_engines', None),
#                             ('last_page', None),
#                             ('last_page_engines', None),
#                             ('publisher', 'Frontiers Media SA'),
#                             ('publisher_engines', ['CrossRef'])])),
#               ('url',
#                OrderedDict([('doi', 'https://doi.org/10.3389/fnins.2019.00573'),
#                             ('doi_engines', ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('publisher',
#                              'https://doi.org/10.3389/fnins.2019.00573'),
#                             ('publisher_engines', ['OpenAlex']),
#                             ('openurl_query', None),
#                             ('openurl_engines', None),
#                             ('openurl_resolved', []),
#                             ('openurl_resolved_engines', []),
#                             ('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('path',
#                OrderedDict([('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('system',
#                OrderedDict([('searched_by_arXiv', False),
#                             ('searched_by_CrossRef', True),
#                             ('searched_by_OpenAlex', True),
#                             ('searched_by_PubMed', True),
#                             ('searched_by_Semantic_Scholar', True),
#                             ('searched_by_URL', False)]))]),
#  OrderedDict([('id',
#                OrderedDict([('doi', '10.1038/s41598-019-48870-2'),
#                             ('doi_engines', ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('arxiv_id', None),
#                             ('arxiv_id_engines', None),
#                             ('pmid', '31455811'),
#                             ('pmid_engines', ['OpenAlex', 'PubMed']),
#                             ('scholar_id', None),
#                             ('scholar_id_engines', None),
#                             ('corpus_id', 201651743),
#                             ('corpus_id_engines', ['Semantic_Scholar'])])),
#               ('basic',
#                OrderedDict([('title',
#                              'Time-Frequency Based Phase-Amplitude Coupling '
#                              'Measure For Neuronal Oscillations'),
#                             ('title_engines',
#                              ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('authors',
#                              ['Tamanna T. K. Munia', 'Selin Aviyente']),
#                             ('authors_engines', ['CrossRef', 'OpenAlex']),
#                             ('year', 2019),
#                             ('year_engines',
#                              ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('abstract',
#                              '<jats:title>Abstract</jats:title><jats:p>Oscillatory '
#                              'activity in the brain has been associated with a '
#                              'wide variety of cognitive processes including '
#                              'decision making, feedback processing, and '
#                              'working memory. The high temporal resolution '
#                              'provided by electroencephalography (EEG) enables '
#                              'the study of variation of oscillatory power and '
#                              'coupling across time. Various forms of neural '
#                              'synchrony across frequency bands have been '
#                              'suggested as the mechanism underlying neural '
#                              'binding. Recently, a considerable amount of work '
#                              'has focused on phase-amplitude coupling (PAC)– a '
#                              'form of cross-frequency coupling where the '
#                              'amplitude of a high frequency signal is '
#                              'modulated by the phase of low frequency '
#                              'oscillations. The existing methods for assessing '
#                              'PAC have some limitations including limited '
#                              'frequency resolution and sensitivity to noise, '
#                              'data length and sampling rate due to the '
#                              'inherent dependence on bandpass filtering. In '
#                              'this paper, we propose a new time-frequency '
#                              'based PAC (t-f PAC) measure that can address '
#                              'these issues. The proposed method relies on a '
#                              'complex time-frequency distribution, known as '
#                              'the Reduced Interference Distribution '
#                              '(RID)-Rihaczek distribution, to estimate both '
#                              'the phase and the envelope of low and high '
#                              'frequency oscillations, respectively. As such, '
#                              'it does not rely on bandpass filtering and '
#                              'possesses some of the desirable properties of '
#                              'time-frequency distributions such as high '
#                              'frequency resolution. The proposed technique is '
#                              'first evaluated for simulated data and then '
#                              'applied to an EEG speeded reaction task dataset. '
#                              'The results illustrate that the proposed '
#                              'time-frequency based PAC is more robust to '
#                              'varying signal parameters and provides a more '
#                              'accurate measure of coupling strength.</jats:p>'),
#                             ('abstract_engines', ['CrossRef']),
#                             ('keywords',
#                              ['SIGNAL (programming language)',
#                               'Envelope (radar)',
#                               'Instantaneous phase']),
#                             ('keywords_engines', ['OpenAlex']),
#                             ('type', 'article'),
#                             ('type_engines', ['OpenAlex'])])),
#               ('citation_count',
#                OrderedDict([('total', 99),
#                             ('total_engines', ['OpenAlex']),
#                             ('2025', 5),
#                             ('2025_engines', ['OpenAlex']),
#                             ('2024', 38),
#                             ('2024_engines', ['OpenAlex']),
#                             ('2023', 15),
#                             ('2023_engines', ['OpenAlex']),
#                             ('2022', 19),
#                             ('2022_engines', ['OpenAlex']),
#                             ('2021', 13),
#                             ('2021_engines', ['OpenAlex']),
#                             ('2020', 7),
#                             ('2020_engines', ['OpenAlex']),
#                             ('2019', 1),
#                             ('2019_engines', ['OpenAlex']),
#                             ('2018', None),
#                             ('2018_engines', None),
#                             ('2017', None),
#                             ('2017_engines', None),
#                             ('2016', None),
#                             ('2016_engines', None),
#                             ('2015', None),
#                             ('2015_engines', None)])),
#               ('publication',
#                OrderedDict([('journal', 'Scientific Reports'),
#                             ('journal_engines', ['CrossRef']),
#                             ('short_journal', 'Sci Rep'),
#                             ('short_journal_engines', ['CrossRef', 'PubMed']),
#                             ('impact_factor', None),
#                             ('impact_factor_engines', None),
#                             ('issn', '2045-2322'),
#                             ('issn_engines', ['CrossRef', 'PubMed']),
#                             ('volume', '9'),
#                             ('volume_engines',
#                              ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('issue', '1'),
#                             ('issue_engines',
#                              ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('first_page', None),
#                             ('first_page_engines', None),
#                             ('last_page', None),
#                             ('last_page_engines', None),
#                             ('publisher',
#                              'Springer Science and Business Media LLC'),
#                             ('publisher_engines', ['CrossRef'])])),
#               ('url',
#                OrderedDict([('doi',
#                              'https://doi.org/10.1038/s41598-019-48870-2'),
#                             ('doi_engines', ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('publisher',
#                              'https://doi.org/10.1038/s41598-019-48870-2'),
#                             ('publisher_engines', ['OpenAlex']),
#                             ('openurl_query', None),
#                             ('openurl_engines', None),
#                             ('openurl_resolved', []),
#                             ('openurl_resolved_engines', []),
#                             ('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('path',
#                OrderedDict([('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('system',
#                OrderedDict([('searched_by_arXiv', False),
#                             ('searched_by_CrossRef', True),
#                             ('searched_by_OpenAlex', True),
#                             ('searched_by_PubMed', True),
#                             ('searched_by_Semantic_Scholar', True),
#                             ('searched_by_URL', False)]))]),
#  OrderedDict([('id',
#                OrderedDict([('doi', '10.3389/fnins.2017.00487'),
#                             ('doi_engines', ['OpenAlex', 'PubMed']),
#                             ('arxiv_id', None),
#                             ('arxiv_id_engines', None),
#                             ('pmid', '28919850'),
#                             ('pmid_engines', ['OpenAlex', 'PubMed']),
#                             ('scholar_id', None),
#                             ('scholar_id_engines', None),
#                             ('corpus_id', 19922713),
#                             ('corpus_id_engines', ['Semantic_Scholar'])])),
#               ('basic',
#                OrderedDict([('title',
#                              'The Detection of Phase Amplitude Coupling During '
#                              'Sensory Processing'),
#                             ('title_engines', ['CrossRef']),
#                             ('authors',
#                              ['R.A Seymour', 'G. Rippon', 'K. Kessler']),
#                             ('authors_engines', ['CrossRef']),
#                             ('year', 2017),
#                             ('year_engines', ['OpenAlex', 'PubMed']),
#                             ('abstract',
#                              '<jats:label>1.</jats:label><jats:title>Abstract</jats:title><jats:p>There '
#                              'is increasing interest in understanding how the '
#                              'phase and amplitude of distinct neural '
#                              'oscillations might interact to support dynamic '
#                              'communication within the brain. In particular, '
#                              'previous work has demonstrated a coupling '
#                              'between the phase of low frequency oscillations '
#                              'and the amplitude (or power) of high frequency '
#                              'oscillations during certain tasks, termed phase '
#                              'amplitude coupling (PAC). For instance, during '
#                              'visual processing in humans, PAC has been '
#                              'reliably observed between ongoing alpha (8-13Hz) '
#                              'and gamma-band (&gt;40Hz) activity. However, the '
#                              'application of PAC metrics to '
#                              'electrophysiological data can be challenging due '
#                              'to numerous methodological issues and lack of '
#                              'coherent approaches within the field. Therefore, '
#                              'in this article we outline the various analysis '
#                              'steps involved in detecting PAC, using an openly '
#                              'available MEG dataset from 16 participants '
#                              'performing an interactive visual task. Firstly, '
#                              'we localised gamma and alpha-band power using '
#                              'the Fieldtrip toolbox, and extracted time '
#                              'courses from area V1, defined using a multimodal '
#                              'parcellation scheme. These V1 responses were '
#                              'analysed for changes in alpha-gamma PAC, using '
#                              'four common algorithms. Results showed an '
#                              'increase in gamma (40-100Hz) - alpha (7-13Hz) '
#                              'PAC in response to the visual grating stimulus, '
#                              'though specific patterns of coupling were '
#                              'somewhat dependent upon the algorithm employed. '
#                              'Additionally, post-hoc analyses showed that '
#                              'these results were not driven by the presence of '
#                              'non-sinusoidal oscillations, and that trial '
#                              'length was sufficient to obtain reliable PAC '
#                              'estimates. Finally, throughout the article, '
#                              'methodological issues and practical guidelines '
#                              'for ongoing PAC research will be '
#                              'discussed.</jats:p>'),
#                             ('abstract_engines', ['CrossRef']),
#                             ('keywords',
#                              ['Toolbox',
#                               'Local field potential',
#                               'Sensory Processing',
#                               'Stimulus (psychology)']),
#                             ('keywords_engines', ['OpenAlex']),
#                             ('type', 'article'),
#                             ('type_engines', ['OpenAlex'])])),
#               ('citation_count',
#                OrderedDict([('total', 76),
#                             ('total_engines', ['OpenAlex']),
#                             ('2025', 7),
#                             ('2025_engines', ['OpenAlex']),
#                             ('2024', 7),
#                             ('2024_engines', ['OpenAlex']),
#                             ('2023', 6),
#                             ('2023_engines', ['OpenAlex']),
#                             ('2022', 9),
#                             ('2022_engines', ['OpenAlex']),
#                             ('2021', 17),
#                             ('2021_engines', ['OpenAlex']),
#                             ('2020', 14),
#                             ('2020_engines', ['OpenAlex']),
#                             ('2019', 9),
#                             ('2019_engines', ['OpenAlex']),
#                             ('2018', 6),
#                             ('2018_engines', ['OpenAlex']),
#                             ('2017', None),
#                             ('2017_engines', None),
#                             ('2016', None),
#                             ('2016_engines', None),
#                             ('2015', None),
#                             ('2015_engines', None)])),
#               ('publication',
#                OrderedDict([('journal', 'Frontiers in neuroscience'),
#                             ('journal_engines', ['PubMed']),
#                             ('short_journal', 'Front Neurosci'),
#                             ('short_journal_engines', ['PubMed']),
#                             ('impact_factor', None),
#                             ('impact_factor_engines', None),
#                             ('issn', '1662-4548'),
#                             ('issn_engines', ['PubMed']),
#                             ('volume', '11'),
#                             ('volume_engines', ['OpenAlex', 'PubMed']),
#                             ('issue', None),
#                             ('issue_engines', None),
#                             ('first_page', None),
#                             ('first_page_engines', None),
#                             ('last_page', None),
#                             ('last_page_engines', None),
#                             ('publisher', 'Cold Spring Harbor Laboratory'),
#                             ('publisher_engines', ['CrossRef'])])),
#               ('url',
#                OrderedDict([('doi', 'https://doi.org/10.3389/fnins.2017.00487'),
#                             ('doi_engines', ['OpenAlex', 'PubMed']),
#                             ('publisher',
#                              'https://doi.org/10.3389/fnins.2017.00487'),
#                             ('publisher_engines', ['OpenAlex']),
#                             ('openurl_query', None),
#                             ('openurl_engines', None),
#                             ('openurl_resolved', []),
#                             ('openurl_resolved_engines', []),
#                             ('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('path',
#                OrderedDict([('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('system',
#                OrderedDict([('searched_by_arXiv', False),
#                             ('searched_by_CrossRef', True),
#                             ('searched_by_OpenAlex', True),
#                             ('searched_by_PubMed', True),
#                             ('searched_by_Semantic_Scholar', True),
#                             ('searched_by_URL', False)]))]),
#  OrderedDict([('id',
#                OrderedDict([('doi', '10.1371/journal.pcbi.1005180'),
#                             ('doi_engines', ['OpenAlex']),
#                             ('arxiv_id', None),
#                             ('arxiv_id_engines', None),
#                             ('pmid', '27802274'),
#                             ('pmid_engines', ['OpenAlex']),
#                             ('scholar_id', None),
#                             ('scholar_id_engines', None),
#                             ('corpus_id', 3626970),
#                             ('corpus_id_engines', ['Semantic_Scholar'])])),
#               ('basic',
#                OrderedDict([('title',
#                              'Topology, cross-frequency, and same-frequency '
#                              'band interactions shape the generation of '
#                              'phase-amplitude coupling in a neural mass model '
#                              'of a cortical column'),
#                             ('title_engines', ['CrossRef']),
#                             ('authors', ['Roberto C. Sotero']),
#                             ('authors_engines', ['CrossRef', 'OpenAlex']),
#                             ('year', 2016),
#                             ('year_engines', ['OpenAlex']),
#                             ('abstract',
#                              '<jats:title>Abstract</jats:title><jats:p>Phase-amplitude '
#                              'coupling (PAC), a type of cross-frequency '
#                              'coupling (CFC) where the phase of a '
#                              'low-frequency rhythm modulates the amplitude of '
#                              'a higher frequency, is becoming an important '
#                              'indicator of information transmission in the '
#                              'brain. However, the neurobiological mechanisms '
#                              'underlying its generation remain undetermined. A '
#                              'realistic, yet tractable computational model of '
#                              'the phenomenon is thus needed. Here we propose a '
#                              'neural mass model of a cortical column, '
#                              'comprising fourteen neuronal populations '
#                              'distributed across four layers (L2/3, L4, L5 and '
#                              'L6). The conditional transfer entropies (cTE) '
#                              'from the phases to the amplitudes of the '
#                              'generated oscillations are estimated by means of '
#                              'the conditional mutual information. This '
#                              'approach provides information regarding '
#                              'directionality by distinguishing PAC from APC '
#                              '(amplitude-phase coupling), i.e. the information '
#                              'transfer from amplitudes to phases, and can be '
#                              'used to estimate other types of CFC such as '
#                              'amplitude-amplitude coupling (AAC) and '
#                              'phase-phase coupling (PPC). While experiments '
#                              'often only focus on one or two PAC combinations '
#                              '(e.g., theta-gamma or alpha-gamma), we found '
#                              'that a cortical column can simultaneously '
#                              'generate almost all possible PAC combinations, '
#                              'depending on connectivity parameters, time '
#                              'constants, and external inputs. We found that '
#                              'the strength of PAC between two populations was '
#                              'strongly correlated with the strength of the '
#                              'effective connections between them and, on '
#                              'average, did not depend upon the presence or '
#                              'absence of a direct (anatomical) connection. '
#                              'When considering a cortical column circuit as a '
#                              'complex network, we found that neuronal '
#                              'populations making indirect PAC connections had, '
#                              'on average, higher local clustering coefficient, '
#                              'efficiency, and betweenness centrality than '
#                              'populations making direct connections and '
#                              'populations not involved in PAC connections. '
#                              'This suggests that their interactions were more '
#                              'efficient when transmitting information. Since '
#                              'more than 60% of the obtained interactions '
#                              'represented indirect connections, our results '
#                              'highlight the importance of the topology of '
#                              'cortical circuits for the generation on of the '
#                              'PAC phenomenon. Finally, our results '
#                              'demonstrated that indirect PAC interactions can '
#                              'be explained by a cascade of direct CFC and '
#                              'same-frequency band interactions, suggesting '
#                              'that PAC analysis of experimental data should be '
#                              'accompanied by the estimation of other types of '
#                              'frequency interactions for an integrative '
#                              'understanding of the phenomenon.</jats:p>'),
#                             ('abstract_engines', ['CrossRef']),
#                             ('keywords', None),
#                             ('keywords_engines', None),
#                             ('type', 'article'),
#                             ('type_engines', ['OpenAlex'])])),
#               ('citation_count',
#                OrderedDict([('total', 36),
#                             ('total_engines', ['OpenAlex']),
#                             ('2025', 2),
#                             ('2025_engines', ['OpenAlex']),
#                             ('2024', 6),
#                             ('2024_engines', ['OpenAlex']),
#                             ('2023', 3),
#                             ('2023_engines', ['OpenAlex']),
#                             ('2022', 4),
#                             ('2022_engines', ['OpenAlex']),
#                             ('2021', 2),
#                             ('2021_engines', ['OpenAlex']),
#                             ('2020', 3),
#                             ('2020_engines', ['OpenAlex']),
#                             ('2019', 11),
#                             ('2019_engines', ['OpenAlex']),
#                             ('2018', 3),
#                             ('2018_engines', ['OpenAlex']),
#                             ('2017', 2),
#                             ('2017_engines', ['OpenAlex']),
#                             ('2016', None),
#                             ('2016_engines', None),
#                             ('2015', None),
#                             ('2015_engines', None)])),
#               ('publication',
#                OrderedDict([('journal', 'bioRxiv'),
#                             ('journal_engines', ['Semantic_Scholar']),
#                             ('short_journal', None),
#                             ('short_journal_engines', None),
#                             ('impact_factor', None),
#                             ('impact_factor_engines', None),
#                             ('issn', None),
#                             ('issn_engines', None),
#                             ('volume', '12'),
#                             ('volume_engines', ['OpenAlex']),
#                             ('issue', '11'),
#                             ('issue_engines', ['OpenAlex']),
#                             ('first_page', 'e1005180'),
#                             ('first_page_engines', ['OpenAlex']),
#                             ('last_page', 'e1005180'),
#                             ('last_page_engines', ['OpenAlex']),
#                             ('publisher', 'Cold Spring Harbor Laboratory'),
#                             ('publisher_engines', ['CrossRef'])])),
#               ('url',
#                OrderedDict([('doi',
#                              'https://doi.org/10.1371/journal.pcbi.1005180'),
#                             ('doi_engines', ['OpenAlex']),
#                             ('publisher',
#                              'https://doi.org/10.1371/journal.pcbi.1005180'),
#                             ('publisher_engines', ['OpenAlex']),
#                             ('openurl_query', None),
#                             ('openurl_engines', None),
#                             ('openurl_resolved', []),
#                             ('openurl_resolved_engines', []),
#                             ('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('path',
#                OrderedDict([('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('system',
#                OrderedDict([('searched_by_arXiv', False),
#                             ('searched_by_CrossRef', True),
#                             ('searched_by_OpenAlex', True),
#                             ('searched_by_PubMed', False),
#                             ('searched_by_Semantic_Scholar', True),
#                             ('searched_by_URL', False)]))]),
#  OrderedDict([('id',
#                OrderedDict([('doi', '10.1371/journal.pcbi.1010942'),
#                             ('doi_engines', ['CrossRef', 'OpenAlex']),
#                             ('arxiv_id', None),
#                             ('arxiv_id_engines', None),
#                             ('pmid', '36952558'),
#                             ('pmid_engines', ['OpenAlex']),
#                             ('scholar_id', None),
#                             ('scholar_id_engines', None),
#                             ('corpus_id', 257717129),
#                             ('corpus_id_engines', ['Semantic_Scholar'])])),
#               ('basic',
#                OrderedDict([('title',
#                              'Theta-gamma phase amplitude coupling in a '
#                              'hippocampal CA1 microcircuit'),
#                             ('title_engines', ['CrossRef', 'OpenAlex']),
#                             ('authors',
#                              ['Adam Ponzi',
#                               'Salvador Dura-Bernal',
#                               'Michele Migliore']),
#                             ('authors_engines', ['CrossRef']),
#                             ('year', 2023),
#                             ('year_engines', ['CrossRef', 'OpenAlex']),
#                             ('abstract',
#                              '<jats:p>Phase amplitude coupling (PAC) between '
#                              'slow and fast oscillations is found throughout '
#                              'the brain and plays important functional roles. '
#                              'Its neural origin remains unclear. Experimental '
#                              'findings are often puzzling and sometimes '
#                              'contradictory. Most computational models rely on '
#                              'pairs of pacemaker neurons or neural populations '
#                              'tuned at different frequencies to produce PAC. '
#                              'Here, using a data-driven model of a hippocampal '
#                              'microcircuit, we demonstrate that PAC can '
#                              'naturally emerge from a single feedback '
#                              'mechanism involving an inhibitory and excitatory '
#                              'neuron population, which interplay to generate '
#                              'theta frequency periodic bursts of higher '
#                              'frequency gamma. The model suggests the '
#                              'conditions under which a CA1 microcircuit can '
#                              'operate to elicit theta-gamma PAC, and '
#                              'highlights the modulatory role of OLM and PVBC '
#                              'cells, recurrent connectivity, and short term '
#                              'synaptic plasticity. Surprisingly, the results '
#                              'suggest the experimentally testable prediction '
#                              'that the generation of the slow population '
#                              'oscillation requires the fast one and cannot '
#                              'occur without it.</jats:p>'),
#                             ('abstract_engines', ['CrossRef']),
#                             ('keywords', ['Oscillation (cell signaling)']),
#                             ('keywords_engines', ['OpenAlex']),
#                             ('type', 'article'),
#                             ('type_engines', ['OpenAlex'])])),
#               ('citation_count',
#                OrderedDict([('total', 18),
#                             ('total_engines', ['OpenAlex']),
#                             ('2025', 3),
#                             ('2025_engines', ['OpenAlex']),
#                             ('2024', 12),
#                             ('2024_engines', ['OpenAlex']),
#                             ('2023', 3),
#                             ('2023_engines', ['OpenAlex']),
#                             ('2022', None),
#                             ('2022_engines', None),
#                             ('2021', None),
#                             ('2021_engines', None),
#                             ('2020', None),
#                             ('2020_engines', None),
#                             ('2019', None),
#                             ('2019_engines', None),
#                             ('2018', None),
#                             ('2018_engines', None),
#                             ('2017', None),
#                             ('2017_engines', None),
#                             ('2016', None),
#                             ('2016_engines', None),
#                             ('2015', None),
#                             ('2015_engines', None)])),
#               ('publication',
#                OrderedDict([('journal', 'PLOS Computational Biology'),
#                             ('journal_engines', ['CrossRef']),
#                             ('short_journal', 'PLoS Comput Biol'),
#                             ('short_journal_engines', ['CrossRef']),
#                             ('impact_factor', None),
#                             ('impact_factor_engines', None),
#                             ('issn', '1553-7358'),
#                             ('issn_engines', ['CrossRef']),
#                             ('volume', '19'),
#                             ('volume_engines', ['CrossRef', 'OpenAlex']),
#                             ('issue', '3'),
#                             ('issue_engines', ['CrossRef', 'OpenAlex']),
#                             ('first_page', 'e1010942'),
#                             ('first_page_engines', ['OpenAlex']),
#                             ('last_page', 'e1010942'),
#                             ('last_page_engines', ['OpenAlex']),
#                             ('publisher', 'Public Library of Science (PLoS)'),
#                             ('publisher_engines', ['CrossRef'])])),
#               ('url',
#                OrderedDict([('doi',
#                              'https://doi.org/10.1371/journal.pcbi.1010942'),
#                             ('doi_engines', ['CrossRef', 'OpenAlex']),
#                             ('publisher',
#                              'https://doi.org/10.1371/journal.pcbi.1010942'),
#                             ('publisher_engines', ['OpenAlex']),
#                             ('openurl_query', None),
#                             ('openurl_engines', None),
#                             ('openurl_resolved', []),
#                             ('openurl_resolved_engines', []),
#                             ('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('path',
#                OrderedDict([('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('system',
#                OrderedDict([('searched_by_arXiv', False),
#                             ('searched_by_CrossRef', True),
#                             ('searched_by_OpenAlex', True),
#                             ('searched_by_PubMed', False),
#                             ('searched_by_Semantic_Scholar', True),
#                             ('searched_by_URL', False)]))]),
#  OrderedDict([('id',
#                OrderedDict([('doi', '10.1371/journal.pcbi.1005180'),
#                             ('doi_engines', ['OpenAlex']),
#                             ('arxiv_id', None),
#                             ('arxiv_id_engines', None),
#                             ('pmid', '27802274'),
#                             ('pmid_engines', ['OpenAlex']),
#                             ('scholar_id', None),
#                             ('scholar_id_engines', None),
#                             ('corpus_id', 3626970),
#                             ('corpus_id_engines', ['Semantic_Scholar'])])),
#               ('basic',
#                OrderedDict([('title',
#                              'Topology, cross-frequency, and same-frequency '
#                              'band interactions shape the generation of '
#                              'phase-amplitude coupling in a neural mass model '
#                              'of a cortical column'),
#                             ('title_engines', ['CrossRef']),
#                             ('authors', ['Roberto C. Sotero']),
#                             ('authors_engines', ['CrossRef', 'OpenAlex']),
#                             ('year', 2016),
#                             ('year_engines', ['OpenAlex']),
#                             ('abstract',
#                              '<jats:title>Abstract</jats:title><jats:p>Phase-amplitude '
#                              'coupling (PAC), a type of cross-frequency '
#                              'coupling (CFC) where the phase of a '
#                              'low-frequency rhythm modulates the amplitude of '
#                              'a higher frequency, is becoming an important '
#                              'indicator of information transmission in the '
#                              'brain. However, the neurobiological mechanisms '
#                              'underlying its generation remain undetermined. A '
#                              'realistic, yet tractable computational model of '
#                              'the phenomenon is thus needed. Here we propose a '
#                              'neural mass model of a cortical column, '
#                              'comprising fourteen neuronal populations '
#                              'distributed across four layers (L2/3, L4, L5 and '
#                              'L6). The conditional transfer entropies (cTE) '
#                              'from the phases to the amplitudes of the '
#                              'generated oscillations are estimated by means of '
#                              'the conditional mutual information. This '
#                              'approach provides information regarding '
#                              'directionality by distinguishing PAC from APC '
#                              '(amplitude-phase coupling), i.e. the information '
#                              'transfer from amplitudes to phases, and can be '
#                              'used to estimate other types of CFC such as '
#                              'amplitude-amplitude coupling (AAC) and '
#                              'phase-phase coupling (PPC). While experiments '
#                              'often only focus on one or two PAC combinations '
#                              '(e.g., theta-gamma or alpha-gamma), we found '
#                              'that a cortical column can simultaneously '
#                              'generate almost all possible PAC combinations, '
#                              'depending on connectivity parameters, time '
#                              'constants, and external inputs. We found that '
#                              'the strength of PAC between two populations was '
#                              'strongly correlated with the strength of the '
#                              'effective connections between them and, on '
#                              'average, did not depend upon the presence or '
#                              'absence of a direct (anatomical) connection. '
#                              'When considering a cortical column circuit as a '
#                              'complex network, we found that neuronal '
#                              'populations making indirect PAC connections had, '
#                              'on average, higher local clustering coefficient, '
#                              'efficiency, and betweenness centrality than '
#                              'populations making direct connections and '
#                              'populations not involved in PAC connections. '
#                              'This suggests that their interactions were more '
#                              'efficient when transmitting information. Since '
#                              'more than 60% of the obtained interactions '
#                              'represented indirect connections, our results '
#                              'highlight the importance of the topology of '
#                              'cortical circuits for the generation on of the '
#                              'PAC phenomenon. Finally, our results '
#                              'demonstrated that indirect PAC interactions can '
#                              'be explained by a cascade of direct CFC and '
#                              'same-frequency band interactions, suggesting '
#                              'that PAC analysis of experimental data should be '
#                              'accompanied by the estimation of other types of '
#                              'frequency interactions for an integrative '
#                              'understanding of the phenomenon.</jats:p>'),
#                             ('abstract_engines', ['CrossRef']),
#                             ('keywords', None),
#                             ('keywords_engines', None),
#                             ('type', 'article'),
#                             ('type_engines', ['OpenAlex'])])),
#               ('citation_count',
#                OrderedDict([('total', 36),
#                             ('total_engines', ['OpenAlex']),
#                             ('2025', 2),
#                             ('2025_engines', ['OpenAlex']),
#                             ('2024', 6),
#                             ('2024_engines', ['OpenAlex']),
#                             ('2023', 3),
#                             ('2023_engines', ['OpenAlex']),
#                             ('2022', 4),
#                             ('2022_engines', ['OpenAlex']),
#                             ('2021', 2),
#                             ('2021_engines', ['OpenAlex']),
#                             ('2020', 3),
#                             ('2020_engines', ['OpenAlex']),
#                             ('2019', 11),
#                             ('2019_engines', ['OpenAlex']),
#                             ('2018', 3),
#                             ('2018_engines', ['OpenAlex']),
#                             ('2017', 2),
#                             ('2017_engines', ['OpenAlex']),
#                             ('2016', None),
#                             ('2016_engines', None),
#                             ('2015', None),
#                             ('2015_engines', None)])),
#               ('publication',
#                OrderedDict([('journal', 'bioRxiv'),
#                             ('journal_engines', ['Semantic_Scholar']),
#                             ('short_journal', None),
#                             ('short_journal_engines', None),
#                             ('impact_factor', None),
#                             ('impact_factor_engines', None),
#                             ('issn', None),
#                             ('issn_engines', None),
#                             ('volume', '12'),
#                             ('volume_engines', ['OpenAlex']),
#                             ('issue', '11'),
#                             ('issue_engines', ['OpenAlex']),
#                             ('first_page', 'e1005180'),
#                             ('first_page_engines', ['OpenAlex']),
#                             ('last_page', 'e1005180'),
#                             ('last_page_engines', ['OpenAlex']),
#                             ('publisher', 'Cold Spring Harbor Laboratory'),
#                             ('publisher_engines', ['CrossRef'])])),
#               ('url',
#                OrderedDict([('doi',
#                              'https://doi.org/10.1371/journal.pcbi.1005180'),
#                             ('doi_engines', ['OpenAlex']),
#                             ('publisher',
#                              'https://doi.org/10.1371/journal.pcbi.1005180'),
#                             ('publisher_engines', ['OpenAlex']),
#                             ('openurl_query', None),
#                             ('openurl_engines', None),
#                             ('openurl_resolved', []),
#                             ('openurl_resolved_engines', []),
#                             ('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('path',
#                OrderedDict([('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('system',
#                OrderedDict([('searched_by_arXiv', False),
#                             ('searched_by_CrossRef', True),
#                             ('searched_by_OpenAlex', True),
#                             ('searched_by_PubMed', False),
#                             ('searched_by_Semantic_Scholar', True),
#                             ('searched_by_URL', False)]))]),
#  OrderedDict([('id',
#                OrderedDict([('doi', '10.1038/s41598-019-48870-2'),
#                             ('doi_engines', ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('arxiv_id', None),
#                             ('arxiv_id_engines', None),
#                             ('pmid', '31455811'),
#                             ('pmid_engines', ['OpenAlex', 'PubMed']),
#                             ('scholar_id', None),
#                             ('scholar_id_engines', None),
#                             ('corpus_id', 201651743),
#                             ('corpus_id_engines', ['Semantic_Scholar'])])),
#               ('basic',
#                OrderedDict([('title',
#                              'Time-Frequency Based Phase-Amplitude Coupling '
#                              'Measure For Neuronal Oscillations'),
#                             ('title_engines',
#                              ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('authors',
#                              ['Tamanna T. K. Munia', 'Selin Aviyente']),
#                             ('authors_engines', ['CrossRef', 'OpenAlex']),
#                             ('year', 2019),
#                             ('year_engines',
#                              ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('abstract',
#                              '<jats:title>Abstract</jats:title><jats:p>Oscillatory '
#                              'activity in the brain has been associated with a '
#                              'wide variety of cognitive processes including '
#                              'decision making, feedback processing, and '
#                              'working memory. The high temporal resolution '
#                              'provided by electroencephalography (EEG) enables '
#                              'the study of variation of oscillatory power and '
#                              'coupling across time. Various forms of neural '
#                              'synchrony across frequency bands have been '
#                              'suggested as the mechanism underlying neural '
#                              'binding. Recently, a considerable amount of work '
#                              'has focused on phase-amplitude coupling (PAC)– a '
#                              'form of cross-frequency coupling where the '
#                              'amplitude of a high frequency signal is '
#                              'modulated by the phase of low frequency '
#                              'oscillations. The existing methods for assessing '
#                              'PAC have some limitations including limited '
#                              'frequency resolution and sensitivity to noise, '
#                              'data length and sampling rate due to the '
#                              'inherent dependence on bandpass filtering. In '
#                              'this paper, we propose a new time-frequency '
#                              'based PAC (t-f PAC) measure that can address '
#                              'these issues. The proposed method relies on a '
#                              'complex time-frequency distribution, known as '
#                              'the Reduced Interference Distribution '
#                              '(RID)-Rihaczek distribution, to estimate both '
#                              'the phase and the envelope of low and high '
#                              'frequency oscillations, respectively. As such, '
#                              'it does not rely on bandpass filtering and '
#                              'possesses some of the desirable properties of '
#                              'time-frequency distributions such as high '
#                              'frequency resolution. The proposed technique is '
#                              'first evaluated for simulated data and then '
#                              'applied to an EEG speeded reaction task dataset. '
#                              'The results illustrate that the proposed '
#                              'time-frequency based PAC is more robust to '
#                              'varying signal parameters and provides a more '
#                              'accurate measure of coupling strength.</jats:p>'),
#                             ('abstract_engines', ['CrossRef']),
#                             ('keywords',
#                              ['SIGNAL (programming language)',
#                               'Envelope (radar)',
#                               'Instantaneous phase']),
#                             ('keywords_engines', ['OpenAlex']),
#                             ('type', 'article'),
#                             ('type_engines', ['OpenAlex'])])),
#               ('citation_count',
#                OrderedDict([('total', 99),
#                             ('total_engines', ['OpenAlex']),
#                             ('2025', 5),
#                             ('2025_engines', ['OpenAlex']),
#                             ('2024', 38),
#                             ('2024_engines', ['OpenAlex']),
#                             ('2023', 15),
#                             ('2023_engines', ['OpenAlex']),
#                             ('2022', 19),
#                             ('2022_engines', ['OpenAlex']),
#                             ('2021', 13),
#                             ('2021_engines', ['OpenAlex']),
#                             ('2020', 7),
#                             ('2020_engines', ['OpenAlex']),
#                             ('2019', 1),
#                             ('2019_engines', ['OpenAlex']),
#                             ('2018', None),
#                             ('2018_engines', None),
#                             ('2017', None),
#                             ('2017_engines', None),
#                             ('2016', None),
#                             ('2016_engines', None),
#                             ('2015', None),
#                             ('2015_engines', None)])),
#               ('publication',
#                OrderedDict([('journal', 'Scientific Reports'),
#                             ('journal_engines', ['CrossRef']),
#                             ('short_journal', 'Sci Rep'),
#                             ('short_journal_engines', ['CrossRef', 'PubMed']),
#                             ('impact_factor', None),
#                             ('impact_factor_engines', None),
#                             ('issn', '2045-2322'),
#                             ('issn_engines', ['CrossRef', 'PubMed']),
#                             ('volume', '9'),
#                             ('volume_engines',
#                              ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('issue', '1'),
#                             ('issue_engines',
#                              ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('first_page', None),
#                             ('first_page_engines', None),
#                             ('last_page', None),
#                             ('last_page_engines', None),
#                             ('publisher',
#                              'Springer Science and Business Media LLC'),
#                             ('publisher_engines', ['CrossRef'])])),
#               ('url',
#                OrderedDict([('doi',
#                              'https://doi.org/10.1038/s41598-019-48870-2'),
#                             ('doi_engines', ['CrossRef', 'OpenAlex', 'PubMed']),
#                             ('publisher',
#                              'https://doi.org/10.1038/s41598-019-48870-2'),
#                             ('publisher_engines', ['OpenAlex']),
#                             ('openurl_query', None),
#                             ('openurl_engines', None),
#                             ('openurl_resolved', []),
#                             ('openurl_resolved_engines', []),
#                             ('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('path',
#                OrderedDict([('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('system',
#                OrderedDict([('searched_by_arXiv', False),
#                             ('searched_by_CrossRef', True),
#                             ('searched_by_OpenAlex', True),
#                             ('searched_by_PubMed', True),
#                             ('searched_by_Semantic_Scholar', True),
#                             ('searched_by_URL', False)]))]),
#  OrderedDict([('id',
#                OrderedDict([('doi', '10.3389/fnhum.2010.00191'),
#                             ('doi_engines', ['CrossRef', 'OpenAlex']),
#                             ('arxiv_id', None),
#                             ('arxiv_id_engines', None),
#                             ('pmid', '21060716'),
#                             ('pmid_engines', ['OpenAlex']),
#                             ('scholar_id', None),
#                             ('scholar_id_engines', None),
#                             ('corpus_id', 7724159),
#                             ('corpus_id_engines', ['Semantic_Scholar'])])),
#               ('basic',
#                OrderedDict([('title',
#                              'Shifts in gamma phase–amplitude coupling '
#                              'frequency from theta to alpha over posterior '
#                              'cortex during visual tasks'),
#                             ('title_engines', ['CrossRef', 'OpenAlex']),
#                             ('authors', ['Bradley Voytek']),
#                             ('authors_engines', ['CrossRef', 'OpenAlex']),
#                             ('year', 2010),
#                             ('year_engines', ['CrossRef', 'OpenAlex']),
#                             ('abstract',
#                              'The phase of ongoing theta (4–8 Hz) and alpha '
#                              '(8–12 Hz) electrophysiological oscillations is '
#                              'coupled to high gamma (80–150 Hz) amplitude, '
#                              'which suggests that low-frequency oscillations '
#                              'modulate local cortical activity. While this '
#                              'phase–amplitude coupling (PAC) has been '
#                              'demonstrated in a variety of tasks and cortical '
#                              'regions, it has not been shown whether task '
#                              'demands differentially affect the regional '
#                              'distribution of the preferred low-frequency '
#                              'coupling to high gamma. To address this issue we '
#                              'investigated multiple-rhythm theta/alpha to high '
#                              'gamma PAC in two subjects with implanted '
#                              'subdural electrocorticographic grids. We show '
#                              'that high gamma amplitude couples to the theta '
#                              'and alpha troughs and demonstrate that, during '
#                              'visual tasks, alpha/high gamma coupling '
#                              'preferentially increases in visual cortical '
#                              'regions. These results suggest that '
#                              'low-frequency phase to high-frequency amplitude '
#                              'coupling is modulated by behavioral task and may '
#                              'reflect a mechanism for selection between '
#                              'communicating neuronal networks.'),
#                             ('abstract_engines', ['Semantic_Scholar']),
#                             ('keywords',
#                              ['Alpha (finance)',
#                               'BETA (programming language)']),
#                             ('keywords_engines', ['OpenAlex']),
#                             ('type', 'article'),
#                             ('type_engines', ['OpenAlex'])])),
#               ('citation_count',
#                OrderedDict([('total', 416),
#                             ('total_engines', ['OpenAlex']),
#                             ('2025', 11),
#                             ('2025_engines', ['OpenAlex']),
#                             ('2024', 29),
#                             ('2024_engines', ['OpenAlex']),
#                             ('2023', 18),
#                             ('2023_engines', ['OpenAlex']),
#                             ('2022', 23),
#                             ('2022_engines', ['OpenAlex']),
#                             ('2021', 41),
#                             ('2021_engines', ['OpenAlex']),
#                             ('2020', 35),
#                             ('2020_engines', ['OpenAlex']),
#                             ('2019', 36),
#                             ('2019_engines', ['OpenAlex']),
#                             ('2018', 30),
#                             ('2018_engines', ['OpenAlex']),
#                             ('2017', 30),
#                             ('2017_engines', ['OpenAlex']),
#                             ('2016', 40),
#                             ('2016_engines', ['OpenAlex']),
#                             ('2015', 32),
#                             ('2015_engines', ['OpenAlex']),
#                             ('2014_engines', ['OpenAlex']),
#                             ('2014', 26),
#                             ('2013_engines', ['OpenAlex']),
#                             ('2013', 23),
#                             ('2012_engines', ['OpenAlex']),
#                             ('2012', 25)])),
#               ('publication',
#                OrderedDict([('journal', 'Frontiers in Human Neuroscience'),
#                             ('journal_engines', ['CrossRef']),
#                             ('short_journal', 'Front. Hum. Neurosci.'),
#                             ('short_journal_engines', ['CrossRef']),
#                             ('impact_factor', None),
#                             ('impact_factor_engines', None),
#                             ('issn', '1662-5161'),
#                             ('issn_engines', ['CrossRef']),
#                             ('volume', '4'),
#                             ('volume_engines', ['CrossRef', 'OpenAlex']),
#                             ('issue', None),
#                             ('issue_engines', None),
#                             ('first_page', None),
#                             ('first_page_engines', None),
#                             ('last_page', None),
#                             ('last_page_engines', None),
#                             ('publisher', 'Frontiers Media SA'),
#                             ('publisher_engines', ['CrossRef'])])),
#               ('url',
#                OrderedDict([('doi', 'https://doi.org/10.3389/fnhum.2010.00191'),
#                             ('doi_engines', ['CrossRef', 'OpenAlex']),
#                             ('publisher',
#                              'https://doi.org/10.3389/fnhum.2010.00191'),
#                             ('publisher_engines', ['OpenAlex']),
#                             ('openurl_query', None),
#                             ('openurl_engines', None),
#                             ('openurl_resolved', []),
#                             ('openurl_resolved_engines', []),
#                             ('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('path',
#                OrderedDict([('pdfs', []),
#                             ('pdfs_engines', []),
#                             ('supplementary_files', []),
#                             ('supplementary_files_engines', []),
#                             ('additional_files', []),
#                             ('additional_files_engines', [])])),
#               ('system',
#                OrderedDict([('searched_by_arXiv', False),
#                             ('searched_by_CrossRef', True),
#                             ('searched_by_OpenAlex', True),
#                             ('searched_by_PubMed', False),
#                             ('searched_by_Semantic_Scholar', True),
#                             ('searched_by_URL', False)]))])]
# ['10.3389/fnins.2017.00487',
#  '10.1371/journal.pcbi.1010942',
#  '10.3389/fnhum.2021.622313',
#  '10.1371/journal.pcbi.1008302',
#  '10.3389/fnins.2019.00573',
#  '10.1371/journal.pone.0102591',
#  '10.3389/fnhum.2021.622313',
#  '10.3389/fnhum.2013.00084',
#  '10.1371/journal.pone.0102591',
#  '10.1371/journal.pcbi.1008302',
#  '10.3389/fnhum.2013.00084',
#  '10.3389/fnins.2019.00573',
#  '10.1038/s41598-019-48870-2',
#  '10.3389/fnins.2017.00487',
#  '10.1371/journal.pcbi.1005180',
#  '10.1371/journal.pcbi.1010942',
#  '10.1371/journal.pcbi.1005180',
#  '10.1038/s41598-019-48870-2',
#  '10.3389/fnhum.2010.00191']
# 2. Finding URLs...
# INFO: Resolving DOI: 10.3389/fnins.2017.00487
# INFO: Resolving DOI: 10.1371/journal.pcbi.1010942
# INFO: Resolving DOI: 10.3389/fnhum.2021.622313
# INFO: Resolving DOI: 10.1371/journal.pcbi.1008302
# INFO: Resolving DOI: 10.3389/fnins.2019.00573
# INFO: Resolved to: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008302
# INFO: Resolved to: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1010942
# INFO: Resolved to: https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2021.622313/full
# INFO: Resolved to: https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2019.00573/full
# INFO: Resolved to: https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2017.00487/full
# INFO: Finding resolver link for DOI: 10.3389/fnhum.2021.622313
# INFO: Finding resolver link for DOI: 10.3389/fnins.2017.00487
# INFO: Finding resolver link for DOI: 10.3389/fnins.2019.00573
# INFO: Finding resolver link for DOI: 10.1371/journal.pcbi.1008302
# INFO: Finding resolver link for DOI: 10.1371/journal.pcbi.1010942
# WARNING: Could not find resolver link with domain matching strategy
# WARNING: Could not find resolver link with domain matching strategy
# WARNING: Could not find resolver link with domain matching strategy
# WARNING: Could not find resolver link with page structure strategy
# WARNING: Could not find resolver link with page structure strategy
# WARNING: Could not find resolver link with domain matching strategy
# WARNING: Could not find resolver link with text pattern strategy
# WARNING: Could not resolve OpenURL
# WARNING: Could not find resolver link with domain matching strategy
# WARNING: Could not find resolver link with page structure strategy
# WARNING: Could not find resolver link with text pattern strategy
# WARNING: Could not resolve OpenURL
# WARNING: Could not find resolver link with text pattern strategy
# WARNING: Could not resolve OpenURL
# WARNING: Could not find resolver link with page structure strategy
# WARNING: Could not find resolver link with page structure strategy
# WARNING: Could not find resolver link with text pattern strategy
# WARNING: Could not resolve OpenURL
# WARNING: Could not find resolver link with text pattern strategy
# WARNING: Could not resolve OpenURL
# INFO: Loaded 681 Zotero translators
# INFO: Executing Zotero translator: PLoS Journals
# INFO: Loaded 681 Zotero translators
# INFO: Executing Zotero translator: Frontiers
# INFO: Loaded 681 Zotero translators
# INFO: Executing Zotero translator: PLoS Journals
# INFO: Loaded 681 Zotero translators
# INFO: Executing Zotero translator: Frontiers
# INFO: Loaded 681 Zotero translators
# INFO: Executing Zotero translator: Frontiers
# WARNING: Zotero Translator did not extracted any URLs from https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1010942
# WARNING: Zotero translator did not find any PDF URLs
# WARNING: Zotero Translator did not extracted any URLs from https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2017.00487/full
# WARNING: Zotero translator did not find any PDF URLs
# WARNING: Zotero Translator did not extracted any URLs from https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008302
# WARNING: Zotero translator did not find any PDF URLs
# WARNING: Zotero Translator did not extracted any URLs from https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2021.622313/full
# WARNING: Zotero translator did not find any PDF URLs
# WARNING: Zotero Translator did not extracted any URLs from https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2019.00573/full
# WARNING: Zotero translator did not find any PDF URLs
# SUCCESS: Publisher-specific pattern matching found 1 PDF URLs from https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2021.622313/full
# SUCCESS: Found 1 unique PDF URLs from https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2021.622313/full
# INFO:   - direct_link: 1 URLs
# INFO: Resolving DOI: 10.1371/journal.pone.0102591
# INFO: Resolved to: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0102591
# SUCCESS: Publisher-specific pattern matching found 1 PDF URLs from https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1010942
# SUCCESS: Found 1 unique PDF URLs from https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1010942
# INFO:   - direct_link: 1 URLs
# SUCCESS: Publisher-specific pattern matching found 1 PDF URLs from https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2017.00487/full
# SUCCESS: Found 1 unique PDF URLs from https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2017.00487/full
# INFO:   - direct_link: 1 URLs
# SUCCESS: Publisher-specific pattern matching found 1 PDF URLs from https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008302
# SUCCESS: Found 1 unique PDF URLs from https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008302
# INFO:   - direct_link: 1 URLs
# INFO: Resolving DOI: 10.3389/fnhum.2021.622313
# INFO: Resolving DOI: 10.3389/fnhum.2013.00084
# INFO: Resolving DOI: 10.1371/journal.pone.0102591
# SUCCESS: Publisher-specific pattern matching found 1 PDF URLs from https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2019.00573/full
# SUCCESS: Found 1 unique PDF URLs from https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2019.00573/full
# INFO:   - direct_link: 1 URLs
# INFO: Resolving DOI: 10.1371/journal.pcbi.1008302
# INFO: Resolved to: https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2021.622313/full
# INFO: Finding resolver link for DOI: 10.1371/journal.pone.0102591
# INFO: Resolved to: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0102591
# INFO: Resolved to: https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2013.00084/full
# INFO: Resolved to: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008302
# WARNING: Could not find resolver link with domain matching strategy
# WARNING: Could not find resolver link with page structure strategy
# WARNING: Could not find resolver link with text pattern strategy
# WARNING: Could not resolve OpenURL
# INFO: Loaded 681 Zotero translators
# INFO: Executing Zotero translator: PLoS Journals
# WARNING: Zotero Translator did not extracted any URLs from https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0102591
# WARNING: Zotero translator did not find any PDF URLs
# INFO: Finding resolver link for DOI: 10.3389/fnhum.2021.622313
# INFO: Finding resolver link for DOI: 10.3389/fnhum.2013.00084
# WARNING: Could not find resolver link with domain matching strategy
# WARNING: Could not find resolver link with page structure strategy
# WARNING: Could not find resolver link with domain matching strategy
# WARNING: Could not find resolver link with text pattern strategy
# WARNING: Could not resolve OpenURL
# WARNING: Could not find resolver link with page structure strategy
# INFO: Finding resolver link for DOI: 10.1371/journal.pone.0102591
# WARNING: Could not find resolver link with text pattern strategy
# WARNING: Could not resolve OpenURL
# WARNING: Could not find resolver link with domain matching strategy
# WARNING: Could not find resolver link with page structure strategy
# INFO: Finding resolver link for DOI: 10.1371/journal.pcbi.1008302
# WARNING: Could not find resolver link with text pattern strategy
# WARNING: Could not resolve OpenURL
# WARNING: Could not find resolver link with domain matching strategy
# WARNING: Could not find resolver link with page structure strategy
# WARNING: Could not find resolver link with text pattern strategy
# WARNING: Could not resolve OpenURL
# INFO: Loaded 681 Zotero translators
# INFO: Executing Zotero translator: Frontiers
# INFO: Loaded 681 Zotero translators
# INFO: Executing Zotero translator: Frontiers
# INFO: Loaded 681 Zotero translators
# INFO: Executing Zotero translator: PLoS Journals
# WARNING: Zotero Translator did not extracted any URLs from https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2021.622313/full
# WARNING: Zotero translator did not find any PDF URLs
# WARNING: Zotero Translator did not extracted any URLs from https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2013.00084/full
# WARNING: Zotero translator did not find any PDF URLs
# WARNING: Zotero Translator did not extracted any URLs from https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0102591
# WARNING: Zotero translator did not find any PDF URLs
# INFO: Loaded 681 Zotero translators
# INFO: Executing Zotero translator: PLoS Journals
# WARNING: Zotero Translator did not extracted any URLs from https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008302
# WARNING: Zotero translator did not find any PDF URLs
# SUCCESS: Publisher-specific pattern matching found 1 PDF URLs from https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0102591
# SUCCESS: Found 1 unique PDF URLs from https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0102591
# INFO:   - direct_link: 1 URLs
# INFO: Resolving DOI: 10.3389/fnhum.2013.00084
# INFO: Resolved to: https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2013.00084/full
# SUCCESS: Publisher-specific pattern matching found 1 PDF URLs from https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2021.622313/full
# SUCCESS: Found 1 unique PDF URLs from https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2021.622313/full
# INFO:   - direct_link: 1 URLs
# SUCCESS: Publisher-specific pattern matching found 1 PDF URLs from https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2013.00084/full
# SUCCESS: Found 1 unique PDF URLs from https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2013.00084/full
# INFO:   - direct_link: 1 URLs
# INFO: Resolving DOI: 10.3389/fnins.2019.00573
# INFO: Resolving DOI: 10.1038/s41598-019-48870-2
# SUCCESS: Publisher-specific pattern matching found 1 PDF URLs from https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0102591
# SUCCESS: Found 1 unique PDF URLs from https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0102591
# INFO:   - direct_link: 1 URLs
# INFO: Resolving DOI: 10.3389/fnins.2017.00487
# SUCCESS: Publisher-specific pattern matching found 1 PDF URLs from https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008302
# SUCCESS: Found 1 unique PDF URLs from https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008302
# INFO:   - direct_link: 1 URLs
# INFO: Resolving DOI: 10.1371/journal.pcbi.1005180
# INFO: Finding resolver link for DOI: 10.3389/fnhum.2013.00084
# INFO: Resolved to: https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2019.00573/full
# INFO: Resolved to: https://www.nature.com/articles/s41598-019-48870-2
# WARNING: Could not find resolver link with domain matching strategy
# WARNING: Could not find resolver link with page structure strategy
# INFO: Resolved to: https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2017.00487/full
# WARNING: Could not find resolver link with text pattern strategy
# WARNING: Could not resolve OpenURL
# INFO: Resolved to: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005180
# INFO: Loaded 681 Zotero translators
# INFO: Executing Zotero translator: Frontiers
# WARNING: Zotero Translator did not extracted any URLs from https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2013.00084/full
# WARNING: Zotero translator did not find any PDF URLs
# INFO: Finding resolver link for DOI: 10.3389/fnins.2019.00573
# INFO: Finding resolver link for DOI: 10.1038/s41598-019-48870-2
# WARNING: Could not find resolver link with domain matching strategy
# INFO: Found SFX Nature link: Springer Nature - nature.com Journals - Fully Open
# SUCCESS: Found link using domain matching (Strategy 1)
# INFO: Found resolver link, attempting to click...
# WARNING: Could not find resolver link with page structure strategy
# WARNING: Could not find resolver link with text pattern strategy
# WARNING: Could not resolve OpenURL
# INFO: Finding resolver link for DOI: 10.3389/fnins.2017.00487
# SUCCESS: Publisher-specific pattern matching found 1 PDF URLs from https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2013.00084/full
# SUCCESS: Found 1 unique PDF URLs from https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2013.00084/full
# INFO:   - direct_link: 1 URLs
# INFO: Resolving DOI: 10.1371/journal.pcbi.1010942
# WARNING: Could not find resolver link with domain matching strategy
# WARNING: Could not find resolver link with page structure strategy
# WARNING: Could not find resolver link with text pattern strategy
# WARNING: Could not resolve OpenURL
# INFO: Finding resolver link for DOI: 10.1371/journal.pcbi.1005180
# INFO: Loaded 681 Zotero translators
# INFO: Executing Zotero translator: Frontiers
# WARNING: Could not find resolver link with domain matching strategy
# WARNING: Could not find resolver link with page structure strategy
# WARNING: Could not find resolver link with text pattern strategy
# WARNING: Could not resolve OpenURL
# INFO: Loaded 681 Zotero translators
# INFO: Executing Zotero translator: Frontiers
# WARNING: Zotero Translator did not extracted any URLs from https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2019.00573/full
# WARNING: Zotero translator did not find any PDF URLs
# WARNING: Zotero Translator did not extracted any URLs from https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2017.00487/full
# WARNING: Zotero translator did not find any PDF URLs
# INFO: Resolved to: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1010942
# INFO: Loaded 681 Zotero translators
# INFO: Executing Zotero translator: PLoS Journals
# WARNING: Could not resolve OpenURL
# WARNING: Zotero Translator did not extracted any URLs from https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005180
# WARNING: Zotero translator did not find any PDF URLs
# INFO: Loaded 681 Zotero translators
# INFO: Executing Zotero translator: Nature Publishing Group
# SUCCESS: Zotero Translator extracted 5 URLs from https://www.nature.com/articles/s41598-019-48870-2
# INFO: Zotero translator found 5 PDF URLs
# INFO: Finding resolver link for DOI: 10.1371/journal.pcbi.1010942
# WARNING: Could not find resolver link with domain matching strategy
# WARNING: Could not find resolver link with page structure strategy
# SUCCESS: Publisher-specific pattern matching found 1 PDF URLs from https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2019.00573/full
# SUCCESS: Found 1 unique PDF URLs from https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2019.00573/full
# INFO:   - direct_link: 1 URLs
# WARNING: Could not find resolver link with text pattern strategy
# WARNING: Could not resolve OpenURL
# INFO: Resolving DOI: 10.1371/journal.pcbi.1005180
# SUCCESS: Publisher-specific pattern matching found 1 PDF URLs from https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2017.00487/full
# SUCCESS: Found 1 unique PDF URLs from https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2017.00487/full
# INFO:   - direct_link: 1 URLs
# INFO: Resolving DOI: 10.1038/s41598-019-48870-2
# INFO: Loaded 681 Zotero translators
# INFO: Executing Zotero translator: PLoS Journals
# SUCCESS: Publisher-specific pattern matching found 1 PDF URLs from https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005180
# SUCCESS: Found 1 unique PDF URLs from https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005180
# INFO:   - direct_link: 1 URLs
# WARNING: Zotero Translator did not extracted any URLs from https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1010942
# WARNING: Zotero translator did not find any PDF URLs
# INFO: Resolving DOI: 10.3389/fnhum.2010.00191
# INFO: Resolved to: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005180
# SUCCESS: Publisher-specific pattern matching found 1 PDF URLs from https://www.nature.com/articles/s41598-019-48870-2
# SUCCESS: Found 5 unique PDF URLs from https://www.nature.com/articles/s41598-019-48870-2
# INFO:   - zotero_translator: 5 URLs
# INFO: Resolved to: https://www.nature.com/articles/s41598-019-48870-2
# INFO: Resolved to: https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2010.00191/full
# INFO: Finding resolver link for DOI: 10.1038/s41598-019-48870-2
# INFO: Finding resolver link for DOI: 10.1371/journal.pcbi.1005180
# INFO: Found SFX Nature link: Springer Nature - nature.com Journals - Fully Open
# SUCCESS: Found link using domain matching (Strategy 1)
# INFO: Found resolver link, attempting to click...
# WARNING: Could not find resolver link with domain matching strategy
# WARNING: Could not find resolver link with page structure strategy
# WARNING: Could not find resolver link with text pattern strategy
# WARNING: Could not resolve OpenURL
# SUCCESS: Publisher-specific pattern matching found 1 PDF URLs from https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1010942
# SUCCESS: Found 1 unique PDF URLs from https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1010942
# INFO:   - direct_link: 1 URLs
# INFO: Finding resolver link for DOI: 10.3389/fnhum.2010.00191
# WARNING: Could not find resolver link with domain matching strategy
# WARNING: Could not find resolver link with page structure strategy
# WARNING: Could not find resolver link with text pattern strategy
# WARNING: Could not resolve OpenURL
# INFO: Loaded 681 Zotero translators
# INFO: Executing Zotero translator: PLoS Journals
# WARNING: Zotero Translator did not extracted any URLs from https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005180
# WARNING: Zotero translator did not find any PDF URLs
# INFO: Loaded 681 Zotero translators
# INFO: Executing Zotero translator: Frontiers
# WARNING: Could not resolve OpenURL
# WARNING: Zotero Translator did not extracted any URLs from https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2010.00191/full
# WARNING: Zotero translator did not find any PDF URLs
# INFO: Loaded 681 Zotero translators
# INFO: Executing Zotero translator: Nature Publishing Group
# SUCCESS: Zotero Translator extracted 5 URLs from https://www.nature.com/articles/s41598-019-48870-2
# INFO: Zotero translator found 5 PDF URLs
# SUCCESS: Publisher-specific pattern matching found 1 PDF URLs from https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2010.00191/full
# SUCCESS: Found 1 unique PDF URLs from https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2010.00191/full
# INFO:   - direct_link: 1 URLs
# SUCCESS: Publisher-specific pattern matching found 1 PDF URLs from https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005180
# SUCCESS: Found 1 unique PDF URLs from https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005180
# INFO:   - direct_link: 1 URLs
# ^P^P^P^P^P^P^P^P^P^P^P^P^P^P^P^PSUCCESS: Publisher-specific pattern matching found 1 PDF URLs from https://www.nature.com/articles/s41598-019-48870-2
# SUCCESS: Found 5 unique PDF URLs from https://www.nature.com/articles/s41598-019-48870-2
# INFO:   - zotero_translator: 5 URLs
# SUCCESS: Found 19/19 PDFs (= 100.0%)
# [{'url_doi': 'https://doi.org/10.3389/fnins.2017.00487',
#   'url_openurl_query': 'https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.3389/fnins.2017.00487',
#   'url_publisher': 'https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2017.00487/full',
#   'urls_pdf': [{'source': 'direct_link',
#                 'url': 'https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2017.00487/pdf'}]},
#  {'url_doi': 'https://doi.org/10.1371/journal.pcbi.1010942',
#   'url_openurl_query': 'https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.1371/journal.pcbi.1010942',
#   'url_publisher': 'https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1010942',
#   'urls_pdf': [{'source': 'direct_link',
#                 'url': 'https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1010942&type=printable'}]},
#  {'url_doi': 'https://doi.org/10.3389/fnhum.2021.622313',
#   'url_openurl_query': 'https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.3389/fnhum.2021.622313',
#   'url_publisher': 'https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2021.622313/full',
#   'urls_pdf': [{'source': 'direct_link',
#                 'url': 'https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2021.622313/pdf'}]},
#  {'url_doi': 'https://doi.org/10.1371/journal.pcbi.1008302',
#   'url_openurl_query': 'https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.1371/journal.pcbi.1008302',
#   'url_publisher': 'https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008302',
#   'urls_pdf': [{'source': 'direct_link',
#                 'url': 'https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1008302&type=printable'}]},
#  {'url_doi': 'https://doi.org/10.3389/fnins.2019.00573',
#   'url_openurl_query': 'https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.3389/fnins.2019.00573',
#   'url_publisher': 'https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2019.00573/full',
#   'urls_pdf': [{'source': 'direct_link',
#                 'url': 'https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2019.00573/pdf'}]},
#  {'url_doi': 'https://doi.org/10.1371/journal.pone.0102591',
#   'url_openurl_query': 'https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.1371/journal.pone.0102591',
#   'url_publisher': 'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0102591',
#   'urls_pdf': [{'source': 'direct_link',
#                 'url': 'https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0102591&type=printable'}]},
#  {'url_doi': 'https://doi.org/10.3389/fnhum.2021.622313',
#   'url_openurl_query': 'https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.3389/fnhum.2021.622313',
#   'url_publisher': 'https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2021.622313/full',
#   'urls_pdf': [{'source': 'direct_link',
#                 'url': 'https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2021.622313/pdf'}]},
#  {'url_doi': 'https://doi.org/10.3389/fnhum.2013.00084',
#   'url_openurl_query': 'https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.3389/fnhum.2013.00084',
#   'url_publisher': 'https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2013.00084/full',
#   'urls_pdf': [{'source': 'direct_link',
#                 'url': 'https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2013.00084/pdf'}]},
#  {'url_doi': 'https://doi.org/10.1371/journal.pone.0102591',
#   'url_openurl_query': 'https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.1371/journal.pone.0102591',
#   'url_publisher': 'https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0102591',
#   'urls_pdf': [{'source': 'direct_link',
#                 'url': 'https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0102591&type=printable'}]},
#  {'url_doi': 'https://doi.org/10.1371/journal.pcbi.1008302',
#   'url_openurl_query': 'https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.1371/journal.pcbi.1008302',
#   'url_publisher': 'https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008302',
#   'urls_pdf': [{'source': 'direct_link',
#                 'url': 'https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1008302&type=printable'}]},
#  {'url_doi': 'https://doi.org/10.3389/fnhum.2013.00084',
#   'url_openurl_query': 'https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.3389/fnhum.2013.00084',
#   'url_publisher': 'https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2013.00084/full',
#   'urls_pdf': [{'source': 'direct_link',
#                 'url': 'https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2013.00084/pdf'}]},
#  {'url_doi': 'https://doi.org/10.3389/fnins.2019.00573',
#   'url_openurl_query': 'https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.3389/fnins.2019.00573',
#   'url_publisher': 'https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2019.00573/full',
#   'urls_pdf': [{'source': 'direct_link',
#                 'url': 'https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2019.00573/pdf'}]},
#  {'url_doi': 'https://doi.org/10.1038/s41598-019-48870-2',
#   'url_openurl_query': 'https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.1038/s41598-019-48870-2',
#   'url_publisher': 'https://www.nature.com/articles/s41598-019-48870-2',
#   'urls_pdf': [{'source': 'zotero_translator',
#                 'url': 'https://www.nature.com/articles/s41598-019-48870-2.pdf'},
#                {'source': 'zotero_translator',
#                 'url': 'http://www.pnas.org/content/107/7/3228.full.pdf'},
#                {'source': 'zotero_translator',
#                 'url': 'http://www.pnas.org/content/110/8/3107.full.pdf'},
#                {'source': 'zotero_translator',
#                 'url': 'http://www.pnas.org/content/110/12/4780.full.pdf'},
#                {'source': 'zotero_translator',
#                 'url': 'https://www.biorxiv.org/content/early/2018/03/28/290361.full.pdf'}]},
#  {'url_doi': 'https://doi.org/10.3389/fnins.2017.00487',
#   'url_openurl_query': 'https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.3389/fnins.2017.00487',
#   'url_publisher': 'https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2017.00487/full',
#   'urls_pdf': [{'source': 'direct_link',
#                 'url': 'https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2017.00487/pdf'}]},
#  {'url_doi': 'https://doi.org/10.1371/journal.pcbi.1005180',
#   'url_openurl_query': 'https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.1371/journal.pcbi.1005180',
#   'url_publisher': 'https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005180',
#   'urls_pdf': [{'source': 'direct_link',
#                 'url': 'https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1005180&type=printable'}]},
#  {'url_doi': 'https://doi.org/10.1371/journal.pcbi.1010942',
#   'url_openurl_query': 'https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.1371/journal.pcbi.1010942',
#   'url_publisher': 'https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1010942',
#   'urls_pdf': [{'source': 'direct_link',
#                 'url': 'https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1010942&type=printable'}]},
#  {'url_doi': 'https://doi.org/10.1371/journal.pcbi.1005180',
#   'url_openurl_query': 'https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.1371/journal.pcbi.1005180',
#   'url_publisher': 'https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005180',
#   'urls_pdf': [{'source': 'direct_link',
#                 'url': 'https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1005180&type=printable'}]},
#  {'url_doi': 'https://doi.org/10.1038/s41598-019-48870-2',
#   'url_openurl_query': 'https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.1038/s41598-019-48870-2',
#   'url_publisher': 'https://www.nature.com/articles/s41598-019-48870-2',
#   'urls_pdf': [{'source': 'zotero_translator',
#                 'url': 'https://www.nature.com/articles/s41598-019-48870-2.pdf'},
#                {'source': 'zotero_translator',
#                 'url': 'http://www.pnas.org/content/107/7/3228.full.pdf'},
#                {'source': 'zotero_translator',
#                 'url': 'http://www.pnas.org/content/110/8/3107.full.pdf'},
#                {'source': 'zotero_translator',
#                 'url': 'http://www.pnas.org/content/110/12/4780.full.pdf'},
#                {'source': 'zotero_translator',
#                 'url': 'https://www.biorxiv.org/content/early/2018/03/28/290361.full.pdf'}]},
#  {'url_doi': 'https://doi.org/10.3389/fnhum.2010.00191',
#   'url_openurl_query': 'https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.3389/fnhum.2010.00191',
#   'url_publisher': 'https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2010.00191/full',
#   'urls_pdf': [{'source': 'direct_link',
#                 'url': 'https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2010.00191/pdf'}]}]
# 3. Downloading PDFs...
# https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2017.00487/pdf
# INFO: openurl_resolver_url resolved as https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# INFO: use_cache_url_finder resolved as True
# INFO: Trying method: From Response Body
# INFO: Trying to download https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2017.00487/pdf from response body
# INFO: Failed download from response body
# INFO: Trying method: Direct Download
# INFO: Trying direct download from https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2017.00487/pdf
# INFO: ERR_ABORTED detected - likely direct download
# SUCCESS: Direct download: from https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2017.00487/pdf to /tmp/scholar_pipeline/paper_00.pdf (1.58 MiB)
# https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1010942&type=printable
# INFO: openurl_resolver_url resolved as https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# INFO: use_cache_url_finder resolved as True
# INFO: Trying method: From Response Body
# INFO: Trying to download https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1010942&type=printable from response body
# INFO: Failed download from response body
# INFO: Trying method: Direct Download
# INFO: Trying direct download from https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1010942&type=printable
# INFO: ERR_ABORTED detected - likely direct download
# SUCCESS: Direct download: from https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1010942&type=printable to /tmp/scholar_pipeline/paper_01.pdf (5.68 MiB)
# https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2021.622313/pdf
# INFO: openurl_resolver_url resolved as https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# INFO: use_cache_url_finder resolved as True
# INFO: Trying method: From Response Body
# INFO: Trying to download https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2021.622313/pdf from response body
# INFO: Failed download from response body
# INFO: Trying method: Direct Download
# INFO: Trying direct download from https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2021.622313/pdf
# INFO: ERR_ABORTED detected - likely direct download
# SUCCESS: Direct download: from https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2021.622313/pdf to /tmp/scholar_pipeline/paper_02.pdf (0.17 MiB)
# https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1008302&type=printable
# INFO: openurl_resolver_url resolved as https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# INFO: use_cache_url_finder resolved as True
# INFO: Trying method: From Response Body
# INFO: Trying to download https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1008302&type=printable from response body
# INFO: Failed download from response body
# INFO: Trying method: Direct Download
# INFO: Trying direct download from https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1008302&type=printable
# INFO: Trying method: Chrome PDF
# INFO: PDF viewer detected
# SUCCESS: Downloaded: /tmp/scholar_pipeline/paper_03.pdf (2.6 MB)
# SUCCESS: Downloaded via Chrome PDF Viewer: from https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1008302&type=printable to /tmp/scholar_pipeline/paper_03.pdf
# https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2019.00573/pdf
# INFO: openurl_resolver_url resolved as https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# INFO: use_cache_url_finder resolved as True
# INFO: Trying method: From Response Body
# INFO: Trying to download https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2019.00573/pdf from response body
# INFO: Failed download from response body
# INFO: Trying method: Direct Download
# INFO: Trying direct download from https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2019.00573/pdf
# INFO: ERR_ABORTED detected - likely direct download
# SUCCESS: Direct download: from https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2019.00573/pdf to /tmp/scholar_pipeline/paper_04.pdf (5.71 MiB)
# https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0102591&type=printable
# INFO: openurl_resolver_url resolved as https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# INFO: use_cache_url_finder resolved as True
# INFO: Trying method: From Response Body
# INFO: Trying to download https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0102591&type=printable from response body
# INFO: Failed download from response body
# INFO: Trying method: Direct Download
# INFO: Trying direct download from https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0102591&type=printable
# INFO: Trying method: Chrome PDF
# INFO: PDF viewer detected
# SUCCESS: Downloaded: /tmp/scholar_pipeline/paper_05.pdf (2.1 MB)
# SUCCESS: Downloaded via Chrome PDF Viewer: from https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0102591&type=printable to /tmp/scholar_pipeline/paper_05.pdf
# https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2021.622313/pdf
# INFO: openurl_resolver_url resolved as https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# INFO: use_cache_url_finder resolved as True
# INFO: Trying method: From Response Body
# INFO: Trying to download https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2021.622313/pdf from response body
# INFO: Failed download from response body
# INFO: Trying method: Direct Download
# INFO: Trying direct download from https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2021.622313/pdf
# INFO: ERR_ABORTED detected - likely direct download
# SUCCESS: Direct download: from https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2021.622313/pdf to /tmp/scholar_pipeline/paper_06.pdf (0.17 MiB)
# https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2013.00084/pdf
# INFO: openurl_resolver_url resolved as https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# INFO: use_cache_url_finder resolved as True
# INFO: Trying method: From Response Body
# INFO: Trying to download https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2013.00084/pdf from response body
# INFO: Failed download from response body
# INFO: Trying method: Direct Download
# INFO: Trying direct download from https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2013.00084/pdf
# INFO: ERR_ABORTED detected - likely direct download
# SUCCESS: Direct download: from https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2013.00084/pdf to /tmp/scholar_pipeline/paper_07.pdf (3.56 MiB)
# https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0102591&type=printable
# INFO: openurl_resolver_url resolved as https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# INFO: use_cache_url_finder resolved as True
# INFO: Trying method: From Response Body
# INFO: Trying to download https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0102591&type=printable from response body
# INFO: Failed download from response body
# INFO: Trying method: Direct Download
# INFO: Trying direct download from https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0102591&type=printable
# INFO: Trying method: Chrome PDF
# INFO: PDF viewer detected
# SUCCESS: Downloaded: /tmp/scholar_pipeline/paper_08.pdf (2.1 MB)
# SUCCESS: Downloaded via Chrome PDF Viewer: from https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0102591&type=printable to /tmp/scholar_pipeline/paper_08.pdf
# https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1008302&type=printable
# INFO: openurl_resolver_url resolved as https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# INFO: use_cache_url_finder resolved as True
# INFO: Trying method: From Response Body
# INFO: Trying to download https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1008302&type=printable from response body
# INFO: Failed download from response body
# INFO: Trying method: Direct Download
# INFO: Trying direct download from https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1008302&type=printable
# INFO: Trying method: Chrome PDF
# INFO: PDF viewer detected
# SUCCESS: Downloaded: /tmp/scholar_pipeline/paper_09.pdf (2.6 MB)
# SUCCESS: Downloaded via Chrome PDF Viewer: from https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1008302&type=printable to /tmp/scholar_pipeline/paper_09.pdf
# https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2013.00084/pdf
# INFO: openurl_resolver_url resolved as https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# INFO: use_cache_url_finder resolved as True
# INFO: Trying method: From Response Body
# INFO: Trying to download https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2013.00084/pdf from response body
# INFO: Failed download from response body
# INFO: Trying method: Direct Download
# INFO: Trying direct download from https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2013.00084/pdf
# INFO: ERR_ABORTED detected - likely direct download
# SUCCESS: Direct download: from https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2013.00084/pdf to /tmp/scholar_pipeline/paper_10.pdf (3.56 MiB)
# https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2019.00573/pdf
# INFO: openurl_resolver_url resolved as https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# INFO: use_cache_url_finder resolved as True
# INFO: Trying method: From Response Body
# INFO: Trying to download https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2019.00573/pdf from response body
# INFO: Failed download from response body
# INFO: Trying method: Direct Download
# INFO: Trying direct download from https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2019.00573/pdf
# INFO: ERR_ABORTED detected - likely direct download
# SUCCESS: Direct download: from https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2019.00573/pdf to /tmp/scholar_pipeline/paper_11.pdf (5.71 MiB)
# https://www.nature.com/articles/s41598-019-48870-2.pdf
# INFO: openurl_resolver_url resolved as https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# INFO: use_cache_url_finder resolved as True
# INFO: Trying method: From Response Body
# INFO: Trying to download https://www.nature.com/articles/s41598-019-48870-2.pdf from response body
# INFO: Failed download from response body
# INFO: Trying method: Direct Download
# INFO: Trying direct download from https://www.nature.com/articles/s41598-019-48870-2.pdf
# INFO: Trying method: Chrome PDF
# INFO: PDF viewer detected
# SUCCESS: Downloaded: /tmp/scholar_pipeline/paper_12.pdf (2.4 MB)
# SUCCESS: Downloaded via Chrome PDF Viewer: from https://www.nature.com/articles/s41598-019-48870-2.pdf to /tmp/scholar_pipeline/paper_12.pdf
# http://www.pnas.org/content/107/7/3228.full.pdf
# INFO: openurl_resolver_url resolved as https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# INFO: use_cache_url_finder resolved as True
# INFO: Trying method: From Response Body
# INFO: Trying to download http://www.pnas.org/content/107/7/3228.full.pdf from response body
# INFO: Failed download from response body
# INFO: Trying method: Direct Download
# INFO: Trying direct download from http://www.pnas.org/content/107/7/3228.full.pdf
# INFO: Trying method: Chrome PDF
# INFO: PDF viewer detected
# ERROR: Chrome page download failed: Timeout 30000ms exceeded while waiting for event "download"
# =========================== logs ===========================
# waiting for event "download"
# ============================================================
# FAIL: Failed via Chrome PDF Viewer: from http://www.pnas.org/content/107/7/3228.full.pdf to /tmp/scholar_pipeline/paper_13.pdf
# FAIL: All download methods failed for http://www.pnas.org/content/107/7/3228.full.pdf
# http://www.pnas.org/content/110/8/3107.full.pdf
# INFO: openurl_resolver_url resolved as https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# INFO: use_cache_url_finder resolved as True
# INFO: Trying method: From Response Body
# INFO: Trying to download http://www.pnas.org/content/110/8/3107.full.pdf from response body
# INFO: Failed download from response body
# INFO: Trying method: Direct Download
# INFO: Trying direct download from http://www.pnas.org/content/110/8/3107.full.pdf
# INFO: Trying method: Chrome PDF
# INFO: PDF viewer detected
# ERROR: Chrome page download failed: Timeout 30000ms exceeded while waiting for event "download"
# =========================== logs ===========================
# waiting for event "download"
# ============================================================
# FAIL: Failed via Chrome PDF Viewer: from http://www.pnas.org/content/110/8/3107.full.pdf to /tmp/scholar_pipeline/paper_14.pdf
# FAIL: All download methods failed for http://www.pnas.org/content/110/8/3107.full.pdf
# http://www.pnas.org/content/110/12/4780.full.pdf
# INFO: openurl_resolver_url resolved as https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# INFO: use_cache_url_finder resolved as True
# INFO: Trying method: From Response Body
# INFO: Trying to download http://www.pnas.org/content/110/12/4780.full.pdf from response body
# INFO: Failed download from response body
# INFO: Trying method: Direct Download
# INFO: Trying direct download from http://www.pnas.org/content/110/12/4780.full.pdf
# INFO: Trying method: Chrome PDF
# INFO: PDF viewer detected
# ERROR: Chrome page download failed: Timeout 30000ms exceeded while waiting for event "download"
# =========================== logs ===========================
# waiting for event "download"
# ============================================================
# FAIL: Failed via Chrome PDF Viewer: from http://www.pnas.org/content/110/12/4780.full.pdf to /tmp/scholar_pipeline/paper_15.pdf
# FAIL: All download methods failed for http://www.pnas.org/content/110/12/4780.full.pdf
# https://www.biorxiv.org/content/early/2018/03/28/290361.full.pdf
# INFO: openurl_resolver_url resolved as https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# INFO: use_cache_url_finder resolved as True
# INFO: Trying method: From Response Body
# INFO: Trying to download https://www.biorxiv.org/content/early/2018/03/28/290361.full.pdf from response body
# INFO: Failed download from response body
# INFO: Trying method: Direct Download
# INFO: Trying direct download from https://www.biorxiv.org/content/early/2018/03/28/290361.full.pdf
# INFO: Trying method: Chrome PDF
# INFO: PDF viewer detected
# SUCCESS: Downloaded: /tmp/scholar_pipeline/paper_16.pdf (1.5 MB)
# SUCCESS: Downloaded via Chrome PDF Viewer: from https://www.biorxiv.org/content/early/2018/03/28/290361.full.pdf to /tmp/scholar_pipeline/paper_16.pdf
# https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2017.00487/pdf
# INFO: openurl_resolver_url resolved as https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# INFO: use_cache_url_finder resolved as True
# INFO: Trying method: From Response Body
# INFO: Trying to download https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2017.00487/pdf from response body
# INFO: Failed download from response body
# INFO: Trying method: Direct Download
# INFO: Trying direct download from https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2017.00487/pdf
# INFO: ERR_ABORTED detected - likely direct download
# SUCCESS: Direct download: from https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2017.00487/pdf to /tmp/scholar_pipeline/paper_17.pdf (1.58 MiB)
# https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1005180&type=printable
# INFO: openurl_resolver_url resolved as https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# INFO: use_cache_url_finder resolved as True
# INFO: Trying method: From Response Body
# INFO: Trying to download https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1005180&type=printable from response body
# INFO: Failed download from response body
# INFO: Trying method: Direct Download
# INFO: Trying direct download from https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1005180&type=printable
# INFO: Trying method: Chrome PDF
# INFO: PDF viewer detected
# SUCCESS: Downloaded: /tmp/scholar_pipeline/paper_18.pdf (5.3 MB)
# SUCCESS: Downloaded via Chrome PDF Viewer: from https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1005180&type=printable to /tmp/scholar_pipeline/paper_18.pdf
# https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1010942&type=printable
# INFO: openurl_resolver_url resolved as https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# INFO: use_cache_url_finder resolved as True
# INFO: Trying method: From Response Body
# INFO: Trying to download https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1010942&type=printable from response body
# INFO: Failed download from response body
# INFO: Trying method: Direct Download
# INFO: Trying direct download from https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1010942&type=printable
# INFO: ERR_ABORTED detected - likely direct download
# SUCCESS: Direct download: from https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1010942&type=printable to /tmp/scholar_pipeline/paper_19.pdf (5.68 MiB)
# https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1005180&type=printable
# INFO: openurl_resolver_url resolved as https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# INFO: use_cache_url_finder resolved as True
# INFO: Trying method: From Response Body
# INFO: Trying to download https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1005180&type=printable from response body
# INFO: Failed download from response body
# INFO: Trying method: Direct Download
# INFO: Trying direct download from https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1005180&type=printable
# INFO: Trying method: Chrome PDF
# INFO: PDF viewer detected
# SUCCESS: Downloaded: /tmp/scholar_pipeline/paper_20.pdf (5.3 MB)
# SUCCESS: Downloaded via Chrome PDF Viewer: from https://journals.plos.org/ploscompbiol/article/file?id=10.1371/journal.pcbi.1005180&type=printable to /tmp/scholar_pipeline/paper_20.pdf
# https://www.nature.com/articles/s41598-019-48870-2.pdf
# INFO: openurl_resolver_url resolved as https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# INFO: use_cache_url_finder resolved as True
# INFO: Trying method: From Response Body
# INFO: Trying to download https://www.nature.com/articles/s41598-019-48870-2.pdf from response body
# INFO: Failed download from response body
# INFO: Trying method: Direct Download
# INFO: Trying direct download from https://www.nature.com/articles/s41598-019-48870-2.pdf
# INFO: Trying method: Chrome PDF
# INFO: PDF viewer detected
# SUCCESS: Downloaded: /tmp/scholar_pipeline/paper_21.pdf (2.4 MB)
# SUCCESS: Downloaded via Chrome PDF Viewer: from https://www.nature.com/articles/s41598-019-48870-2.pdf to /tmp/scholar_pipeline/paper_21.pdf
# http://www.pnas.org/content/107/7/3228.full.pdf
# INFO: openurl_resolver_url resolved as https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# INFO: use_cache_url_finder resolved as True
# INFO: Trying method: From Response Body
# INFO: Trying to download http://www.pnas.org/content/107/7/3228.full.pdf from response body
# INFO: Failed download from response body
# INFO: Trying method: Direct Download
# INFO: Trying direct download from http://www.pnas.org/content/107/7/3228.full.pdf
# INFO: Trying method: Chrome PDF
# INFO: PDF viewer detected
# ERROR: Chrome page download failed: Timeout 30000ms exceeded while waiting for event "download"
# =========================== logs ===========================
# waiting for event "download"
# ============================================================
# FAIL: Failed via Chrome PDF Viewer: from http://www.pnas.org/content/107/7/3228.full.pdf to /tmp/scholar_pipeline/paper_22.pdf
# FAIL: All download methods failed for http://www.pnas.org/content/107/7/3228.full.pdf
# http://www.pnas.org/content/110/8/3107.full.pdf
# INFO: openurl_resolver_url resolved as https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# INFO: use_cache_url_finder resolved as True
# INFO: Trying method: From Response Body
# INFO: Trying to download http://www.pnas.org/content/110/8/3107.full.pdf from response body
# INFO: Failed download from response body
# INFO: Trying method: Direct Download
# INFO: Trying direct download from http://www.pnas.org/content/110/8/3107.full.pdf
# INFO: Trying method: Chrome PDF
# INFO: PDF viewer detected
# ERROR: Chrome page download failed: Timeout 30000ms exceeded while waiting for event "download"
# =========================== logs ===========================
# waiting for event "download"
# ============================================================
# FAIL: Failed via Chrome PDF Viewer: from http://www.pnas.org/content/110/8/3107.full.pdf to /tmp/scholar_pipeline/paper_23.pdf
# FAIL: All download methods failed for http://www.pnas.org/content/110/8/3107.full.pdf
# http://www.pnas.org/content/110/12/4780.full.pdf
# INFO: openurl_resolver_url resolved as https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# INFO: use_cache_url_finder resolved as True
# INFO: Trying method: From Response Body
# INFO: Trying to download http://www.pnas.org/content/110/12/4780.full.pdf from response body
# INFO: Failed download from response body
# INFO: Trying method: Direct Download
# INFO: Trying direct download from http://www.pnas.org/content/110/12/4780.full.pdf
# INFO: Trying method: Chrome PDF
# INFO: PDF viewer detected
# ERROR: Chrome page download failed: Timeout 30000ms exceeded while waiting for event "download"
# =========================== logs ===========================
# waiting for event "download"
# ============================================================
# FAIL: Failed via Chrome PDF Viewer: from http://www.pnas.org/content/110/12/4780.full.pdf to /tmp/scholar_pipeline/paper_24.pdf
# FAIL: All download methods failed for http://www.pnas.org/content/110/12/4780.full.pdf
# https://www.biorxiv.org/content/early/2018/03/28/290361.full.pdf
# INFO: openurl_resolver_url resolved as https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# INFO: use_cache_url_finder resolved as True
# INFO: Trying method: From Response Body
# INFO: Trying to download https://www.biorxiv.org/content/early/2018/03/28/290361.full.pdf from response body
# INFO: Failed download from response body
# INFO: Trying method: Direct Download
# INFO: Trying direct download from https://www.biorxiv.org/content/early/2018/03/28/290361.full.pdf
# INFO: Trying method: Chrome PDF
# INFO: PDF viewer detected
# SUCCESS: Downloaded: /tmp/scholar_pipeline/paper_25.pdf (1.5 MB)
# SUCCESS: Downloaded via Chrome PDF Viewer: from https://www.biorxiv.org/content/early/2018/03/28/290361.full.pdf to /tmp/scholar_pipeline/paper_25.pdf
# https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2010.00191/pdf
# INFO: openurl_resolver_url resolved as https://unimelb.hosted.exlibrisgroup.com/sfxlcl41
# INFO: use_cache_url_finder resolved as True
# INFO: Trying method: From Response Body
# INFO: Trying to download https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2010.00191/pdf from response body
# INFO: Failed download from response body
# INFO: Trying method: Direct Download
# INFO: Trying direct download from https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2010.00191/pdf
# INFO: ERR_ABORTED detected - likely direct download
# SUCCESS: Direct download: from https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2010.00191/pdf to /tmp/scholar_pipeline/paper_26.pdf (2.71 MiB)
# (.env-3.11) (wsl) scholar $ /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/examples/99_fullpipeline-for-bibtex.py^C^C
# (.env-3.11) (wsl) scholar $

# EOF
