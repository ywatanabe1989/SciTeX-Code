# Release Notes: SciTeX v2.0.0

## 🎉 Major Breaking Change: Rebranding from MNGS to SciTeX

### What's New
- **Package renamed**: `mngs` → `scitex`
- **Project name**: `MNGS` → `SciTeX` 
- **Better reflects purpose**: **Sci**entific **Tex**t and data processing framework

### Migration Guide

#### For New Users
```bash
pip install scitex
```

```python
import scitex
from scitex.io import save
from scitex.plt import subplots
```

#### For Existing Users
1. **Update imports**:
   ```python
   # Old
   import mngs
   
   # New
   import scitex
   ```

2. **Update environment variables**:
   ```bash
   # Old
   export MNGS_SCHOLAR_DIR=~/.mngs/scholar
   
   # New  
   export SCITEX_SCHOLAR_DIR=~/.scitex/scholar
   ```

### Backward Compatibility
- A redirect package `mngs>=2.0.0` is available that:
  - Shows deprecation warnings
  - Automatically installs and imports scitex
  - Allows existing code to continue working temporarily

### Features from v1.12.0
- **Scholar Module**: Academic paper search and management
- **Save Module Fixes**: Resolved import issues
- All previous mngs functionality is preserved in scitex

### Breaking Changes
- Package name changed from `mngs` to `scitex`
- All imports must be updated
- Environment variables changed from `MNGS_*` to `SCITEX_*`

### Installation
```bash
# Remove old package
pip uninstall mngs

# Install new package
pip install scitex
```

### Repository
- GitHub: https://github.com/ywatanabe1989/SciTeX-Code
- PyPI: https://pypi.org/project/scitex/

---
For questions or issues, please visit the GitHub repository.