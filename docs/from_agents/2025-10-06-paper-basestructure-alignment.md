# Paper Class and BASE_STRUCTURE Alignment

**Date**: 2025-10-06
**Agent**: Claude Code
**Context**: Establishing single source of truth between Paper class and BASE_STRUCTURE

## Design Decision

**BASE_STRUCTURE is the single source of truth for metadata format.**

The Paper class is a **flat convenience wrapper** that maps to/from the nested BASE_STRUCTURE.

## Why This Design?

1. **BASE_STRUCTURE**: Defines the standardized JSON storage format
   - Nested OrderedDict with sections (id, basic, citation_count, publication, url, path, system)
   - Each data field has a corresponding `_engines` field tracking sources
   - Example: `metadata["citation_count"]["total"]` and `metadata["citation_count"]["total_engines"]`

2. **Paper class**: Python dataclass for convenient access
   - Flat structure (Python dataclasses can't have nested field access like `paper.citation_count.total`)
   - Direct field access: `paper.citation_count`, `paper.citation_2025`, `paper.urls_pdf`
   - Source tracking via `sources` dict: `paper.sources["citation_count"] = "CrossRef"`

## Field Mapping

### Citation Counts
```
BASE_STRUCTURE              Paper Class
─────────────────          ─────────────────
citation_count.total   →   citation_count
citation_count.2025    →   citation_2025
citation_count.2024    →   citation_2024
...
```

### URLs
```
BASE_STRUCTURE              Paper Class
─────────────────          ─────────────────
url.doi                →   url_doi
url.publisher          →   url_publisher
url.openurl_query      →   url_openurl_query
url.openurl_resolved   →   url_openurl_resolved
url.pdfs               →   urls_pdf (plural for clarity)
url.supplementary_files →  urls_supplementary
url.additional_files   →   urls_additional
```

### Paths
```
BASE_STRUCTURE              Paper Class
─────────────────          ─────────────────
path.pdfs              →   paths_pdf
path.supplementary_files → paths_supplementary
path.additional_files  →   paths_additional
```

### Direct Mappings (same names)
All other fields map directly:
- `id.doi` → `doi`
- `basic.title` → `title`
- `basic.authors` → `authors`
- `publication.journal` → `journal`
- `publication.impact_factor` → `impact_factor`
- etc.

## Container Fields (Paper-specific)

These fields are in the `container` section of JSON but are top-level in Paper class:

```python
# Container section in JSON
{
  "metadata": { ... BASE_STRUCTURE ... },
  "container": {
    "library_id": "C74FDF10",
    "scitex_id": "C74FDF10",
    "created_at": "2025-10-06T20:32:41",
    "created_by": "SciTeX Scholar",
    "updated_at": "2025-10-06T20:32:41",
    "projects": ["neurovista"],
    "master_storage_path": "/path/to/MASTER/C74FDF10",
    "readable_name": "Gregg-2020-Brain-Communications",
    "metadata_file": "/path/to/metadata.json",
    "pdf_downloaded_at": "2025-10-06T20:34:27",
    "pdf_size_bytes": 1176475
  }
}

# Paper class fields
paper.library_id
paper.scitex_id
paper.created_at
paper.created_by
paper.updated_at
paper.projects
paper.master_storage_path
paper.readable_name
paper.metadata_file
paper.pdf_downloaded_at
paper.pdf_size_bytes
```

## Conversion Functions

### Paper → BASE_STRUCTURE (for saving)
```python
def paper_to_base_structure(paper: Paper) -> OrderedDict:
    """Convert Paper to standardized BASE_STRUCTURE format."""
    structure = copy.deepcopy(BASE_STRUCTURE)

    # ID section
    structure["id"]["doi"] = paper.doi
    structure["id"]["scholar_id"] = paper.scholar_id
    # ... more mappings

    # Citation section
    structure["citation_count"]["total"] = paper.citation_count
    structure["citation_count"]["2025"] = paper.citation_2025
    # ... more years

    # URL section
    structure["url"]["doi"] = paper.url_doi
    structure["url"]["pdfs"] = paper.urls_pdf

    return structure
```

### BASE_STRUCTURE → Paper (for loading)
```python
def base_structure_to_paper(structure: OrderedDict) -> Paper:
    """Convert BASE_STRUCTURE format to Paper instance."""
    return Paper(
        # ID section
        doi=structure["id"]["doi"],
        scholar_id=structure["id"]["scholar_id"],

        # Citation section
        citation_count=structure["citation_count"]["total"],
        citation_2025=structure["citation_count"]["2025"],

        # URL section
        url_doi=structure["url"]["doi"],
        urls_pdf=structure["url"]["pdfs"],

        # Container section
        library_id=structure.get("_container", {}).get("library_id"),
        # ... more fields
    )
```

## Benefits

1. **Single Source of Truth**: BASE_STRUCTURE defines the canonical format
2. **Convenient Access**: Paper class provides Pythonic field access
3. **Type Safety**: Dataclass provides type hints and validation
4. **Backward Compatibility**: Old code using `paper.citation_count` still works
5. **Extensible**: Easy to add new fields to both structures

## Implementation Status

✅ **Completed**:
- Paper class updated to include all BASE_STRUCTURE fields
- Field naming follows consistent patterns (citation_YYYY, url_*, urls_*, paths_*)
- Container fields separated for clarity
- Backward compatibility maintained

⏳ **Pending**:
- Conversion functions in paper_utils
- Update all code using Paper to handle new fields
- Migration script for existing library data

## Related Files

- `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/core/Paper.py` - Paper dataclass (updated)
- `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/engines/utils/_standardize_metadata.py` - BASE_STRUCTURE definition
- `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/storage/_LibraryManager.py` - Conversion logic (updated)
- `/home/ywatanabe/proj/scitex_repo/src/scitex/scholar/utils/paper_utils.py` - Conversion utilities (to be updated)

## User Directive

> "keep single source of truth all the time"
> "so, standardize format and the Paper class should be tied closely to keep single source of truth"

This design achieves this by:
1. BASE_STRUCTURE is the authoritative definition
2. Paper class mirrors it with clear, consistent naming
3. Conversion functions maintain the mapping
4. Any changes to BASE_STRUCTURE should be reflected in Paper
