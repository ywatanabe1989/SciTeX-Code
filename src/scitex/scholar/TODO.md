<!-- ---
!-- Timestamp: 2025-10-13 09:07:18
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/TODO.md
!-- --- -->

# Scholar Module TODO

## Release Preparation

<!-- ### Adjustment
 !-- - [ ] Style of Journal Names should be normalized
 !--   - [ ] NG: PDF-00_CC-000000_IF-000_2025_Lu_IEEE J. Biomed. Health Inform -> ../MASTER/D7D3ADE9
 !--   - [ ] OK: PDF-00_CC-000000_IF-000_2025_Lu_IEEE-J.-Biomed.-Health-Inform -> ../MASTER/D7D3ADE9
 !--   - [ ] NG: Andrade-2024-FrontNeurosci.pdf
 !--   - [ ] OK: Andrade-2024-Front-Neurosci.pdf
 !--   - [ ] Fix them: in /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/config/core/_PathManager.py and use them throught the codebase when these names needed; keep one source of truth 
 !--     def get_library_project_entry_dirname(
 !--         self,
 !--         n_pdfs: int,
 !--         citation_count: int,
 !--         impact_factor: int,
 !--         year: int,
 !--         first_author: str,
 !--         journal_name: str,
 !--     ) -> str:
 !--         """Format entry directory name using PATH_STRUCTURE template.
 !-- 
 !--         Args:
 !--             n_pdfs: Number of PDF files (0, 1, 2, ...)
 !--             citation_count: Total citation count
 !--             impact_factor: Journal impact factor
 !--             year: Publication year
 !--             first_author: First author last name
 !--             journal_name: Journal name
 !-- 
 !--         Returns:
 !--             Formatted directory name
 !--         """
 !--         first_author = self._sanitize_filename(first_author)
 !--         journal_name = self._sanitize_filename(journal_name)
 !--         return PATH_STRUCTURE["library_project_entry_dirname"].format(
 !--             n_pdfs=n_pdfs,
 !--             citation_count=citation_count,
 !--             impact_factor=impact_factor,
 !--             year=year,
 !--             first_author=first_author,
 !--             journal_name=journal_name,
 !--         )
 !-- 
 !--     def get_library_project_entry_pdf_fname(
 !--         self, first_author: str, year: int, journal_name: str
 !--     ) -> str:
 !--         """Format PDF filename using PATH_STRUCTURE template."""
 !--         first_author = self._sanitize_filename(first_author)
 !--         journal_name = self._sanitize_filename(journal_name)
 !--         return PATH_STRUCTURE["library_project_entry_pdf_fname"].format(
 !--             first_author=first_author,
 !--             year=year,
 !--             journal_name=journal_name,
 !--         )
 !-- 
 !-- - [ ] `info` dir needed for each project
 !--   - [ ] /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/library/neurovista/info
 !--   - [ ] info/bibliography/xxx.bib
 !--   - [ ] info/bibliography/yyy.bib
 !--   - [ ] info/bibliography/merged.bib
 !--   - [ ] info/neurovista.bib -> bibliography/merged.bib
 !--   - [ ] Use the logic of /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/cli/handlers/bibtex_handler.py
 !--     - [ ] Also, please implement this to "all pipelines"
 !--       - [ ] Sometimes, this is created from imported bibtex files
 !--       - [ ] Sometimes, we need to implement this from all entries in the project for expooooortinggg
 !--   - [ ] The logic should be implemented in /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/storage/BibTeXHandler.py and reused throught the project to keep single truth
 !--   - [ ] What are differences between BibliographyManager and BibTeXHandler?
 !-- 
 !-- - [ ] Organize pipelines and keep single source of truth
 !--   - [ ] core/*Pipeline*.py
 !--   - [ ] pipelines/*.py
 !--     - [ ] Which are the primary, centralized pipelines?
 !--   - [ ] __main__.py
 !--   - [ ] cli/*.py
 !--     - [ ] This must delegate to actual implementations to keep readability -->

### Configuration System
- [ ] Organize configuration YAML files
  - [ ] Split into categorized configuration files
  - [ ] Implement hierarchical configuration structure
  - [ ] Reference: src/scitex/io/_load_configs.py

### Documentation and Examples
- [ ] Create demonstration video/tutorial
- [ ] Update README.md files to reflect current codebase
- [ ] Revise and restructure ./examples for current implementation
- [ ] Update CLI and __main__.py interfaces

### Known Limitations
- [ ] Document JCR data requirement in impact_factor module
- [ ] Add fallback mechanisms for users without JCR access

## Testing and Quality Assurance

### Failure Analysis
- [ ] Implement comprehensive failure analysis system
- [ ] Identify unsupported journals and publishers
- [ ] Determine which translators require improvement
- [ ] Collect and organize screenshots/logs for debugging

### Debugging Tools
- [ ] Ensure debug mode functionality (`$ stx_set_loglevel debug`)
- [ ] Implement step-by-step debugging for ScholarURLFinder
- [ ] Enhance debugging output for ScholarPDFDownloader
- [ ] Improve screenshot and terminal log collection

## Zotero compatibility

### Implementation Status
- [ ] Complete Zotero translator support for major publishers
- [ ] Develop Python port of zotero-translators (installed via `pip install -e`)
- [ ] Translate community-maintained JavaScript translators to Python
- [ ] Maintain compatibility with authentic community implementations

### Move zotero translator into this module
- [ ] whether to include `zotero_translator` as a keyword
- [ ] Zotero importing/exporting for compatibility
- [ ] Zotero database
  - [ ] We have pure zotero library at ~/Zotero/
  - [ ] So, we can check/implement compatibility layers
- [ ] Positioning scholar module as "Zotero Enhancer" would collect attraction easily

### SciTeX Cloud
- [ ] Expose scitex scholar usable in web (https://scitex.ai; django; ~/proj/scitex-cloud)

<!-- EOF -->