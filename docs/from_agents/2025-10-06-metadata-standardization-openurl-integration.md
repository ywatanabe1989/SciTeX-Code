# Metadata Standardization and OpenURL Integration

**Date**: 2025-10-06
**Agent**: Claude Code
**Context**: Implementing consistent metadata format across Scholar library

## Problem Statement

Two critical issues were identified in the Scholar library system:

1. **Metadata format inconsistency**: JSON metadata files were using a flat structure instead of the standardized nested OrderedDict format defined in `_standardize_metadata.py`

2. **Missing URL information**: OpenURL resolution URLs (which contain authentication info for accessing paywalled papers through University of Melbourne) were being generated during downloads but NOT saved to metadata

## Root Cause

The download process was:
1. Calling `ScholarURLFinder.find_urls(doi)` to get all URLs including:
   - `url_doi`: Direct DOI URL
   - `url_publisher`: Publisher's page URL
   - `url_openurl_query`: OpenURL query string
   - `url_openurl_resolved`: **Authenticated URL with subscription access**
   - `urls_pdf`: List of PDF URLs

2. Downloading PDFs using these URLs

3. **BUT** only saving basic paper metadata (title, authors, year, etc.) - **NOT the URL information**

This meant losing critical information about:
- How the paper was accessed
- Which authentication path was used
- What URLs were tried and succeeded/failed

## Solution

### 1. Updated ParallelPDFDownloader (3 changes)

**File**: `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/download/ParallelPDFDownloader.py`

#### Change 1: Pass URL info through download pipeline
```python
# Line 335-351: Parallel worker download
urls = await url_finder.find_urls(doi)
pdf_urls = urls.get("urls_pdf", [])

success = await self._download_single_pdf(
    paper, pdf_urls, pdf_downloader,
    project, library_dir, worker_id,
    url_info=urls  # ← ADDED: Pass all URL info
)
```

#### Change 2: Sequential download path
```python
# Line 416-428: Sequential download
success = await self._download_single_pdf(
    paper, pdf_urls, pdf_downloader,
    project, library_dir, worker_id=0,
    url_info=urls  # ← ADDED: Pass all URL info
)
```

#### Change 3: Update method signatures and save URLs
```python
# Line 454: Method signature
async def _download_single_pdf(
    self, paper, pdf_urls, pdf_downloader,
    project, library_dir, worker_id,
    url_info: Dict = None  # ← ADDED
):
    ...
    # Line 498: Pass to library save
    saved = self._save_to_library(
        paper, result, project, library_dir,
        url_info=url_info  # ← ADDED
    )

# Line 518: Save method signature
def _save_to_library(
    self, paper, pdf_path, project, library_dir,
    url_info: Dict = None  # ← ADDED
):
    ...
    # Line 552-558: Save URL info to metadata
    if url_info:
        metadata["url_doi"] = url_info.get("url_doi")
        metadata["url_publisher"] = url_info.get("url_publisher")
        metadata["url_openurl_query"] = url_info.get("url_openurl_query")
        metadata["url_openurl_resolved"] = url_info.get("url_openurl_resolved")
        metadata["urls_pdf"] = url_info.get("urls_pdf", [])
```

### 2. Updated LibraryManager for Standardized Format

**File**: `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/storage/_LibraryManager.py`

#### Added imports (Line 12-25):
```python
from collections import OrderedDict
import copy
from scitex.scholar.engines.utils import standardize_metadata, BASE_STRUCTURE
```

#### Added conversion method (Line 47-121):
```python
def _convert_to_standardized_metadata(self, flat_metadata: Dict) -> OrderedDict:
    """Convert flat metadata dict to standardized nested structure with _engines tracking."""
    standardized = copy.deepcopy(BASE_STRUCTURE)

    # ID section
    standardized["id"]["doi"] = flat_metadata["doi"]
    standardized["id"]["doi_engines"] = flat_metadata.get("doi_source")
    standardized["id"]["scholar_id"] = flat_metadata.get("scitex_id")

    # Basic section
    standardized["basic"]["title"] = flat_metadata["title"]
    standardized["basic"]["title_engines"] = flat_metadata.get("title_source")
    standardized["basic"]["authors"] = flat_metadata["authors"]
    standardized["basic"]["authors_engines"] = flat_metadata.get("authors_source")
    # ... more fields

    # URL section
    standardized["url"]["doi"] = flat_metadata.get("url_doi")
    standardized["url"]["publisher"] = flat_metadata.get("url_publisher")
    standardized["url"]["publisher_engines"] = "ScholarURLFinder"
    standardized["url"]["openurl_query"] = flat_metadata.get("url_openurl_query")
    standardized["url"]["openurl_resolved"] = flat_metadata.get("url_openurl_resolved")
    standardized["url"]["openurl_resolved_engines"] = "ScholarURLFinder"
    standardized["url"]["pdfs"] = flat_metadata.get("urls_pdf")
    standardized["url"]["pdfs_engines"] = "ScholarURLFinder"

    # Path section
    standardized["path"]["pdfs"] = [flat_metadata["pdf_path"]]
    standardized["path"]["pdfs_engines"] = "ParallelPDFDownloader"

    return standardized
```

#### Updated save method (Line 394-420):
```python
# Convert to standardized format before saving
standardized_metadata = self._convert_to_standardized_metadata(comprehensive_metadata)

# Wrap with Paper container properties
final_structure = OrderedDict([
    ("metadata", standardized_metadata),
    ("container", OrderedDict([
        ("scitex_id", comprehensive_metadata.get("scitex_id")),
        ("library_id", paper_id),
        ("created_at", comprehensive_metadata.get("created_at")),
        ("created_by", comprehensive_metadata.get("created_by")),
        ("updated_at", comprehensive_metadata.get("updated_at")),
        ("projects", comprehensive_metadata.get("projects", [])),
        ("master_storage_path", str(master_storage_path)),
        ("readable_name", readable_name),
        ("metadata_file", str(master_metadata_file)),
        ("pdf_downloaded_at", comprehensive_metadata.get("pdf_downloaded_at")),
        ("pdf_size_bytes", comprehensive_metadata.get("pdf_size_bytes")),
    ]))
])

with open(master_metadata_file, "w") as file_:
    json.dump(final_structure, file_, indent=2, ensure_ascii=False)
```

## New Metadata Structure

### Before (Flat):
```json
{
  "doi": "10.1093/braincomms/fcaa008",
  "title": "Circadian and multiday seizure periodicities...",
  "title_source": "input",
  "doi_source": null,
  "year": 2020,
  "authors": ["N. Gregg", ...],
  "journal": "Brain Communications",
  "abstract": "...",
  "citation_count": 85,
  "scitex_id": "C74FDF10",
  "pdf_path": "MASTER/C74FDF10/DOI_10.1093_braincomms_fcaa008.pdf"
}
```

### After (Standardized with Container):
```json
{
  "metadata": {
    "id": {
      "doi": "10.1093/braincomms/fcaa008",
      "doi_engines": null,
      "arxiv_id": null,
      "arxiv_id_engines": null,
      "pmid": null,
      "pmid_engines": null,
      "scholar_id": "C74FDF10",
      "scholar_id_engines": null
    },
    "basic": {
      "title": "Circadian and multiday seizure periodicities...",
      "title_engines": "input",
      "authors": ["N. Gregg", ...],
      "authors_engines": "input",
      "year": 2020,
      "year_engines": "input",
      "abstract": "...",
      "abstract_engines": "input"
    },
    "citation_count": {
      "total": 85,
      "total_engines": null
    },
    "publication": {
      "journal": "Brain Communications",
      "journal_engines": "input",
      "impact_factor": null,
      "issn": null,
      "volume": "2",
      "issue": "1"
    },
    "url": {
      "doi": "https://doi.org/10.1093/braincomms/fcaa008",
      "publisher": "https://academic.oup.com/braincomms/article/2/1/fcaa008",
      "publisher_engines": "ScholarURLFinder",
      "openurl_query": "https://unimelb.hosted.exlibrisgroup.com/sfxlcl41?doi=10.1093/braincomms/fcaa008",
      "openurl_resolved": "https://academic.oup.com/braincomms/article/2/1/fcaa008?login=true",
      "openurl_resolved_engines": "ScholarURLFinder",
      "pdfs": [
        {"url": "https://academic.oup.com/braincomms/article-pdf/2/1/fcaa008/32901907/fcaa008.pdf"}
      ],
      "pdfs_engines": "ScholarURLFinder"
    },
    "path": {
      "pdfs": ["MASTER/C74FDF10/DOI_10.1093_braincomms_fcaa008.pdf"],
      "pdfs_engines": "ParallelPDFDownloader"
    },
    "system": {
      "searched_by_CrossRef": null,
      "searched_by_OpenAlex": null,
      ...
    }
  },
  "container": {
    "scitex_id": "C74FDF10",
    "library_id": "C74FDF10",
    "created_at": "2025-10-06T20:32:41.466395",
    "created_by": "SciTeX Scholar",
    "updated_at": "2025-10-06T20:32:41.466444",
    "projects": ["neurovista"],
    "master_storage_path": "/home/ywatanabe/.scitex/scholar/library/MASTER/C74FDF10",
    "readable_name": "Gregg-2020-Brain-Communications",
    "metadata_file": "/home/ywatanabe/.scitex/scholar/library/MASTER/C74FDF10/metadata.json",
    "pdf_downloaded_at": "2025-10-06T20:34:27.712004",
    "pdf_size_bytes": 1176475
  }
}
```

## Benefits

1. **Consistency**: All metadata follows the same standardized format defined in `_standardize_metadata.py`

2. **Source tracking**: Every field has a corresponding `_engines` field tracking which engine/source provided that information

3. **OpenURL preservation**: Authentication-enabled URLs are now saved, enabling:
   - Reproducible access to paywalled papers
   - Debugging download issues
   - Understanding which authentication path worked

4. **Separation of concerns**:
   - `metadata`: Paper content and bibliographic data
   - `container`: Paper storage and system properties

5. **BibTeX compatibility**: The standardized structure can be easily exported to BibTeX while maintaining richer internal structure

6. **Future-proof**: Extensible structure supports adding new fields without breaking existing code

## User Directive

> "always be simple, always standardized, keep it simple"
> "I know that would be too much for bibtex but consistency and stability is more prioritized"

The implementation follows this directive by:
- Using the BASE_STRUCTURE as single source of truth
- Converting all metadata to standardized format
- Accepting that internal structure is richer than BibTeX can represent
- Prioritizing consistency over minimal file size

## Next Steps

Future downloads will automatically use this standardized format. Existing metadata files can be migrated to the new format using a conversion script if needed.

## Related Files

- `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/engines/utils/_standardize_metadata.py` - Defines BASE_STRUCTURE
- `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/url/ScholarURLFinder.py` - Generates URLs including OpenURL resolution
- `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/core/Paper.py` - Paper dataclass defining container properties
