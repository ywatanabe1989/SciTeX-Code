# Rebranding Plan: SciTeX → SciTeX

## Overview
This document outlines the complete rebranding process from `scitex` to `scitex` as part of the SciTeX ecosystem.

## Phase 1: Pre-Migration Checklist

### 1. Backup Current State
```bash
# Create backup branch
git checkout -b pre-rebranding-backup
git push origin pre-rebranding-backup

# Tag current version
git tag v1.11.0-final-scitex
git push origin v1.11.0-final-scitex
```

### 2. Check Current PyPI Status
- Current package: https://pypi.org/project/scitex/
- Reserve new name: https://pypi.org/project/scitex/

## Phase 2: Code Rebranding

### 1. Test Rename Script (Dry Run)
```bash
# First, do a dry run to see what will change
./docs/to_claude/bin/general/rename.sh 'scitex' 'scitex' .
```

### 2. Execute Rename
```bash
# Actually perform the rename
./docs/to_claude/bin/general/rename.sh -n 'scitex' 'scitex' .
```

### 3. Manual Updates Needed

#### Update pyproject.toml
```toml
[project]
name = "scitex"
description = "SciTeX: Scientific Text and Experiment toolkit"

[project.urls]
"Homepage" = "https://github.com/yourusername/scitex"
"Bug Tracker" = "https://github.com/yourusername/scitex/issues"
```

#### Update setup.py (if exists)
```python
setup(
    name="scitex",
    # ... other fields
)
```

#### Update README.md
- Change all references from SciTeX to SciTeX
- Update installation instructions: `pip install scitex`
- Update import examples: `import scitex as stx`

#### Update Documentation
- Sphinx conf.py: Change project name
- Update all documentation references
- Update badges and links

## Phase 3: Directory Structure Updates

### 1. Rename Main Package Directory
```bash
mv src/scitex src/scitex
```

### 2. Update Import Paths in Tests
```bash
# This should be handled by rename script, but verify:
find tests -name "*.py" -exec grep -l "from scitex" {} \;
find tests -name "*.py" -exec grep -l "import scitex" {} \;
```

## Phase 4: Git Repository Migration

### 1. Update Git Remote (New Repository)
```bash
# If creating new repository
git remote add scitex https://github.com/yourusername/scitex.git
git push scitex main

# Or rename existing repository on GitHub
# GitHub Settings → Repository name → Rename to "scitex"
```

### 2. Update Git Hooks and CI/CD
- Update GitHub Actions workflows
- Update any references to old repository name

## Phase 5: PyPI Migration Strategy

### Option A: Deprecate Old Package
```python
# In scitex package, release final version with deprecation notice
# setup.py or pyproject.toml
long_description = """
# DEPRECATED: scitex has been renamed to scitex

Please install the new package:
```
pip install scitex
```

Update your imports:
```python
# Old
import scitex

# New
import scitex as stx
```

For more information, visit: https://github.com/yourusername/scitex
"""
```

### Option B: Maintain Compatibility
```python
# Create a compatibility package that imports from scitex
# scitex/__init__.py
import warnings
warnings.warn(
    "scitex is deprecated, please use 'import scitex' instead",
    DeprecationWarning,
    stacklevel=2
)

from scitex import *
```

## Phase 6: Testing

### 1. Run All Tests
```bash
# After renaming
pytest tests/ -v

# Check imports work
python -c "import scitex; print(scitex.__version__)"
```

### 2. Test Installation
```bash
# Create fresh virtual environment
python -m venv test_env
source test_env/bin/activate

# Install locally
pip install -e .

# Test basic functionality
python -c "import scitex as stx; print('Success!')"
```

## Phase 7: Documentation Updates

### 1. Update Citations
```bibtex
@software{scitex2025,
  title = {SciTeX: Scientific Text and Experiment Toolkit},
  author = {Your Name},
  year = {2025},
  url = {https://github.com/yourusername/scitex}
}
```

### 2. Update Examples
- Rename all example files
- Update import statements
- Update output directories

## Phase 8: Release Process

### 1. Create New PyPI Package
```bash
# Build the package
python -m build

# Upload to TestPyPI first
python -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ scitex

# Upload to PyPI
python -m twine upload dist/*
```

### 2. GitHub Release
- Create new release with tag `v2.0.0-scitex`
- Include migration guide in release notes

## Phase 9: Community Communication

### 1. Announcement Template
```markdown
# 🎉 SciTeX is now SciTeX!

We're excited to announce that SciTeX has been rebranded to **SciTeX** 
(Scientific Text and Experiment toolkit) as part of the growing SciTeX ecosystem.

## What's Changed?
- Package name: `scitex` → `scitex`
- Import convention: `import scitex as stx`
- Repository: [github.com/yourusername/scitex](https://github.com/yourusername/scitex)

## Migration Guide
```bash
# Uninstall old package
pip uninstall scitex

# Install new package
pip install scitex
```

Update your imports:
```python
# Old
import scitex

# New
import scitex as stx
```

## Why the Change?
SciTeX better reflects our mission to provide comprehensive tools for 
scientific computing, text processing, and experiment management.
```

### 2. Update Channels
- GitHub repository description
- PyPI package description  
- Documentation site
- Any blog posts or tutorials

## Phase 10: Post-Migration

### 1. Monitor Issues
- Watch for migration-related issues
- Provide support for users migrating

### 2. Maintain Legacy Support
- Keep scitex package with deprecation notice for 6-12 months
- Redirect documentation to new site

### 3. Update Dependencies
- Notify projects that depend on scitex
- Submit PRs to update their dependencies

## Automation Script

Create `migrate_to_scitex.sh`:
```bash
#!/bin/bash
set -e

echo "Starting SciTeX → SciTeX migration..."

# Backup
git checkout -b rebranding-backup-$(date +%Y%m%d)
git commit -am "Backup before rebranding"

# Run rename
./docs/to_claude/bin/general/rename.sh -n 'scitex' 'scitex' .

# Rename directory
mv src/scitex src/scitex

# Update imports in specific files that might be missed
find . -name "*.py" -exec sed -i 's/from scitex/from scitex/g' {} \;
find . -name "*.py" -exec sed -i 's/import scitex/import scitex/g' {} \;

# Run tests
pytest tests/ -v

echo "Migration complete! Please review changes and update documentation manually."
```

## Timeline Estimate
- Phase 1-3: 1-2 hours (code changes)
- Phase 4-5: 2-3 hours (repository and PyPI setup)
- Phase 6-7: 2-3 hours (testing and documentation)
- Phase 8-10: 1-2 days (release and communication)

**Total: 1-2 days of focused work**

## Conclusion
The rebranding from SciTeX to SciTeX is straightforward thanks to the rename script. The main challenges are:
1. PyPI package migration and user communication
2. Updating external references and dependencies
3. Maintaining backward compatibility during transition

The scientific Python community is generally understanding about rebranding when it's well-communicated and provides clear migration paths.