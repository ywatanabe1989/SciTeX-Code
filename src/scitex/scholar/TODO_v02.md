<!-- ---
!-- Timestamp: 2025-10-12 00:52:30
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/TODO.md
!-- --- -->

# Scholar Module TODO

## Release Preparation

### Code Organization and Cleanup
- [ ] Rename engines module to metadata_engines for clarity
- [ ] Rename url to url_finder
- [ ] Rename download to pdf_download
- [ ] Review and refactor Scholar class implementation (src/scitex/scholar/core/Scholar.py)
- [ ] Consolidate externals and extra modules into unified impact_factor module
- [ ] Refactor storage module to remove unused components
- [ ] Reorganize utils module for better maintainability (src/scitex/scholar/utils/)
  - [ ] utils might be "too general"

### Configuration System
- [ ] Organize configuration YAML files
  - [ ] Split into categorized configuration files
  - [ ] Implement hierarchical configuration structure
  - [ ] Reference: src/scitex/io/_load_configs.py

### API Enhancements
- [ ] Implement ext=None option in stx.io.load() to handle files without extensions
  - [ ] Refactor src/scitex/scholar/download/utils.py to use stx.io.load(IUD_path, ext="pdf")
  - [ ] Consider temporary RAM file approach

### Documentation and Examples
- [ ] Create demonstration video/tutorial
- [ ] Update README.md files to reflect current codebase
- [ ] Revise and restructure ./examples for current implementation
- [ ] Update CLI and __main__.py interfaces

### Known Limitations
- [ ] Document JCR data requirement in externals module
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