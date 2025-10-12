<!-- ---
!-- Timestamp: 2025-10-12 02:03:49
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex_repo/src/scitex/scholar/impact_factor/README.md
!-- --- -->

# Impact Factor Module

**Journal-level metrics for Scholar module - Optional, opt-in functionality**

## ⚠️ Important: Opt-In Module

This module provides **optional** impact factor functionality. The core Scholar module works completely without it.

**We provide**:
- ✅ Code/logic to use impact factor data
- ✅ Interfaces to query JCR databases
- ✅ Graceful fallbacks when unavailable

**We do NOT provide**:
- ❌ JCR data itself (users must obtain separately)

## Structure

```
impact_factor/
├── __init__.py                          # Our public API
├── JCRImpactFactorEngine.py             # Our code (query interface)
├── JournalMetrics.py                    # Our code (wrapper)
├── README.md                            # This file
└── externals/                           # External packages (opt-in)
    ├── impact_factor_calculator/        # Third-party package
    └── impact_factor_jcr/               # Third-party package
```

## Our Code (Always Included)

### JCRImpactFactorEngine.py
- Interface for querying JCR database
- **Does NOT include data** - users must provide JCR database
- Gracefully handles missing database (logs warning, continues)

### JournalMetrics.py
- Wrapper providing simple journal metrics API
- Falls back gracefully when dependencies unavailable

## External Packages (Opt-In, Separate Licenses)

### externals/impact_factor_jcr/
- **License**: Check `externals/impact_factor_jcr/LICENSE`
- **Installation**: `pip install -e ./impact_factor/externals/impact_factor_jcr`
- **Data Required**: Users must obtain JCR data separately
- **Optional**: Scholar works without this

### externals/impact_factor_calculator/
- **License**: Check `externals/impact_factor_calculator/LICENSE`
- **Installation**: `pip install -e ./impact_factor/externals/impact_factor_calculator`
- **Optional**: Scholar works without this

## Installation Options

### Option 1: Without Impact Factors (Default)
```bash
# No additional installation needed
# Scholar works fully, just skips impact factor enrichment
```

### Option 2: With Impact Factors (Opt-In)
```bash
# User must:
# 1. Review licenses in externals/ packages
# 2. Obtain JCR data (not provided by us)
# 3. Install external packages:

pip install -e ./impact_factor/externals/impact_factor_jcr
pip install -e ./impact_factor/externals/impact_factor_calculator

# 4. Configure JCR database path in Scholar config
```

## Usage

```python
from scitex.scholar import Scholar, Papers

# Works WITHOUT impact factors (default)
scholar = Scholar()
papers = scholar.load_bibtex("papers.bib")
enriched = scholar.enrich_papers(papers)  # Skips impact factors gracefully

# Works WITH impact factors (if installed and configured)
scholar = Scholar()
papers = scholar.load_bibtex("papers.bib")
enriched = scholar.enrich_papers(papers)  # Adds impact factors if available
```

## Licensing & Legal

### Our Code (MIT License - Same as SciTeX)
- `JCRImpactFactorEngine.py`
- `JournalMetrics.py`
- `__init__.py`

### External Packages (Separate Licenses)
- `externals/impact_factor_jcr/` - See package for license
- `externals/impact_factor_calculator/` - See package for license

### Data Requirements
- **JCR Database**: Users must obtain from Clarivate or authorized sources
- **We do NOT provide**: Any JCR data, only the code to use it
- **User responsibility**: Ensure proper licensing for any data used

## Why This Design?

1. **Legal clarity**: Our code separate from third-party code
2. **Opt-in**: Users consciously choose to use external packages
3. **No forced dependencies**: Core Scholar works without impact factors
4. **Data responsibility**: Users obtain and license data themselves
5. **Transparent**: Clear what's ours, what's external, what's missing

## For Publication

**Documentation must state**:
- Impact factor features are **optional**
- Requires user to obtain JCR data separately
- External packages have separate licenses
- Scholar provides the interface/logic, not the data

**Benefits**:
- No legal issues with data distribution
- No forced dependencies
- Users have full control and understanding
- Proper attribution to external packages

<!-- EOF -->