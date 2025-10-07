<!-- ---
!-- Timestamp: 2025-10-08 00:44:11
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/TODO.md
!-- --- -->

## !!!IMPORTANT!!! 
## When you claim something, especially after source code updates, always run this by yourself and verify the improvement
## DO NOT MAKE ANY CONCLUSIONS WITHOUT ANY EVIDENCE
## KEEP HONEST, DO NOT MAKE A LIE

``` bash

run_neurovista_pipeline() {
    local fresh_start=$1
    LOG_PATH="./FULL_DOWNLOAD_LOG.txt"
    echo > $LOG_PATH
    NV_LIBRARY="$HOME/.scitex/scholar/library/neurovista/"
    
    if [ "$fresh_start" = "true" ]; then
        rm -rf ~/.scitex/scholar/library/*
        rm -f ~/.scitex/scholar/cache/url_finder/*.json
    fi
    
    n_pdfs=$(tree "$NV_LIBRARY" 2>/dev/null | grep ".pdf$" | wc -l)
    echo "$n_pdfs" | tee -a $LOG_PATH
    
    cd ~/proj/scitex_repo/src/scitex/scholar
    python -m scitex.scholar \
        --bibtex data/neurovista.bib \
        --output data/neurovista_enriched.bib \
        --project neurovista \
        | tee -a $LOG_PATH
    
    python -m scitex.scholar \
        --bibtex data/neurovista_enriched.bib \
        --project neurovista \
        --download \
        | tee -a $LOG_PATH
    
    tree "$NV_LIBRARY" | tee -a $LOG_PATH
    n_pdfs=$(tree "$NV_LIBRARY" 2>/dev/null | grep ".pdf$" | wc -l)
    echo "$n_pdfs" | tee -a $LOG_PATH
}

run_neurovista_pipeline
```

- [ ] Creating workers takes time
  - [ ] Are the profile files not rsynced effectively?
  - [ ] Are the profile files not kept persistently?

- [ ] Symlink status updates (PDF_r/PDF_s/PDF_f) - PARTIAL FIX
  - [x] Added LibraryManager.update_symlink() method for explicit symlink updates
  - [x] Three checkpoints implemented:
    1. Line 710: PDF_r when download starts (.downloading marker created)
    2. Line 976 (_save_to_library): PDF_s after successful save (called automatically)
    3. Line 850: PDF_f after all attempts fail
  - [x] save_resolved_paper() now handles both Pydantic Paper and dict objects
  - [x] Simplified _save_to_library() to use update_symlink() (removed manual readable name generation)
  - [x] **FIXED**: Metadata extraction issue - update_symlink() now reads nested structure correctly
    - Lines 1009-1024: Added proper extraction of authors/year/journal from nested metadata
    - Was accessing `metadata.get('year')` but should access `metadata['metadata']['basic']['year']`
  - [ ] **BUG**: Symlinks not updating from PDF_r to PDF_s even after PDF downloaded
    - Metadata now works but status transitions (r→s→f) still not working
  - [ ] Testing: Need fresh download run to verify metadata shows correctly AND status transitions work

- [x] Use ScholarConfig cascade for cache control
  - Config key: `use_cache_url_finder` in config/default.yaml
  - Env var: `SCITEX_SCHOLAR_USE_CACHE_URL_FINDER=false` to disable
  - --download-force automatically sets env var to disable URL finder cache
  - Implemented in ScholarURLFinder using config.resolve() pattern

- [ ] Screenshots are white
  - [ ] ~/proj/scitex_repo/src/scitex/scholar/library/neurovista/CC_000000-PDF_r-IF_003-2024-Yang-Clinical-Neurophysiology/screenshots/
  - [ ] Until screenshots created here, YOU MUST NOT SAY IT IS FIXED
  - [ ] YOU CAN RUN FRESH ANYTIME

- [x] Meta characters in titles cause search failures - FIXED & VERIFIED
  - [x] Added _clean_query() method to BaseDOIEngine (inherited by all engines)
  - [x] Removes meta characters: ()[]{}!@#$%^&*+=<>?/\|~`"':;
  - [x] Keeps: letters, numbers, spaces, hyphens, periods, commas
  - [x] Collapses multiple spaces into one
  - [x] Used in SemanticScholarEngine._search_by_metadata() (line 158)
  - [x] Tested in .dev/meta_characters_test/ - all tests pass
  - [x] Verified with actual LSTM paper - found in Semantic Scholar (corpus_id: 262046731)
  - Example: "(LSTM)" → "LSTM", search succeeds and finds correct paper

- [x] Papers with no DOI now have arXiv/Corpus ID support - PARTIAL FIX
  - Example: /home/ywatanabe/.scitex/scholar/library/MASTER/02452894/metadata.json
  - Title: "Epileptic seizure forecasting with long short-term memory (LSTM) neural networks"
  - Has: title, authors, year, abstract, **arXiv ID: 2309.09471**, **Corpus ID: 262046731**
  - Missing: DOI (genuinely not available for this paper)
  - [x] Added corpus_id field to Paper.py IDMetadata
  - [x] SemanticScholarEngine now extracts arXiv ID, PMID, Corpus ID
  - [x] Added arxiv and corpus_id URL fields to URLMetadata
  - [x] Paper class automatically generates URLs from IDs (sync_ids_and_urls validator)
  - [x] Added convert_corpus_id_to_doi_async() to extract DOI from Semantic Scholar page
  - [ ] **TODO**: Integrate arXiv URL into download pipeline as fallback
  - [ ] **TODO**: Use convert_corpus_id_to_doi_async() when DOI missing but corpus_id available

- [x] Understand and use ScholarConfig appropriately
  - Pattern: `self.param_name = config.resolve("param_name", param_name, default=default_value)`
  - Cascade priority: Direct spec → Env var (SCITEX_SCHOLAR_*) → Config file → Default
  - Example implemented: ScholarURLFinder now uses `config.resolve("use_cache_url_finder", ...)`
  - --download-force sets `SCITEX_SCHOLAR_USE_CACHE_URL_FINDER=false` to cascade through system

- [ ] Manual Investigation
  1. 39305E03 - Ahmad 2022 (IEEE conference, not subscribed)
     ~/proj/scitex_repo/src/scitex/scholar/scholar/library/neurovista/CC_000001-PDF_p-IF_000-2022-Ahmad-2022-4th-Novel-Intelligent-and/
     Already resolved: https://ieeexplore.ieee.org/search/searchresult.jsp?searchWithin=%22Publication%20Number%22:9942273&searchWithin=%22Document%20Title%22:FPGA%20Implementation%20of%20Epileptic%20Seizure%20Detection%20using%20Artificial%20Neural%20Network
     For IEEE, we can find a button to open the PDF with chrome viewer
     Might be possible to build link from information given:
     For example, the URL for this entry is: https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=9942397
        
  2. D26B4E35 - Sirbu 2025 (SSRN preprint)
     ~/proj/scitex_repo/src/scitex/scholar/scholar/library/neurovista/CC_000001-PDF_p-IF_000-2025-Sirbu-ArXiv/
     Captcha might block
     OpenURL query must be resolved from "Unpaywall" link
     "openurl_query": "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.2139/ssrn.5293145"
     Open Access version of full text found via Unpaywall
  3. 36DA45DE - Baldassano 2019 (IOP Journal of Neural Engineering)
     ~/proj/scitex_repo/src/scitex/scholar/scholar/library/neurovista/CC_000000-PDF_p-IF_003-2019-Baldassano-Journal-of-Neural-Engineering/
     Available from Institute of Physics Journals
  4. 3ADFFF45 - Davis 2011 (Epilepsy Research)
     ~/proj/scitex_repo/src/scitex/scholar/scholar/library/neurovista/CC_000110-PDF_p-IF_002-2011-Davis-Epilepsy-Research/
     Science direct
     Needs to click "Access through your institution"
     Needs wait until the journal page with "View PDF" button shown
     Maybe this is strictly paywalled
  5. D7D3ADE9 - Lu 2025 (IEEE Journal)
     ~/proj/scitex_repo/src/scitex/scholar/scholar/library/neurovista/CC_000000-PDF_p-IF_006-2025-Lu-IEEE-Journal-of-Biomedical-and/
    Available from IEEE Electronic Library (IEL) Journals 
  6. 1CDA22A9 - Cook 2013 (Lancet Neurology)
     Resolved: https://www.thelancet.com/journals/laneur/article/PIIS1474-4422(13)70075-9/fulltext
     OpenFlare captcha there


- LOG:

<!-- EOF -->