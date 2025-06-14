# CI/CD Workflow Update Task

## Issue Discovered
The GitHub Actions workflow files still contain references to the old `mngs` package name instead of `scitex`.

## Files to Update
1. `.github/workflows/install-develop-branch.yml`
2. `.github/workflows/test-with-coverage.yml`
3. `.github/workflows/custom-run-pytest.yml`
4. `.github/workflows/install-pypi-latest.yml`
5. `.github/workflows/install-latest-release.yml`
6. `.github/workflows/test-comprehensive.yml`
7. `.github/workflows/release.yml`

## Required Changes
- Replace `mngs` with `scitex` in all references
- Update GitHub repository URLs from `ywatanabe1989/mngs` to correct repository
- Update import statements and package names
- Update file paths from `tests/mngs` to `tests/scitex`
- Update coverage paths from `src/mngs` to `src/scitex`

## Started
- Already updated `ci.yml` main workflow file

---
Agent: e8e4389a-39e5-4aa3-92c5-5cb96bdee182
Timestamp: 2025-06-14 22:17