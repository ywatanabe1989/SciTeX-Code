<!-- ---
!-- Timestamp: 2025-07-04 20:38:00
!-- Author: Claude
!-- File: /home/ywatanabe/proj/SciTeX-Code/project_management/github_actions_analysis_20250704.md
!-- --- -->

# GitHub Actions Analysis - 2025-07-04

## Overview
Analysis of GitHub Actions CI/CD workflows to identify persistent errors mentioned in CLAUDE.md.

## Current Workflow Configuration

### Workflows Found
1. **ci.yml** - Main CI pipeline (test, lint, docs, package)
2. **test-comprehensive.yml** - Comprehensive test suite
3. **test-with-coverage.yml** - Tests with coverage reporting
4. **release.yml** - PyPI release automation
5. **custom-run-pytest.yml** - Custom pytest runs
6. **install-*.yml** - Installation test workflows

### CI Pipeline Structure (ci.yml)
- **Test Job**: Python 3.8, 3.9, 3.10, 3.11
- **Lint Job**: flake8, black, isort, mypy
- **Docs Job**: Sphinx documentation build
- **Package Job**: Build and check distribution

## Local Testing Results

### ✅ Working Components
1. **Python environment** - 3.11.0rc1
2. **Package import** - `import scitex` works (v2.0.0)
3. **Linting tools** - All installed and functioning:
   - flake8 7.3.0
   - black 25.1.0
   - isort 6.0.1
   - mypy 1.16.1
4. **Build tools** - python-build 1.2.2.post1
5. **Documentation** - conf.py imports successfully
6. **Test collection** - pytest can find and collect tests

### ⚠️ Potential Issues

#### 1. Test Directory Reference
**Issue**: CI references `tests/scitex` but may need adjustment
**In ci.yml line 40**:
```yaml
python -m pytest tests/scitex -v --cov=src/scitex
```
**Status**: Directory exists and tests collect properly

#### 2. Documentation Path
**Issue**: CI references `docs/requirements.txt` but actual path is `docs/RTD/requirements.txt`
**In ci.yml line 104**:
```yaml
pip install -r docs/requirements.txt
```
**Fix needed**: Update to `docs/RTD/requirements.txt`

#### 3. Flake8 Warnings in .old Directory
**Issue**: Flake8 finds issues in archived .old directories
**Output**: 
```
src/scitex/.old/SciTeX-Scholar-20250701_235036/...F824 `global sys` is unused
```
**Fix needed**: Exclude .old directories from linting

## Likely Root Causes

### 1. Documentation Build Path
The most likely CI failure is in the docs job:
- CI expects `docs/requirements.txt`
- Actual file is at `docs/RTD/requirements.txt`
- This would cause pip install to fail

### 2. Linting False Positives
Flake8 is checking archived code in .old directories, which may cause the lint job to fail.

### 3. Missing Dependencies
Some GitHub Actions specific dependencies might not be in requirements.txt

## Recommended Fixes

### Fix 1: Update Documentation Path
```yaml
# In ci.yml, line 104
pip install -r docs/RTD/requirements.txt
```

### Fix 2: Exclude .old Directories
```yaml
# In ci.yml, line 75
flake8 src/scitex --count --exclude=.old --exit-zero --max-complexity=10
```

### Fix 3: Create Setup Configuration
Add to flake8 configuration:
```ini
# setup.cfg or .flake8
[flake8]
exclude = .old,__pycache__,.git,build,dist
```

### Fix 4: Verify All Paths
- Ensure all workflow files reference correct paths
- Update any remaining mngs references to scitex

## Action Items
1. [ ] Update docs/requirements.txt path in ci.yml
2. [ ] Add .old exclusion to linting commands
3. [ ] Create/update .flake8 configuration
4. [ ] Test workflows with act (GitHub Actions locally)
5. [ ] Monitor next CI run after fixes

## Testing Command
To test CI locally with act:
```bash
# Install act if not available
# brew install act  # macOS
# or download from https://github.com/nektos/act

# Test the CI workflow
act -j test
act -j lint
act -j docs
```

## Conclusion
The GitHub Actions setup is mostly correct. The main issues appear to be:
1. Documentation requirements path mismatch
2. Linting scanning archived .old directories
3. Possible missing workflow-specific dependencies

These are minor configuration issues that can be fixed with the updates suggested above.

<!-- EOF -->