<!-- ---
!-- Timestamp: 2025-10-12 00:04:25
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/TODO.md
!-- --- -->

## !!!IMPORTANT!!! 
## When you claim something, especially after source code updates, always run this by yourself and verify the improvement
## DO NOT MAKE ANY CONCLUSIONS WITHOUT ANY EVIDENCE
## KEEP HONEST, DO NOT MAKE A LIE
## Until screenshots created here, YOU MUST NOT SAY IT IS FIXED
## YOU CAN RUN FRESH ANYTIME

## For publishing release
- [ ] Demo movie
- [ ] Clean the scholar module for release in a professional manner
- [ ] Update README.md files to the current, latest codebase
- [ ] Update cli and __main__.py
- [ ] Organize config yaml file
  - [ ] Splitting into categorized config yaml files
  - [ ] Add hierarchy
  - [ ] This might be useful to learn how to merge configs from separated files
    - [ ] /home/ywatanabe/proj/scitex_repo/src/scitex/io/_load_configs.py
- [ ] Do we still need Scholar class? /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/core/Scholar.py
- [ ] stx.io.load would be better to implement ext=None option to handle files without exts
  - [ ] /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/download/utils.py
    - [ ] This can be replaced by simply stx.io.load(IUD_path, ext="pdf")
    - [ ] Maybe using temporal RAM file
- [ ] We can revise/restructure ./examples for the current codebase
- [ ] In externals, we uses JCR; however, this is only valid for users with the data in a valid route
- [ ] extrnals and extra should be summarized as impact_factor
- [ ] engines can be renamed as metadata
- [ ] storage should be refactored; some of them are not used
- [ ] Refactor utils
  - [ ] ~/proj/scitex_repo/src/scitex/scholar/utils/

## Failure case study
- [ ] Implement failure analyses
- [ ] Which journal is not covered
  - [ ] Which translator should be improved
  - [ ] What screenshots/logs collected

## Zotero translators
- [ ] Zotero translators for major publishers will work.
  - [ ] However, we need to implement `~/proj/zotero-translators-python`, which is installed via editable mode, `pip install -e`
  - [ ] The corresponding javascript code are authentic community-implementations
  - [ ] We need to translate the zotero translators writtein in Javascript into Python script

## Debugging
- [ ] Debug mode available (`$ stx_set_loglevel debug`)
- [ ] Step-by-step debugging `./url/ScholarURLFinder.py`
- [ ] Simple debugging `./pdf/ScholarPDFDownloader.py`
- [ ] Screenshots, terminal logs

<!-- EOF -->