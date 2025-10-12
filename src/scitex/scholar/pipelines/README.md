# Scholar Pipelines - Single Source of Truth

## Overview

This directory contains the **primary, battle-tested pipeline implementations** for all Scholar workflows. These were moved from `core/` as they are the canonical implementations.

## Structure

```
pipelines/
├── ScholarPipelineSingle.py    → Single paper workflow (complete, mature)
├── ScholarPipelineParallel.py  → Multiple papers in parallel (complete, mature)
├── ScholarPipelineBibTeX.py    → BibTeX import (complete, mature)
└── legacy/                     → Previous modular attempts (archived)
```

## Primary Pipelines

### 1. ScholarPipelineSingle

**File:** `ScholarPipelineSingle.py`
**Purpose:** Complete workflow for processing a single paper

**Workflow:**
1. Resolve DOI (if needed)
2. Fetch metadata
3. Find PDF URLs
4. Download PDF
5. Create library structure
6. Update project symlinks

**Runnable:** Yes
```bash
python -m scitex.scholar.pipelines.ScholarPipelineSingle \
    --doi 10.1038/s41598-017-02626-y \
    --project my_project
```

### 2. ScholarPipelineParallel

**File:** `ScholarPipelineParallel.py`
**Purpose:** Process multiple papers with controlled parallelism

**Features:**
- Parallel worker management
- Browser session pooling
- Storage-first approach (resumes from existing state)
- Detailed progress logging

**Runnable:** Yes
```bash
python -m scitex.scholar.pipelines.ScholarPipelineParallel \
    --num-workers 8 \
    --project my_project
```

### 3. ScholarPipelineBibTeX

**File:** `ScholarPipelineBibTeX.py`
**Purpose:** Import and process papers from BibTeX files

**Workflow:**
1. Parse BibTeX file
2. Process papers in parallel
3. Save enriched BibTeX
4. Update project bibliography structure

**Runnable:** Yes
```bash
python -m scitex.scholar.pipelines.ScholarPipelineBibTeX \
    --bibtex papers.bib \
    --project my_project \
    --num-workers 8 \
    --browser-mode stealth
```

## Why These Are Primary

✅ **Battle-tested** - Used in production, proven reliable
✅ **Complete** - Full feature set, not minimal implementations
✅ **Integrated** - Work with all Scholar services
✅ **Runnable** - Can be used standalone via CLI
✅ **Documented** - Extensive inline documentation and examples

## Usage Patterns

### Pattern 1: Direct Pipeline Usage (Advanced)

```python
from scitex.scholar.pipelines import ScholarPipelineSingle

pipeline = ScholarPipelineSingle()
paper = await pipeline.process_paper_async(
    doi="10.1038/s41598-017-02626-y",
    project="my_project"
)
```

### Pattern 2: BibTeX Import (Common)

```python
from scitex.scholar.pipelines import ScholarPipelineBibTeX

pipeline = ScholarPipelineBibTeX(
    num_workers=8,
    browser_mode="stealth"
)

papers = await pipeline.process_bibtex_file_async(
    bibtex_path="./data/papers.bib",
    project="my_project"
)
```

### Pattern 3: Via Scholar API (Recommended)

```python
from scitex.scholar.core import Scholar

scholar = Scholar(project="my_project")

# Single paper
paper = await scholar.process_paper_async(doi="10.1038/...")

# BibTeX file
papers = await scholar.process_bibtex_async("papers.bib")
```

## Standalone CLI Usage

All pipelines can run standalone:

```bash
# Single paper
python -m scitex.scholar.pipelines.ScholarPipelineSingle \
    --doi 10.1038/s41598-017-02626-y \
    --project neurovista

# BibTeX import (most common)
python -m scitex.scholar.pipelines.ScholarPipelineBibTeX \
    --bibtex ./data/scholar/bib_files/neurovista.bib \
    --project neurovista \
    --num-workers 8 \
    --chrome-profile system \
    --browser-mode stealth
```

## Legacy

The `legacy/` directory contains previous modular pipeline attempts. These were replaced with the proven implementations from `core/`:

- ❌ `legacy/ScholarPipelinePaper.py` - Superseded by ScholarPipelineSingle
- ❌ `legacy/ScholarPipelinePapers.py` - Superseded by ScholarPipelineParallel
- ❌ `legacy/_ScholarPipelineBase.py` - Not needed in battle-tested versions

**Do not use legacy pipelines** - they are kept for reference only.

## Integration

These pipelines integrate with:
- **Storage**: `LibraryManager`, `BibTeXHandler`
- **Auth**: `ScholarAuthManager`
- **Browser**: `ScholarBrowserManager`
- **Metadata**: `ScholarEngine`
- **Downloads**: `ScholarPDFDownloader`

## See Also

- [Pipeline Architecture](./ARCHITECTURE.md)
- [Scholar API Documentation](../core/README.md)
- [Storage Documentation](../storage/README.md)
- [Examples](../examples/)
