<!-- ---
!-- Timestamp: 2025-10-13 09:50:27
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/TODO.md
!-- --- -->

# Scholar Module TODO

## Release Preparation

### Config System
- [ ] Organize ./config/default.yaml in separated yaml files while ensuring current codebase works

### Documentation and Examples
- [ ] Update README.md files to reflect current codebase
- [ ] Create demonstration video/tutorial
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