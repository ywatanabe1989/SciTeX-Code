# SciTeX Redirect Package Implementation

## Option 1: Full Redirect Package (Recommended)

### Create minimal scitex package structure:
```
scitex-redirect/
├── pyproject.toml
├── README.md
└── scitex/
    └── __init__.py
```

### scitex/__init__.py
```python
"""
SciTeX has been renamed to SciTeX!

This is a compatibility package that redirects to the new scitex package.
Please update your code to use scitex directly:

    pip install scitex
    
And update imports:
    # Old
    import scitex
    
    # New
    import scitex as stx
"""

import warnings
import sys

# Show deprecation warning
warnings.warn(
    "\n" + "="*70 + "\n"
    "IMPORTANT: 'scitex' has been renamed to 'scitex'!\n"
    "\n"
    "Please update your installation:\n"
    "    pip uninstall scitex\n" 
    "    pip install scitex\n"
    "\n"
    "And update your imports:\n"
    "    # Old:  import scitex\n"
    "    # New:  import scitex as stx\n"
    "\n"
    "This compatibility package will be removed in the future.\n"
    + "="*70,
    DeprecationWarning,
    stacklevel=2
)

try:
    # Try to import scitex and expose all its contents
    import scitex
    
    # Make all scitex attributes available through scitex
    for attr in dir(scitex):
        if not attr.startswith('_'):
            globals()[attr] = getattr(scitex, attr)
    
    # Preserve version and other metadata
    __version__ = scitex.__version__
    __author__ = scitex.__author__
    __all__ = scitex.__all__ if hasattr(scitex, '__all__') else []
    
    # Add note about deprecation to version string
    __version__ += " (DEPRECATED - use scitex)"
    
except ImportError:
    # If scitex is not installed, provide helpful error
    raise ImportError(
        "\n" + "="*70 + "\n"
        "The 'scitex' package has been renamed to 'scitex'.\n"
        "\n"
        "Please install the new package:\n"
        "    pip install scitex\n"
        "\n"
        "Then update your imports:\n"
        "    import scitex as stx\n"
        "\n"
        "For more information, visit:\n"
        "    https://github.com/yourusername/scitex\n"
        + "="*70
    ) from None

# Provide helpful message when inspecting the module
def _deprecated_help():
    """Show migration instructions."""
    print("""
    SciTeX → SciTeX Migration Guide
    =============================
    
    1. Uninstall old package:
       pip uninstall scitex
    
    2. Install new package:
       pip install scitex
    
    3. Update imports in your code:
       # Old
       import scitex
       from scitex.io import save, load
       
       # New
       import scitex as stx
       from scitex.io import save, load
    
    4. The API remains the same, only the package name changed!
    
    For issues or questions:
    https://github.com/yourusername/scitex/issues
    """)

# Add migration help to module
help = _deprecated_help
migrate = _deprecated_help
```

### pyproject.toml
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "scitex"
version = "2.0.0"
description = "DEPRECATED: Use 'scitex' instead. This is a redirect package."
authors = [{name = "Your Name", email = "your.email@example.com"}]
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.8"
classifiers = [
    "Development Status :: 7 - Inactive",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

dependencies = [
    "scitex>=2.0.0",  # Automatically install the new package!
]

[project.urls]
"Homepage" = "https://github.com/yourusername/scitex"
"New Package" = "https://pypi.org/project/scitex/"
"Migration Guide" = "https://github.com/yourusername/scitex/blob/main/MIGRATION.md"
```

### README.md
```markdown
# ⚠️ DEPRECATED: SciTeX has been renamed to SciTeX

**This package now redirects to `scitex`. Please update your dependencies!**

## Quick Migration

```bash
# The new package is automatically installed with scitex>=2.0.0
pip install --upgrade scitex

# But we recommend explicitly switching to:
pip uninstall scitex
pip install scitex
```

## Update Your Code

```python
# Old
import scitex

# New  
import scitex as stx
```

That's it! The API remains exactly the same.

## Why the change?

SciTeX is now part of the SciTeX (Scientific Text and Experiment) ecosystem, 
better reflecting its comprehensive scientific computing capabilities.

## Links

- 📦 New Package: [pypi.org/project/scitex](https://pypi.org/project/scitex/)
- 📚 Documentation: [scitex.readthedocs.io](https://scitex.readthedocs.io)
- 💻 GitHub: [github.com/yourusername/scitex](https://github.com/yourusername/scitex)
- 🔄 Migration Guide: [Full Migration Instructions](https://github.com/yourusername/scitex/blob/main/MIGRATION.md)

## Support

Having issues? Please report them at the new repository:
[github.com/yourusername/scitex/issues](https://github.com/yourusername/scitex/issues)
```

## Option 2: Import Hook Redirect (Advanced)

### Create an import hook that redirects at import time:
```python
# scitex/__init__.py
import sys
import importlib
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec

class SciTeXRedirectFinder(MetaPathFinder):
    """Redirects scitex imports to scitex."""
    
    def find_spec(self, fullname, path, target=None):
        if fullname.startswith('scitex'):
            # Replace scitex with scitex in the module name
            scitex_name = fullname.replace('scitex', 'scitex', 1)
            
            # Show warning only once per module
            if fullname not in _warned_modules:
                warnings.warn(
                    f"Importing '{fullname}' is deprecated. "
                    f"Please use '{scitex_name}' instead.",
                    DeprecationWarning,
                    stacklevel=2
                )
                _warned_modules.add(fullname)
            
            # Try to find the scitex module
            try:
                return importlib.util.find_spec(scitex_name)
            except ImportError:
                return None
        return None

_warned_modules = set()

# Install the import hook
sys.meta_path.insert(0, SciTeXRedirectFinder())

# Also do the simpler redirect for direct 'import scitex'
from scitex import *
```

## Option 3: GitHub Repository Redirect

If you rename the GitHub repository:
- GitHub automatically redirects the old URL to the new one
- Git remotes continue to work
- Issues, PRs, and stars are preserved

## Option 4: Documentation Redirect

### For Read the Docs:
```python
# docs/conf.py
# Add redirect extension
extensions = [
    'sphinx.ext.autodoc',
    'sphinx_reredirects',
    # ...
]

# Configure redirects
redirects = {
    "index": "../scitex.readthedocs.io/",
    "**": "../scitex.readthedocs.io/",
}
```

### For GitHub Pages:
Create `_redirects` or use Jekyll redirect:
```html
<!-- index.html -->
<!DOCTYPE html>
<meta charset="utf-8">
<title>Redirecting to SciTeX...</title>
<meta http-equiv="refresh" content="0; URL=https://yourusername.github.io/scitex/">
<link rel="canonical" href="https://yourusername.github.io/scitex/">
```

## Best Practices for Redirect Package

1. **Auto-install scitex**: Make `scitex` a dependency so users automatically get it
2. **Clear warnings**: Show deprecation warnings that explain exactly what to do
3. **Preserve functionality**: The redirect package should work seamlessly
4. **Set timeline**: Announce when the redirect package will be removed (e.g., 1 year)
5. **Version numbering**: Use 2.0.0 for the redirect to indicate major change

## Release Timeline Example

```
Month 0: Release scitex 2.0.0 and scitex 2.0.0 (redirect)
Month 1-6: Both packages coexist, scitex shows warnings
Month 6: Release scitex 2.1.0 with louder warnings
Month 12: Release final scitex 2.2.0 announcing removal
Month 18: Remove scitex from PyPI (optional)
```

## Testing the Redirect

```bash
# Test that old code still works
python -c "import scitex; print(scitex.io.save)"

# Should show deprecation warning but work
python -W default -c "import scitex"

# Test submodules
python -c "from scitex.io import save, load"
```

This approach ensures:
- ✅ Existing code continues to work
- ✅ Users see clear migration instructions  
- ✅ pip install scitex automatically gets scitex
- ✅ Gradual, well-communicated transition
- ✅ No broken deployments

The redirect package is lightweight and maintains backward compatibility while guiding users to the new package name.