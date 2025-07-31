# Cleanup Recommendations
Date: 2025-07-31
Agent: 59cac716-6d7b-11f0-87b5-00155dff97a1

## Current State Assessment

After implementing the SSO automation architecture, here are cleanup recommendations:

### 1. Test Files in .dev Directory (20+ files)
The `.dev` directory contains numerous test files from our investigation:
- `test_bot_detection_hypothesis.py`
- `test_sso_integration.py`
- `test_javascript_popup_resolution.py`
- `test_zenrows_*.py` (multiple variants)
- `test_openurl_*.py` (multiple variants)

**Recommendation**: These were useful for diagnosis but can be cleaned up. Keep only:
- `test_bot_detection_hypothesis.py` (documents the findings)
- `test_sso_integration.py` (shows integration pattern)

### 2. Screenshots (2 directories)
Found screenshot directories that should be cleaned:
- `/zenrows_screenshots/` - Test screenshots
- `/zenrows_workflow_screenshots/` - Workflow documentation
- `openurl_*.png` files in root

**Recommendation**: Move to `.dev/screenshots_archive/` or remove entirely

### 3. Code Quality Improvements

#### In SSO Automations Module:
- Add type hints for all methods
- Add docstring examples
- Consider adding retry decorators for network operations

#### In OpenURL Resolver:
- Update to use the new SSO automators
- Add popup handling as documented
- Remove references to obsolete files

### 4. Documentation Consolidation
Created multiple documentation files:
- `openurl_failure_analysis_20250731.md`
- `openurl_improvement_plan_20250731.md`
- `openurl_complete_solution_20250731.md`
- `sso_automation_architecture.md`

**Recommendation**: Consolidate into a single comprehensive guide

### 5. Environment Variables
Document required environment variables in a `.env.example`:
```bash
# University of Melbourne
UNIMELB_USERNAME=
UNIMELB_PASSWORD=

# Optional: ZenRows (only for anti-bot publishers)
SCITEX_SCHOLAR_ZENROWS_API_KEY=
```

### 6. Tests to Add
Create proper unit tests for:
- `test_base_sso_automator.py`
- `test_unimelb_sso_automator.py`
- `test_sso_factory.py`

### 7. Integration Points
Update these files to use SSO automators:
- `src/scitex/scholar/open_url/_OpenURLResolver.py`
- `src/scitex/scholar/download/_PDFDownloader.py`

## Cleanup Commands

```bash
# Archive test files
mkdir -p .dev/archive_20250731
mv .dev/test_*.py .dev/archive_20250731/

# Clean screenshots
safe_rm.sh zenrows_screenshots
safe_rm.sh zenrows_workflow_screenshots
safe_rm.sh openurl_*.png

# Keep only essential test files
cp .dev/archive_20250731/test_bot_detection_hypothesis.py .dev/
cp .dev/archive_20250731/test_sso_integration.py .dev/
```

## Priority Actions

1. **High**: Integrate SSO automators into OpenURLResolver
2. **High**: Add popup handling to resolver
3. **Medium**: Clean up test files and screenshots
4. **Medium**: Add proper unit tests
5. **Low**: Consolidate documentation

## Code Quality Checklist

- [ ] All new classes have comprehensive docstrings
- [ ] Type hints added to all methods
- [ ] Error handling is consistent with scitex.errors
- [ ] Logging follows project conventions
- [ ] No hardcoded values (use config/env vars)
- [ ] Tests cover main functionality
- [ ] Documentation is up to date

## Next Session Goals

1. Integrate SSO automators into OpenURLResolver
2. Test with full DOI dataset
3. Add more institution implementations
4. Create user documentation