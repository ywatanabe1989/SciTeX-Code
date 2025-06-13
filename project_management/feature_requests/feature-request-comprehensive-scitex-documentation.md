<!-- ---
!-- Timestamp: 2025-05-30 01:20:00
!-- Author: Claude
!-- File: ./project_management/feature_requests/feature-request-comprehensive-scitex-documentation.md
!-- --- -->

# Feature Request: Comprehensive SciTeX Documentation and Guidelines

## Summary
Create comprehensive documentation and guidelines for the scitex package that enables other agents and developers to effectively use the framework. This includes module guides, API reference, and searchable Sphinx documentation.

## Motivation
- Current documentation is scattered across guideline files
- No centralized API reference for functions and classes
- Other agents need standardized way to search and understand scitex
- New users struggle to understand the framework's benefits and usage

## Proposed Solution

### 1. **Agent-Friendly Guidelines** (`docs/agent_guidelines/`)
```
docs/agent_guidelines/
├── 00_why_use_scitex.md          # Benefits and use cases
├── 01_quick_start.md            # 5-minute introduction
├── 02_core_concepts.md          # Key concepts and philosophy
├── 03_module_overview.md        # High-level module descriptions
└── 04_common_workflows.md       # Typical usage patterns
```

### 2. **Module Documentation** (`docs/modules/`)
```
docs/modules/
├── io/
│   ├── README.md               # Module overview
│   ├── load.md                 # Detailed load() usage
│   ├── save.md                 # Detailed save() usage
│   └── examples/               # Code examples
├── gen/
│   ├── README.md
│   ├── start.md                # Environment setup
│   └── examples/
├── plt/
│   ├── README.md
│   ├── subplots.md             # Enhanced plotting
│   └── examples/
└── [other modules...]
```

### 3. **Sphinx Documentation**
```python
# docs/conf.py
project = 'scitex'
extensions = [
    'sphinx.ext.autodoc',        # Auto-generate from docstrings
    'sphinx.ext.napoleon',       # Support NumPy docstrings
    'sphinx.ext.viewcode',       # Add source links
    'sphinx.ext.intersphinx',    # Link to other docs
    'sphinx_search.extension',   # Enhanced search
]
```

### 4. **API Reference Structure**
```
API Reference/
├── Core Modules
│   ├── scitex.io
│   ├── scitex.gen
│   └── scitex.plt
├── Data Processing
│   ├── scitex.dsp
│   ├── scitex.pd
│   └── scitex.stats
├── Machine Learning
│   ├── scitex.ai
│   ├── scitex.nn
│   └── scitex.torch
└── Utilities
    ├── scitex.path
    ├── scitex.str
    └── scitex.decorators
```

### 5. **Content for Each Function/Class**
```markdown
## scitex.io.load

### Synopsis
```python
scitex.io.load(lpath: str, show: bool = False, verbose: bool = False, **kwargs) -> Any
```

### Description
Universal file loader that automatically detects format from extension.

### Parameters
- **lpath** (str): Path to file to load
- **show** (bool): Display info during loading
- **verbose** (bool): Print detailed output
- **kwargs**: Format-specific options

### Returns
- Loaded object (type depends on file format)

### Supported Formats
- Data: .csv, .json, .yaml, .xlsx
- Scientific: .npy, .mat, .hdf5
- ML Models: .pth, .pkl, .joblib
- Documents: .txt, .md, .pdf

### Examples
```python
# Load CSV data
df = scitex.io.load("./data.csv")

# Load with options
model = scitex.io.load("./model.pth", map_location="cpu")
```

### See Also
- scitex.io.save
- scitex.io.load_configs
```

## Implementation Plan

### Phase 1: Structure Setup
1. Create documentation directory structure
2. Set up Sphinx configuration
3. Create templates for each doc type

### Phase 2: Core Module Docs
1. Document io module (load, save, etc.)
2. Document gen module (start, close, etc.)
3. Document plt module (subplots, etc.)

### Phase 3: Extended Modules
1. Document data processing modules
2. Document ML/AI modules
3. Document utility modules

### Phase 4: Integration
1. Generate Sphinx HTML docs
2. Set up search functionality
3. Create agent-friendly index
4. Add to CI/CD pipeline

### Phase 5: Examples & Tutorials
1. Create jupyter notebook tutorials
2. Add real-world examples
3. Create video tutorials (optional)

## Benefits
1. **For Agents**: Standardized, searchable documentation
2. **For Developers**: Clear API reference and examples
3. **For Project**: Professional documentation increases adoption
4. **For Maintenance**: Auto-generated docs reduce manual work

## Progress Tracking
- [x] Phase 1: Structure Setup (100%) - Sphinx configured, directories created
- [x] Phase 2: Core Module Docs (100%) - gen, io modules documented
- [x] Phase 3: Extended Modules (80%) - ai, nn, dsp, pd, stats, plt documented
- [ ] Phase 4: Integration (20%) - Need to build HTML docs and deploy
- [ ] Phase 5: Examples & Tutorials (50%) - Examples exist but need tutorials

## Completed Documentation
- ✅ Agent guidelines (00_why_use_scitex.md through 04_common_workflows.md)
- ✅ IMPORTANT-SciTeX-20-gen-module-detailed.md
- ✅ IMPORTANT-SciTeX-21-io-module-detailed.md
- ✅ IMPORTANT-SciTeX-22-ai-module-detailed.md
- ✅ IMPORTANT-SciTeX-23-nn-module-detailed.md
- ✅ Module READMEs for all major modules
- ✅ SciTeX_COMPLETE_REFERENCE.md

## Dependencies
- Sphinx and extensions installation
- Documentation hosting solution (GitHub Pages?)
- Time investment for writing initial docs

## Alternative Approaches Considered
1. **MkDocs**: Simpler but less powerful than Sphinx
2. **Docusaurus**: Good for tutorials but not API docs
3. **Manual Markdown**: Current approach, not scalable

## Decision
Proceed with Sphinx for its:
- Auto-generation from docstrings
- Powerful search capabilities
- Industry standard for Python projects
- Agent-friendly structured output

<!-- EOF -->