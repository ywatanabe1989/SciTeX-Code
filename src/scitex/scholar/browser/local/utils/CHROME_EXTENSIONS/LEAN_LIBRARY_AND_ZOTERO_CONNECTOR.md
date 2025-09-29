<!-- ---
!-- Timestamp: 2025-08-03 22:28:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/browser/local/LEAN_LIBRARY_AND_ZOTERO_CONNECTOR.md
!-- --- -->

# Lean Library & Zotero Connector Extensions

## Lean Library
**Extension ID:** `hghakoefmnkhamdhenpbogkeopjlkpoa`  
**Store Link:** [Lean Library](https://chromewebstore.google.com/detail/lean-library/hghakoefmnkhamdhenpbogkeopjlkpoa)  
**Purpose:** Academic access redirection through institutional authentication

### Verification Test Sites:

#### Primary Test Sites (Should show_async PDF access buttons):
- https://www.science.org/doi/10.1126/science.aao0702
- https://www.nature.com/articles/nature12373
- https://www.cell.com/cell/fulltext/S0092-8674(12)00623-2
- https://onlinelibrary.wiley.com/doi/10.1002/anie.201007988

#### Additional Academic Publishers:
- https://pubs.acs.org/doi/10.1021/ja00051a040
- https://link.springer.com/article/10.1007/s00259-012-2237-0
- https://www.tandfonline.com/doi/full/10.1080/14786419.2012.662648
- https://journals.sagepub.com/doi/10.1177/1745691612459060

#### Expected Behavior:
- PDF access buttons should appear
- "Get PDF" or institutional access links visible
- Lean Library overlay may show_async authentication options

---

## Zotero Connector  
**Extension ID:** `ekhagklcjbdpajgpjgmbionohlpdbjgc`  
**Store Link:** [Zotero Connector](https://chromewebstore.google.com/detail/zotero-connector/ekhagklcjbdpajgpjgmbionohlpdbjgc?hl=en)  
**Purpose:** Save research papers and websites to Zotero library

### Verification Methods:
- **Manual Save:** Ctrl + Shift + S when Zotero is launched
- **Icon Test:** Zotero save icon should appear in browser toolbar on academic pages
- **Automatic Detection:** Extension should detect paper metadata on academic sites

### Test Sites for Zotero Detection:
- https://pubmed.ncbi.nlm.nih.gov/25359968/
- https://arxiv.org/abs/1706.03762
- https://www.biorxiv.org/content/10.1101/2021.06.02.446767v1
- https://scholar.google.com/scholar?q=machine+learning

<!-- EOF -->