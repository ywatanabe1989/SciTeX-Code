# Pipeline Organization - Single Source of Truth

## Current State Analysis

### Location 1: `core/*Pipeline*.py` (Older, High-Level)
```
core/
├── ScholarPipelineSingle.py      - Process single paper (DOI → metadata → URLs → PDF)
├── ScholarPipelineParallel.py    - Process multiple papers in parallel
└── ScholarPipelineBibTeX.py      - Process BibTeX file → Papers with PDFs
```

**Characteristics:**
- High-level, user-facing workflows
- Complete end-to-end operations
- Direct CLI entry points
- Import each other (ScholarPipelineParallel uses ScholarPipelineSingle)

### Location 2: `pipelines/*.py` (Newer, Modular)
```
pipelines/
├── base.py                        - BasePipeline (abstract, shared services)
├── paper_processing.py            - PaperProcessingPipeline (single paper)
├── batch_processing.py            - BatchProcessingPipeline (multiple papers)
└── enrichment.py                  - EnrichmentPipeline (metadata enrichment)
```

**Characteristics:**
- Modular architecture with BasePipeline
- Lazy service initialization
- Used by Scholar class internally
- More flexible, composable

### Location 3: `cli/` (Command Line Interface)
```
cli/
├── _CentralArgumentParser.py     - Unified argument parsing
├── _argument_groups.py            - Argument definitions
├── handlers/
│   ├── bibtex_handler.py         - BibTeX operations
│   ├── doi_handler.py            - DOI operations
│   └── project_handler.py        - Project operations
└── download_pdf.py               - Direct PDF download CLI
```

### Location 4: `__main__.py` (Entry Point)
- Routes to appropriate CLI handlers
- Minimal logic, delegates to handlers

## Problem: Duplication and Confusion

### Overlapping Functionality:

1. **Single Paper Processing**:
   - `core/ScholarPipelineSingle.py`
   - `pipelines/paper_processing.py`

2. **Batch/Parallel Processing**:
   - `core/ScholarPipelineParallel.py`
   - `pipelines/batch_processing.py`

3. **BibTeX Processing**:
   - `core/ScholarPipelineBibTeX.py`
   - `cli/handlers/bibtex_handler.py`

4. **Entry Points**:
   - `core/ScholarPipelineBibTeX.py` (can run with `python -m ...`)
   - `cli/download_pdf.py` (standalone CLI)
   - `__main__.py` (main entry point)

## Proposed Organization: Single Source of Truth

### Tier 1: Core Implementations (pipelines/)
**Location:** `src/scitex/scholar/pipelines/`
**Purpose:** Implementation details, composable components

```python
pipelines/
├── __init__.py                    - Export public pipelines
├── base.py                        - BasePipeline (shared services)
├── single_paper.py                - Process one paper (DOI → PDF)
├── batch_papers.py                - Process multiple papers in parallel
├── bibtex_import.py               - Import from BibTeX file
└── enrichment.py                  - Metadata enrichment
```

**Rules:**
- Implementation only, no CLI logic
- Import each other freely
- Return structured results
- Used by Scholar class

### Tier 2: User-Facing API (core/)
**Location:** `src/scitex/scholar/core/`
**Purpose:** High-level API for common workflows

```python
core/
├── Scholar.py                     - Main API (facade over pipelines)
├── Paper.py                       - Paper data model
└── Papers.py                      - Paper collection
```

**Rules:**
- No pipeline implementations
- Delegates to pipelines/
- Provides simple, intuitive API
- Handles common use cases

### Tier 3: CLI (cli/ and __main__.py)
**Location:** `src/scitex/scholar/cli/`
**Purpose:** Command line interface

```python
cli/
├── __init__.py
├── _CentralArgumentParser.py     - Argument parsing
├── _argument_groups.py            - Argument definitions
└── handlers/
    ├── bibtex.py                 - BibTeX operations
    ├── doi.py                    - DOI operations
    ├── project.py                - Project operations
    └── download.py               - PDF download operations
```

**__main__.py:**
- Minimal routing logic
- Delegates to cli/handlers
- No business logic

**Rules:**
- CLI logic only
- Uses Scholar API (not pipelines directly)
- Argument parsing and validation
- User interaction

## Migration Plan

### Phase 1: Consolidate Core Pipelines → pipelines/

1. **Merge `ScholarPipelineSingle` → `pipelines/single_paper.py`**
   - Rename for clarity
   - Remove CLI-specific code
   - Focus on workflow logic

2. **Merge `ScholarPipelineParallel` → `pipelines/batch_papers.py`**
   - Consolidate with `BatchProcessingPipeline`
   - Keep parallel execution logic

3. **Merge `ScholarPipelineBibTeX` → `pipelines/bibtex_import.py`**
   - Focus on BibTeX → Papers conversion
   - Keep parallel processing

### Phase 2: Simplify Scholar Class

```python
class Scholar:
    """High-level API for Scholar operations"""

    def __init__(self, project=None):
        self.config = ScholarConfig(project=project)
        self.pipelines = {
            'single': SinglePaperPipeline(config),
            'batch': BatchPapersPipeline(config),
            'bibtex': BibTeXImportPipeline(config),
            'enrichment': EnrichmentPipeline(config),
        }

    def process_paper(self, doi):
        return self.pipelines['single'].run(doi=doi)

    def process_bibtex(self, bibtex_path):
        return self.pipelines['bibtex'].run(bibtex_path=bibtex_path)
```

### Phase 3: Unify CLI

1. **Remove standalone CLIs** (ScholarPipelineBibTeX.__main__, download_pdf.py)
2. **Consolidate in __main__.py + handlers/**
3. **Single entry point:** `python -m scitex.scholar`

## Final Structure

```
scitex/scholar/
├── __main__.py                    # Entry point (routing only)
├── __init__.py                    # Public API exports
│
├── core/                          # Public API
│   ├── Scholar.py                # Facade over pipelines
│   ├── Paper.py                  # Data model
│   └── Papers.py                 # Collection
│
├── pipelines/                     # Implementation
│   ├── __init__.py
│   ├── base.py                   # BasePipeline
│   ├── single_paper.py           # Process one paper
│   ├── batch_papers.py           # Process multiple papers
│   ├── bibtex_import.py          # Import from BibTeX
│   └── enrichment.py             # Metadata enrichment
│
├── cli/                           # CLI layer
│   ├── _CentralArgumentParser.py
│   ├── _argument_groups.py
│   └── handlers/
│       ├── bibtex.py
│       ├── doi.py
│       ├── project.py
│       └── download.py
│
├── storage/                       # Data persistence
├── metadata_engines/              # Metadata sources
├── auth/                          # Authentication
└── browser/                       # Browser automation
```

## Migration Priority

### High Priority (Do Now):
- [ ] Create `pipelines/bibtex_import.py` consolidating BibTeX workflows
- [ ] Update `Scholar.py` to use new pipeline structure
- [ ] Document pipeline responsibilities clearly

### Medium Priority (Do Soon):
- [ ] Consolidate single/parallel paper pipelines
- [ ] Unify CLI entry points
- [ ] Remove duplicate implementations

### Low Priority (Do Later):
- [ ] Deprecate old `core/ScholarPipeline*.py` files
- [ ] Migration guide for existing users
- [ ] Update all examples and documentation

## Benefits

1. **Single Source of Truth**: Clear hierarchy (pipelines → API → CLI)
2. **No Duplication**: One implementation per workflow
3. **Maintainability**: Easy to find and update code
4. **Extensibility**: Add new pipelines without touching existing code
5. **Testing**: Test pipelines independently of CLI
6. **Documentation**: Clear separation of concerns

## Decision

**Recommended approach:** Keep both temporarily during transition:
1. Move new code to `pipelines/`
2. Keep `core/ScholarPipeline*` for backward compatibility
3. Gradually migrate callers
4. Deprecate old pipelines when no longer used

This avoids breaking existing code while establishing the new architecture.
