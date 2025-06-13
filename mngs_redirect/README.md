# DEPRECATED: mngs → scitex

**⚠️ This package has been renamed to `scitex`.**

## Migration Instructions

### 1. Install the new package
```bash
pip uninstall mngs
pip install scitex
```

### 2. Update your imports
```python
# Old
import mngs
from mngs.io import save
from mngs.plt import subplots

# New
import scitex
from scitex.io import save
from scitex.plt import subplots
```

### 3. Update environment variables
```bash
# Old
export MNGS_SCHOLAR_DIR=~/.mngs/scholar

# New
export SCITEX_SCHOLAR_DIR=~/.scitex/scholar
```

## Why the rename?

The package has been renamed from `mngs` (monogusa) to `scitex` to better reflect its purpose as a **Sci**entific **Tex**t and data processing framework.

## Backward Compatibility

This redirect package (mngs 2.0.0+) automatically installs and imports scitex, providing temporary backward compatibility. However, we strongly recommend updating your code to use scitex directly.

## Support

For issues and documentation, please visit:
https://github.com/ywatanabe1989/scitex