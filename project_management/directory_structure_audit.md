# SciTeX Directory Structure Audit

## Current Structure Analysis
Date: 2025-05-31

### Overview
The SciTeX repository follows a standard Python package structure with source code in `src/scitex/`, tests in `tests/`, and documentation in `docs/`.

### Root Directory Structure
```
scitex_repo/
├── src/scitex/          # Main source code
├── tests/             # Test files (mirrors src structure)
├── docs/              # Documentation (Sphinx + custom)
├── examples/          # Example scripts and workflows
├── project_management/# Project planning and tracking
├── pyproject.toml     # Modern Python packaging
├── pytest.ini         # Test configuration
├── requirements.txt   # Dependencies
└── README.md          # Project overview
```

### Source Code Organization (`src/scitex/`)

#### Core Modules (26 total)
1. **ai/** - AI/ML utilities, GenAI providers
2. **context/** - Context managers
3. **db/** - Database operations (PostgreSQL, SQLite3)
4. **decorators/** - Function decorators
5. **dev/** - Development utilities
6. **dict/** - Dictionary utilities
7. **dsp/** - Digital signal processing
8. **dt/** - Date/time utilities
9. **gen/** - General utilities, workflow management
10. **gists/** - Code snippets
11. **io/** - File I/O operations
12. **life/** - Life utilities (e.g., rain monitoring)
13. **linalg/** - Linear algebra
14. **nn/** - Neural network layers
15. **os/** - OS utilities
16. **parallel/** - Parallel processing
17. **path/** - Path manipulation
18. **pd/** - Pandas utilities
19. **plt/** - Plotting enhancements
20. **reproduce/** - Reproducibility tools
21. **resource/** - System resource monitoring
22. **stats/** - Statistical analysis
23. **str/** - String utilities
24. **tex/** - LaTeX utilities
25. **torch/** - PyTorch utilities
26. **types/** - Type definitions
27. **utils/** - General utilities
28. **web/** - Web scraping, API access

### Issues Identified

#### 1. File Naming Issues
- **Versioning suffixes**: `_save_v01.py_` (should be removed)
- **Temporary files**: `.#_FreqDropout.py` (editor backup)
- **Inconsistent prefixes**: Mix of `_` prefix for private modules

#### 2. Module Organization Issues
- **Overlapping functionality**:
  - `utils/` and `gen/` have similar purposes
  - `dev/` could be merged with development tools
- **Large modules**:
  - `ai/` has 40 files (needs submodule organization)
  - `plt/` has 31 files
  - `dsp/` has 25 files
  - `db/` has 20 files

#### 3. Duplicate/Redundant Code
- **Multiple UMAP implementations** in `ai/clustering/`:
  - `_umap.py`
  - `_umap_dev.py`
  - `_umap_working.py`
  - `_UMAP.py`
- **Vendored code**: `ai/optim/Ranger_Deep_Learning_Optimizer/`

#### 4. Empty/Placeholder Directories
- `etc/` - Only contains `wait_key.py`
- `ml` - Empty symlink/directory
- `life/` - Only contains rain monitoring

#### 5. Submodule Organization
Good examples:
- `io/_load_modules/` - Well-organized format handlers
- `plt/_subplots/` - Clear wrapper hierarchy
- `db/_*Mixins/` - Good separation of concerns

Needs improvement:
- `ai/` - Mixed concerns (genai, clustering, metrics, etc.)
- `stats/` - Could benefit from clearer submodule structure

### Recommendations

#### Immediate Actions
1. **Remove temporary/backup files**:
   - `.#_FreqDropout.py`
   - `_save_v01.py_`

2. **Consolidate UMAP implementations**:
   - Keep best implementation
   - Remove `_dev` and `_working` versions

3. **Extract vendored code**:
   - Move Ranger optimizer to external dependency

#### Short-term Improvements
1. **Reorganize large modules**:
   ```
   ai/
   ├── genai/        # GenAI providers
   ├── clustering/   # Clustering algorithms
   ├── metrics/      # ML metrics
   ├── training/     # Training utilities
   └── sklearn/      # Scikit-learn wrappers
   ```

2. **Merge similar modules**:
   - Consider merging `utils/` functionality into `gen/`
   - Move `dev/` tools to a development submodule

3. **Standardize file naming**:
   - Remove version suffixes
   - Use consistent `_` prefix for private modules

#### Long-term Structure
Consider adopting a more domain-focused structure:
```
scitex/
├── core/          # Core utilities (dict, str, path, etc.)
├── data/          # Data processing (pd, io, db)
├── scientific/    # Scientific computing (dsp, stats, linalg)
├── ml/            # Machine learning (ai, nn, torch)
├── visualization/ # Plotting and visualization (plt, tex)
├── system/        # System utilities (resource, parallel, os)
└── workflow/      # Workflow management (gen, reproduce)
```

### Test Structure
The test structure properly mirrors the source structure, which is good practice. No changes needed here.

### Documentation Structure
Well-organized with:
- Sphinx documentation
- API references
- Module guidelines
- Examples

### Metrics
- **Total Python files**: ~200+
- **Total modules**: 26
- **Average files per module**: 7.7
- **Largest module**: ai (40 files)
- **Smallest modules**: Several with 1-2 files