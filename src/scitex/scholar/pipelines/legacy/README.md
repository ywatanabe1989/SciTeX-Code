# Scholar Pipelines - Single Source of Truth

## Overview

The `pipelines/` directory contains the **primary, centralized pipeline implementations** for all Scholar workflows. These follow SciTeX naming conventions and architectural patterns.

## Structure

```
pipelines/
├── _BasePipeline.py           → class BasePipeline (internal base)
├── PaperProcessingPipeline.py → class PaperProcessingPipeline
├── BatchProcessingPipeline.py → class BatchProcessingPipeline
├── EnrichmentPipeline.py      → class EnrichmentPipeline
└── BibTeXImportPipeline.py    → class BibTeXImportPipeline
```

## Naming Convention Rules

✅ **Correct:** Filename = ClassName
- `PaperProcessingPipeline.py` contains `class PaperProcessingPipeline`
- `_BasePipeline.py` contains `class BasePipeline` (internal, underscore prefix)

❌ **Wrong:** snake_case filenames
- `paper_processing.py` (old style, now fixed)
- `batch_processing.py` (old style, now fixed)

## Pipeline Descriptions

### 1. _BasePipeline (Internal)

**File:** `_BasePipeline.py`
**Purpose:** Abstract base class for all pipelines

**Provides:**
- Configuration management
- Lazy service initialization (auth, browser, library, metadata engine)
- Abstract `run()` method

**Not used directly** - only inherited by other pipelines.

### 2. PaperProcessingPipeline

**File:** `PaperProcessingPipeline.py`
**Purpose:** Process a single paper through complete workflow

**Workflow:**
1. Resolve DOI from title (if needed)
2. Load/create Paper from storage
3. Find PDF URLs
4. Download PDF
5. Update project symlinks

**Used by:** `Scholar.process_paper_async()`, `BatchProcessingPipeline`

### 3. BatchProcessingPipeline

**File:** `BatchProcessingPipeline.py`
**Purpose:** Process multiple papers with controlled parallelism

**Workflow:**
- Processes N papers concurrently (configurable)
- Each paper goes through `PaperProcessingPipeline`
- Semaphore controls concurrent access

**Used by:** `Scholar.process_papers_async()`, `BibTeXImportPipeline`

### 4. EnrichmentPipeline

**File:** `EnrichmentPipeline.py`
**Purpose:** Enrich papers with metadata from external sources

**Enriches:**
- DOI, PMID, ArXiv ID
- Title, authors, abstract, keywords
- Journal, publisher, volume, issue, pages
- Citation counts
- Journal impact factors (optional)

**Used by:** `Scholar.enrich_papers_async()`

### 5. BibTeXImportPipeline

**File:** `BibTeXImportPipeline.py`
**Purpose:** Import and process papers from BibTeX files

**Workflow:**
1. Parse BibTeX file → Papers collection
2. Process papers in parallel (via `BatchProcessingPipeline`)
3. Save enriched BibTeX with results
4. Update project bibliography structure (`info/bibliography/`)

**Used by:** CLI, direct invocation

## Usage Examples

### Direct Pipeline Usage (Advanced)

```python
from scitex.scholar.pipelines import PaperProcessingPipeline

pipeline = PaperProcessingPipeline()
paper = await pipeline.run(doi="10.1038/s41598-017-02626-y")
```

### Via Scholar API (Recommended)

```python
from scitex.scholar.core import Scholar

scholar = Scholar(project="my_project")
paper = await scholar.process_paper_async(doi="10.1038/...")
```

### BibTeX Import

```python
from scitex.scholar.pipelines import BibTeXImportPipeline

pipeline = BibTeXImportPipeline(num_workers=8)
papers = await pipeline.run(
    bibtex_path="papers.bib",
    project="my_project"
)
```

## Architecture

```
User Code
    ↓
Scholar API (core/Scholar.py)
    ↓
Pipelines (pipelines/*.py) ← PRIMARY IMPLEMENTATIONS
    ↓
Services (storage/, auth/, browser/, metadata_engines/)
```

## Migration Status

### ✅ Current Primary Pipelines (Use These)
- `pipelines/_BasePipeline.py`
- `pipelines/PaperProcessingPipeline.py`
- `pipelines/BatchProcessingPipeline.py`
- `pipelines/EnrichmentPipeline.py`
- `pipelines/BibTeXImportPipeline.py`

### ⚠️ Legacy Pipelines (Deprecated, Backward Compatibility Only)
- `core/ScholarPipelineSingle.py` (use `PaperProcessingPipeline` instead)
- `core/ScholarPipelineParallel.py` (use `BatchProcessingPipeline` instead)
- `core/ScholarPipelineBibTeX.py` (use `BibTeXImportPipeline` instead)

**Note:** Legacy pipelines in `core/` are kept for backward compatibility but should not be used for new development.

## Design Principles

1. **Single Responsibility**: Each pipeline does one thing well
2. **Composition**: Pipelines can use other pipelines
3. **Storage-First**: Check storage before each operation
4. **Lazy Loading**: Services initialized only when needed
5. **Async by Default**: All pipelines are async for performance
6. **Configuration**: All pipelines accept ScholarConfig

## When to Use Which Pipeline

| Task | Pipeline | Method |
|------|----------|--------|
| Process one paper | `PaperProcessingPipeline` | `run(doi=...)` |
| Process many papers | `BatchProcessingPipeline` | `run(papers=...)` |
| Enrich metadata | `EnrichmentPipeline` | `run(papers=...)` |
| Import from BibTeX | `BibTeXImportPipeline` | `run(bibtex_path=...)` |

## See Also

- [Pipeline Organization Documentation](../docs/PIPELINE_ORGANIZATION.md)
- [Scholar API Documentation](../core/README.md)
- [Storage Documentation](../storage/README.md)
