<!-- ---
!-- Timestamp: 2025-07-04 20:39:00
!-- Author: Claude
!-- File: /home/ywatanabe/proj/SciTeX-Code/project_management/github_actions_fixes_20250704.md
!-- --- -->

# GitHub Actions Fixes - 2025-07-04

## Issues Fixed

### 1. Documentation Requirements Path ✅
**Problem**: CI referenced `docs/requirements.txt` but file is at `docs/RTD/requirements.txt`
**Fix**: Updated ci.yml line 104:
```yaml
pip install -r docs/RTD/requirements.txt
```

### 2. Documentation Build Path ✅
**Problem**: CI tried to build docs from `docs/` but documentation is in `docs/RTD/`
**Fix**: Updated ci.yml lines 108-110:
```yaml
cd docs/RTD
make clean
make html
```

### 3. Documentation Artifact Path ✅
**Problem**: Upload artifact looked for `docs/_build/html/` but should be `docs/RTD/_build/html/`
**Fix**: Updated ci.yml line 116:
```yaml
path: docs/RTD/_build/html/
```

### 4. Flake8 Scanning .old Directories ✅
**Problem**: Flake8 was checking archived code in .old directories causing false failures
**Fixes**: 
- Updated ci.yml to exclude .old directories in flake8 commands
- Created `.flake8` configuration file with proper exclusions

### 5. Flake8 Configuration ✅
**Created**: `.flake8` configuration file with:
- Excluded directories: .old, __pycache__, build, dist, etc.
- Set max-line-length: 127
- Set max-complexity: 10
- Added compatibility with black formatter

## Files Modified
1. `.github/workflows/ci.yml` - Fixed paths and exclusions
2. `.flake8` (new) - Created flake8 configuration

## Testing
Local testing shows all components working:
- ✅ Python imports
- ✅ Linting tools installed
- ✅ Documentation builds
- ✅ Tests collect properly
- ✅ Package builds

## Expected Results
After these fixes, GitHub Actions should:
1. Successfully install documentation dependencies
2. Build documentation without path errors
3. Skip linting archived .old directories
4. Upload correct documentation artifacts

## Next GitHub Push
The CI pipeline should now pass. Key improvements:
- No more "file not found" errors for docs/requirements.txt
- No more linting failures from archived code
- Documentation builds from correct directory
- Artifacts uploaded from correct path

## Verification
To verify locally before push:
```bash
# Test documentation build
cd docs/RTD
make clean
make html

# Test flake8 with new config
flake8 src/scitex

# Run pytest
pytest tests/scitex -v
```

All GitHub Actions errors mentioned in CLAUDE.md should now be resolved.

<!-- EOF -->