<!-- ---
!-- Timestamp: 2025-10-08 06:01:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/TODO.md
!-- --- -->

## !!!IMPORTANT!!! 
## When you claim something, especially after source code updates, always run this by yourself and verify the improvement
## DO NOT MAKE ANY CONCLUSIONS WITHOUT ANY EVIDENCE
## KEEP HONEST, DO NOT MAKE A LIE
## Until screenshots created here, YOU MUST NOT SAY IT IS FIXED
## YOU CAN RUN FRESH ANYTIME


``` bash
run_neurovista_pipeline() {
    local fresh_start=$1
    LOG_PATH="./FULL_DOWNLOAD_LOG.txt"
    echo $LOG_PATH > $LOG_PATH
    NV_LIBRARY="$HOME/.scitex/scholar/library/neurovista/"
    
    if [ "$fresh_start" = "true" ]; then
        rm -rf ~/.scitex/scholar/library/*
        rm -f ~/.scitex/scholar/cache/url_finder/*.json
    fi
    
    n_pdfs=$(tree "$NV_LIBRARY" 2>/dev/null | grep ".pdf$" | wc -l)
    echo "$n_pdfs PDFs found" 2>&1 | tee -a $LOG_PATH 2>&1
    
    cd ~/proj/scitex_repo/src/scitex/scholar
    python -m scitex.scholar \
        --bibtex data/neurovista.bib \
        --output data/neurovista_enriched.bib \
        --project neurovista \
         2>&1 | tee -a $LOG_PATH 2>&1
    
    python -m scitex.scholar \
        --bibtex data/neurovista_enriched.bib \
        --project neurovista \
        --download \
         2>&1 | tee -a $LOG_PATH 2>&1

    python -m scitex.scholar \
        --project neurovista \
        --list

    tree "$NV_LIBRARY"  2>&1 | tee -a $LOG_PATH 2>&1
    n_pdfs=$(tree "$NV_LIBRARY" 2>/dev/null | grep ".pdf$" | wc -l)
    echo "$n_pdfs PDFs found" 2>&1 | tee -a $LOG_PATH 2>&1
}

run_neurovista_pipeline
```

- [ ] Manual Investigation
  2. D26B4E35 - Sirbu 2025 (SSRN preprint)
     ```
     Download Log for 10.2139/ssrn.5293145
     ============================================================
     Started at: 2025-10-08T00:47:02.166572
     Worker ID: 0
     Paper ID: D26B4E35

     ============================================================
     URL FINDER RESULTS:
     ============================================================
     url_doi: https://doi.org/10.2139/ssrn.5293145
     url_openurl_query: https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.2139/ssrn.5293145

     ============================================================
     STATUS: NO PDF URLS FOUND
     The URL finder could not locate any PDF download links.
     ============================================================
     ```
     ~/proj/scitex_repo/src/scitex/scholar/library/neurovista/PDF-2f_CC-000001_IF-000_2025_Sirbu_ArXiv/

  3. 36DA45DE - Baldassano 2019 (IOP Journal of Neural Engineering)
    ~/proj/scitex_repo/src/scitex/scholar/library/neurovista/PDF-2f_CC-000000_IF-003_2019_Baldassano_Journal-of-Neural-Engineering/
    ```
    Download Log for 10.1088/1741-2552/aaf92e
    ============================================================
    Started at: 2025-10-08T00:44:19.994415
    Worker ID: 1
    Paper ID: 36DA45DE

    ============================================================
    URL FINDER RESULTS:
    ============================================================
    url_doi: https://doi.org/10.1088/1741-2552/aaf92e
    url_openurl_query: https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.1088/1741-2552/aaf92e

    ============================================================
    STATUS: NO PDF URLS FOUND
    The URL finder could not locate any PDF download links.
    ============================================================
    ```
  4. 3ADFFF45 - Davis 2011 (Epilepsy Research)
    ```
    Download Log for 10.1016/j.eplepsyres.2011.05.011
    ============================================================
    Started at: 2025-10-08T05:41:18.627262
    Worker ID: 2
    Paper ID: 3ADFFF45

    ============================================================
    URL FINDER RESULTS:
    ============================================================
    url_doi: https://doi.org/10.1016/j.eplepsyres.2011.05.011
    url_publisher: https://linkinghub.elsevier.com/retrieve/pii/S0920121111001318
    url_openurl_query: https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.1016/j.eplepsyres.2011.05.011
    url_openurl_resolved: https://www.sciencedirect.com/science/article/abs/pii/S0920121111001318?via%3Dihub
    urls_pdf: [{'url': 'https://www.sciencedirect.com/science/article/pii/S0920121111001318/pdfft', 'source': 'publisher_pattern'}]

    ============================================================
    Attempting 1 PDF URL(s):
    ============================================================

    ------------------------------------------------------------
    URL 1/1: https://www.sciencedirect.com/science/article/pii/S0920121111001318/pdfft
    Method: Screenshot-enabled download
    ```
    ~/proj/scitex_repo/src/scitex/scholar/library/neurovista/PDF-1r_CC-000110_IF-002_2011_Davis_Epilepsy-Research/
    ~/proj/scitex_repo/src/scitex/scholar/library/neurovista/PDF-1r_CC-000110_IF-002_2011_Davis_Epilepsy-Research/screenshots/
    May need to redirect from OpenURL or strictly paywalled
    Science direct
    Needs to click "Access through your institution"
    Needs wait until the journal page with "View PDF" button shown

  6. 1CDA22A9 - Cook 2013 (Lancet Neurology)
     No openurl resolved
     No screenshots

<!-- EOF -->