<!-- ---
!-- Timestamp: 2025-10-08 23:20:43
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
        rm -rf ~/.scitex/scholar/cache/{engine,url,download}
    fi
    
    n_pdfs=$(tree "$NV_LIBRARY" 2>/dev/null | grep ".pdf$" | wc -l)
    echo "$n_pdfs PDFs found" 2>&1 | ctee.sh -a $LOG_PATH 2>&1
    
    cd ~/proj/scitex_repo/src/scitex/scholar
    python -m scitex.scholar \
        --bibtex data/neurovista.bib \
        --output data/neurovista_enriched.bib \
        --project neurovista \
        --browser interactive \
         2>&1 | ctee.sh -a $LOG_PATH 2>&1
    
    python -m scitex.scholar \
        --bibtex data/neurovista_enriched.bib \
        --project neurovista \
        --browser interactive \
        --download \
         2>&1 | ctee.sh -a $LOG_PATH 2>&1

    python -m scitex.scholar \
        --project neurovista \
        --list

    tree "$NV_LIBRARY"  2>&1 | ctee.sh -a $LOG_PATH 2>&1
    n_pdfs=$(tree "$NV_LIBRARY" 2>/dev/null | grep ".pdf$" | wc -l)
    echo "$n_pdfs PDFs found" 2>&1 | ctee.sh -a $LOG_PATH 2>&1
}

run_neurovista_pipeline
# run_neurovista_pipeline true
```

- [ ] DOI Engines as list

  1. Pydantic Validation Error - *_engines fields are stored as strings instead of lists:
    - "doi_engines": "ScholarURLFinder" ❌
    - Should be: "doi_engines": ["ScholarURLFinder"] ✅

<!-- EOF -->