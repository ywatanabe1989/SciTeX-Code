# Typed Metadata System

## Overview

The typed metadata system provides **type-safe** data structures for Scholar paper metadata, replacing the previous dict/DotDict approach with strongly-typed dataclasses.

## Benefits

### 1. Type Safety
```python
# ❌ Old way - no type checking
paper = {"basic": {"year": "2024"}}  # Wrong type, but no error

# ✅ New way - type checked
paper = Paper()
paper.metadata.basic.year = "2024"  # Type checker catches this error
paper.metadata.basic.year = 2024    # ✓ Correct
```

### 2. IDE Autocomplete
```python
# With typed metadata, your IDE shows:
paper.metadata.  # -> Autocomplete: id, basic, citation_count, publication, url, path, system
paper.metadata.basic.  # -> Autocomplete: title, authors, year, abstract, keywords, type
```

### 3. Clear Structure Documentation
The dataclass definitions serve as **living documentation** of the metadata structure.

### 4. Source Tracking with Lists
All `_engines` fields are now **lists** to support multiple sources:
```python
paper.metadata.basic.title_engines = ["input", "CrossRef", "OpenAlex"]
```

## Structure

```
Paper
├── metadata: PaperMetadataStructure
│   ├── id: IDMetadata
│   │   ├── doi: Optional[str]
│   │   ├── doi_engines: List[str]
│   │   ├── arxiv_id: Optional[str]
│   │   ├── arxiv_id_engines: List[str]
│   │   └── ...
│   ├── basic: BasicMetadata
│   │   ├── title: Optional[str]
│   │   ├── title_engines: List[str]
│   │   ├── authors: Optional[List[str]]
│   │   ├── authors_engines: List[str]
│   │   └── ...
│   ├── citation_count: CitationCountMetadata
│   ├── publication: PublicationMetadata
│   ├── url: URLMetadata
│   ├── path: PathMetadata
│   └── system: SystemMetadata
└── container: ContainerMetadata
    ├── scitex_id: Optional[str]
    ├── library_id: Optional[str]
    ├── created_at: Optional[str]
    └── ...
```

## Usage

### Creating New Metadata

```python
from scitex.scholar.core.metadata_types import Paper

# Create empty paper
paper = Paper()

# Set fields with type safety
paper.metadata.id.doi = "10.1234/example.2024"
paper.metadata.id.doi_engines.append("input")

paper.metadata.basic.title = "Example Paper"
paper.metadata.basic.title_engines.append("input")

paper.metadata.basic.authors = ["John Doe", "Jane Smith"]
paper.metadata.basic.authors_engines.append("input")
```

### Loading from Dictionary/JSON

```python
from scitex.scholar.core.metadata_converters import dict_to_typed_metadata

# Load from dict
json_data = {
    "metadata": {
        "id": {"doi": "10.1234/example", "doi_engines": ["input"]},
        "basic": {"title": "Example", "title_engines": ["input"]}
    },
    "container": {"scitex_id": "ABC123"}
}

paper = dict_to_typed_metadata(json_data)
```

### Converting to Dictionary/JSON

```python
from scitex.scholar.core.metadata_converters import typed_to_dict_metadata

paper_dict = typed_to_dict_metadata(paper)
# Can now save to JSON
import json
with open('metadata.json', 'w') as f:
    json.dump(paper_dict, f, indent=2)
```

### Adding Sources

```python
from scitex.scholar.core.metadata_converters import add_source_to_engines

metadata_dict = {"metadata": {...}}

# Add CrossRef as source for title
add_source_to_engines(metadata_dict["metadata"], "basic.title", "CrossRef")
```

### Merging from Multiple Sources

```python
from scitex.scholar.core.metadata_converters import merge_metadata_sources

existing = {"metadata": {"basic": {"title": "Old", "title_engines": ["input"]}}}
new = {"metadata": {"basic": {"title": "New Title"}}}

# Merge and track source
merge_metadata_sources(
    existing["metadata"],
    new["metadata"],
    "basic",
    "title",
    "CrossRef"
)
# Result: {"basic": {"title": "New Title", "title_engines": ["input", "CrossRef"]}}
```

### Normalizing Engines

```python
from scitex.scholar.core.metadata_converters import validate_and_normalize_engines

# Fix inconsistent _engines formats
messy = {
    "metadata": {
        "id": {"doi": "...", "doi_engines": "input"},  # String
        "basic": {"title": "...", "title_engines": None}  # None
    }
}

normalized = validate_and_normalize_engines(messy)
# Result: All _engines are now lists: ["input"] and []
```

## Migration Guide

### Current System (Dict/DotDict)
```python
# Old approach
paper = {
    "doi": "10.1234/example",
    "doi_source": "input",
    "title": "Example",
    "title_source": "input"
}
```

### New Typed System
```python
# New approach
paper = Paper()
paper.metadata.id.doi = "10.1234/example"
paper.metadata.id.doi_engines = ["input"]
paper.metadata.basic.title = "Example"
paper.metadata.basic.title_engines = ["input"]
```

### Backward Compatibility

The system supports both formats through converters:

```python
# Load old format
old_format_dict = {...}
normalized = validate_and_normalize_engines(old_format_dict)
paper = dict_to_typed_metadata(normalized)

# Save in old format if needed
paper_dict = typed_to_dict_metadata(paper)
```

## Source Tracking

### Why Lists for `_engines`?

Fields can be confirmed by multiple sources:

```python
# Title confirmed by multiple sources
paper.metadata.basic.title = "Example Paper"
paper.metadata.basic.title_engines = ["input", "CrossRef", "OpenAlex", "Semantic Scholar"]

# This shows the title has been verified by 4 independent sources
```

### Standard Source Identifiers

- `"input"`: From user input (BibTeX, manual entry)
- `"CrossRef"`: From CrossRef API
- `"CrossRefLocal"`: From local CrossRef database
- `"OpenAlex"`: From OpenAlex API
- `"Semantic_Scholar"`: From Semantic Scholar API
- `"PubMed"`: From PubMed API
- `"arXiv"`: From arXiv API
- `"ScholarURLFinder"`: From URL discovery
- `"OpenURLResolver"`: From OpenURL resolution

## Examples

See `examples_typed_metadata.py` for complete working examples:

1. Creating typed metadata from scratch
2. Loading from dictionary/JSON
3. Normalizing _engines fields
4. Adding sources
5. Merging from multiple sources
6. Type safety demonstration

Run examples:
```bash
cd /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/core
python examples_typed_metadata.py
```

## Files

- `metadata_types.py`: Dataclass definitions for all metadata structures
- `metadata_converters.py`: Conversion utilities and helper functions
- `examples_typed_metadata.py`: Complete usage examples
- `README_TYPED_METADATA.md`: This documentation

## Future Improvements

1. **Validation**: Add field validation (e.g., DOI format, year range)
2. **Pydantic Integration**: Consider using Pydantic for advanced validation
3. **Schema Versioning**: Support multiple metadata schema versions
4. **Auto-migration**: Automatically upgrade old metadata to new format

## FAQ

**Q: Do I need to use typed metadata everywhere?**
A: No, the system maintains backward compatibility. You can gradually migrate.

**Q: What if I have custom fields?**
A: Use `additional_files` lists or extend the dataclasses for custom needs.

**Q: How do I handle nested citation counts by year?**
A: Use the `CitationCountMetadata` class with `y2024`, `y2023`, etc. fields.

**Q: Can I use this with JSON/MongoDB/etc?**
A: Yes, use `to_dict()` to convert to JSON-serializable dictionaries.

---

**Author**: Claude (AI Assistant)
**Date**: 2025-10-06
**Version**: 1.0.0
