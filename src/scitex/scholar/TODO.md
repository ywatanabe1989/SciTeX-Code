<!-- ---
!-- Timestamp: 2025-08-22 22:59:15
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/TODO.md
!-- --- -->

Clean approach suggestions for the Scholar storage architecture:

## 1. Move BibTeX handling to ScholarLibrary

File: `/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/storage/ScholarLibrary.py`

Add BibTeX methods:

```python
class ScholarLibrary:
    def papers_from_bibtex(self, bibtex_input: Union[str, Path]) -> List["Paper"]:
        """Create Papers from BibTeX file or content."""
        # Move the bibtex detection and parsing logic here
        return papers_list
    
    def paper_from_bibtex_entry(self, entry: Dict[str, Any]) -> Optional["Paper"]:
        """Convert BibTeX entry to Paper."""
        # Move _bibtex_entry_to_paper logic here
        return paper
```

## 2. Simplify Papers class

Remove these methods from Papers and delegate to library:
- `from_bibtex` → `ScholarLibrary.papers_from_bibtex`
- `_bibtex_entry_to_paper` → `ScholarLibrary.paper_from_bibtex_entry`
- `_paper_to_bibtex_fields` → move to Paper class

## 3. Move PDF downloading to Scholar class

File: `/home/ywatanabe/proj/SciTeX-Code/src/scitex/scholar/core/_Scholar.py`

```python
class Scholar:
    async def download_pdfs_for_papers_async(self, papers: "Papers", **kwargs) -> Dict[str, Any]:
        """Download PDFs for papers collection."""
        pdf_downloader = ScholarPDFDownloader(self.browser_context, self.config)
        return await pdf_downloader.download_from_papers(papers, **kwargs)
```

## 4. Unified approach:

1. **ScholarLibrary**: Handles all storage operations, BibTeX parsing, similarity calculation
2. **Paper**: Individual paper with basic operations (to_bibtex, to_dict)  
3. **Papers**: Collection operations (filter, sort, summarize) - delegates storage to library
4. **Scholar**: High-level orchestration, PDF downloading, browser operations

This eliminates duplication and creates clear separation of concerns.

<!-- EOF -->