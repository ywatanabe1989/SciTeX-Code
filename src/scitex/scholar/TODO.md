<!-- ---
!-- Timestamp: 2025-10-11 13:36:59
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/TODO.md
!-- --- -->

## !!!IMPORTANT!!! 
## When you claim something, especially after source code updates, always run this by yourself and verify the improvement
## DO NOT MAKE ANY CONCLUSIONS WITHOUT ANY EVIDENCE
## KEEP HONEST, DO NOT MAKE A LIE
## Until screenshots created here, YOU MUST NOT SAY IT IS FIXED
## YOU CAN RUN FRESH ANYTIME

- [ ] Apply full pipeline `./core/ScholarOchestrator.py` to the entries in `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/data/neurovista.bib`, with their DOIs as project neurovista
- [ ] I will not handle manual download so that we can check sucess rate

## Zotero translators
- [ ] Zotero translators for major publishers will work.
  - [ ] However, we need to implement `~/proj/zotero-translators-python`, which is installed via editable mode, `pip install -e`
  - [ ] The corresponding javascript code are authentic community-implementations
  - [ ] We need to translate the zotero translators writtein in Javascript into Python script

## Parallel Execution
- [ ] Running entries can be in parallel. However, we need to care about auth lock. (this is really suspicious)
- [ ] When running multiple chrome instances, WE HAVE TO USE DIFFERENT PROFILES TO AVOID CRASHES.
- [ ] For chrome profile name we can specify the following profiles, which are stored in `~/.scitex/scholar/cache/chrome/`:
     - system
     - system_worker_0
     - system_worker_1
     - system_worker_2
     - system_worker_3
     - system_worker_4
     - system_worker_5
     - system_worker_6
     - system_worker_7

## Debugging
- [ ] Debug mode available (`$ stx_set_loglevel debug`)
- [ ] Simple debugging `./url/ScholarURLFinder.py`
- [ ] Simple debugging `./pdf/ScholarPDFDownloader.py`
- [ ] Screenshots, terminal logs

## Visual insights
- [ ] I saw PDF viewer but `chrome_pdf_viewer download strategy` (This is quite powerful!) seemed not working for  10.1093/brain/awy210 (Oxford Brain) -> working!

## Implementation requests
- [ ] Screenshot paths should be logged in full path. Update `browser_logger`
- [ ] When one pdf downloading strategy succeeds, skip the rest of strategies
- [ ] Authentication gateway should be used for both url finding and pdf downloading
  - [ ] I am not sure they can share across pages if context is the same

<!-- ``` bash
 !-- run_neurovista_pipeline() {
 !--     local fresh_start=$1
 !--     LOG_PATH="./FULL_DOWNLOAD_LOG.txt"
 !--     echo $LOG_PATH > $LOG_PATH
 !--     NV_LIBRARY="$HOME/.scitex/scholar/library/neurovista/"
 !--     
 !--     if [ "$fresh_start" = "true" ]; then
 !--         rm -rf ~/.scitex/scholar/library/*
 !--         rm -rf ~/.scitex/scholar/cache/{engine,url,download}
 !--     fi
 !--     
 !--     n_pdfs=$(tree "$NV_LIBRARY" 2>/dev/null | grep ".pdf$" | wc -l)
 !--     echo "$n_pdfs PDFs found" 2>&1 | ctee.sh -a $LOG_PATH 2>&1
 !--     
 !--     cd ~/proj/scitex_repo/src/scitex/scholar
 !--     python -m scitex.scholar \
 !--         --bibtex data/neurovista.bib \
 !--         --output data/neurovista_enriched.bib \
 !--         --project neurovista \
 !--         --browser interactive \
 !--          2>&1 | ctee.sh -a $LOG_PATH 2>&1
 !--     
 !--     python -m scitex.scholar \
 !--         --bibtex data/neurovista_enriched.bib \
 !--         --project neurovista \
 !--         --browser interactive \
 !--         --download \
 !--          2>&1 | ctee.sh -a $LOG_PATH 2>&1
 !-- 
 !--     python -m scitex.scholar \
 !--         --project neurovista \
 !--         --list
 !-- 
 !--     tree "$NV_LIBRARY"  2>&1 | ctee.sh -a $LOG_PATH 2>&1
 !--     n_pdfs=$(tree "$NV_LIBRARY" 2>/dev/null | grep ".pdf$" | wc -l)
 !--     echo "$n_pdfs PDFs found" 2>&1 | ctee.sh -a $LOG_PATH 2>&1
 !-- }
 !-- 
 !-- run_neurovista_pipeline
 !-- # run_neurovista_pipeline true
 !-- ```
 !-- 
 !-- - [ ] DOI Engines as list
 !-- 
 !--   1. Pydantic Validation Error - *_engines fields are stored as strings instead of lists:
 !--     - "doi_engines": "ScholarURLFinder" ❌
 !--     - Should be: "doi_engines": ["ScholarURLFinder"] ✅
 !-- 
 !-- 
 !-- ## Manual Mode
 !-- - [ ] Shows "Stop Automation" button on browser all the time
 !--   - [ ] Responsive visual feedback and instructions
 !-- - [ ] When the button pressed, automation stops
 !--   - [ ] On the other hand, another automation - download monitoring - starts.
 !--   - [ ] When download detected, correctly verify, move, and rename saved PDF to the library just as the automation system does. -->

<!-- EOF -->