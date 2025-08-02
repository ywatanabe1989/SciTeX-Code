<!-- ---
!-- Timestamp: 2025-08-01 11:36:00
!-- Author: d833c9e2-6e28-11f0-8201-00155dff963d
!-- File: ./docs/from_agents/git_commit_summary_20250801.md
!-- --- -->

# Git Commit Summary - August 1, 2025

## Suggested Commit Messages

### For Unit-Aware Plotting Feature:
```
feat(plt): Add unit-aware plotting system

- Implement UnitAwareMixin for automatic unit handling
- Add plot_with_units() method to AxisWrapper
- Support automatic unit conversion (ms→s, mV→V)
- Include unit validation to prevent mismatches
- Add comprehensive tests (4/4 passing)
- Create example notebook demonstrating usage
```

### For Import Fixes:
```
fix(imports): Add error handling for optional dependencies

- Fix missing import guards in ai/sampling/undersample.py
- Fix missing import guards in nn/_Spectrogram.py
- Create requirements-optional.txt for feature-specific deps
- Add helpful error messages with installation instructions
```

### For Code Quality Improvements:
```
fix(plt): Use dynamic version instead of hardcoded string

- Replace hardcoded '1.11.0' with dynamic __version__ lookup
- Add fallback to 'unknown' if import fails
```

### For Notebook Fixes:
```
fix(notebooks): Resolve IndentationError in gen notebook

- Fix empty else block in XML parsing example
- Add proper fallback demonstration code
- Ensure notebook executes without syntax errors
```

### For Documentation:
```
docs: Add comprehensive quick-start guides

- Create main QUICKSTART.md with 5-minute tutorial
- Add scholar module quick-start guide
- Add plotting module guide with unit-aware examples
- Include pre-commit setup documentation
```

### For Development Infrastructure:
```
chore: Add pre-commit hooks configuration

- Configure black, isort, flake8, bandit, mypy
- Add notebook cleaning with nbstripout
- Include security and type checking
- Add custom hooks for password detection
```

## Files to Stage

### New Features:
```bash
git add src/scitex/plt/_subplots/_AxisWrapperMixins/_UnitAwareMixin.py
git add src/scitex/plt/_subplots/_AxisWrapper.py
git add src/scitex/units.py
git add .dev/test_unit_aware_plotting.py
git add examples/25_scitex_unit_aware_plotting.ipynb
```

### Bug Fixes:
```bash
git add src/scitex/ai/sampling/undersample.py
git add src/scitex/nn/_Spectrogram.py
git add src/scitex/plt/ax/_style/_set_meta.py
git add examples/notebooks/02_scitex_gen.ipynb
```

### Documentation:
```bash
git add requirements-optional.txt
git add .pre-commit-config.yaml
git add docs/QUICKSTART.md
git add docs/quickstart/
git add docs/development/pre-commit-setup.md
```

## PR Description Template

```markdown
## Summary
This PR introduces unit-aware plotting capabilities and improves overall code quality.

## Changes
- ✨ **New Feature**: Unit-aware plotting system
  - Automatic unit detection and conversion
  - Validation to prevent unit mismatches
  - Full test coverage

- 🐛 **Bug Fixes**:
  - Import error handling for optional dependencies
  - Dynamic version retrieval
  - Notebook execution errors

- 📚 **Documentation**:
  - Comprehensive quick-start guides
  - Module-specific tutorials
  - Development setup guides

- 🔧 **Infrastructure**:
  - Pre-commit hooks configuration
  - Optional dependencies documentation

## Testing
- Unit tests: 4/4 passing for unit-aware plotting
- Notebooks: Fixed execution errors
- Manual testing: Verified all examples work

## Breaking Changes
None - all changes are backward compatible.

## Checklist
- [x] Tests pass
- [x] Documentation updated
- [x] Code follows style guidelines
- [x] No breaking changes
```

---
Ready for commit! 🚀

<!-- EOF -->