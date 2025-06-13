# Test Environment Fix Guide
## Fixed Import Issues in SciTeX

### Summary of Fixes Applied

1. **Created Clean Test Environment Scripts**
   - `/scripts/setup_test_env.sh` - Sets clean PYTHONPATH
   - `/scripts/run_tests_clean.py` - Python test runner with environment cleanup
   - `/scripts/run_tests_summary.py` - Test suite summary runner

2. **Fixed Module Imports**
   - Updated `src/scitex/db/__init__.py` - Removed mngs imports
   - Updated `src/scitex/general/__init__.py` - Removed mngs imports
   - Updated `src/scitex/tex/__init__.py` - Removed mngs imports
   - Updated `src/scitex/linalg/__init__.py` - Fixed function imports
   - Updated `src/scitex/web/__init__.py` - Removed mngs imports
   - Updated `src/scitex/res/__init__.py` - Removed mngs imports
   - Fixed `src/scitex/ai/feature_extraction/__init__.py` - Updated error message
   - Fixed `src/scitex/stats/tests/_brunner_munzel_test.py` - Fixed typing imports

### How to Run Tests

**Always use the clean environment scripts:**

```bash
# Run specific test file
./scripts/setup_test_env.sh python -m pytest tests/scitex/test__sh.py -v

# Run test directory
./scripts/setup_test_env.sh python -m pytest tests/scitex/io/ -v

# Run core import verification
./scripts/setup_test_env.sh python tests/test_core_imports.py

# Run test summary
python scripts/run_tests_summary.py
```

### Known Issues

1. **scitex.dsp Module - FIXED**
   - Made audio functionality optional to handle missing PortAudio on HPC
   - Module now imports successfully with warnings for unavailable features
   - Audio features will work when PortAudio is installed

### Test Results

- ✅ Import verification: PASS
- ✅ Shell module: PASS (28 tests)
- ✅ IO module: Imports work correctly
- ✅ Database module: Imports work correctly
- ✅ Most core modules: Import successfully
- ❌ DSP module: Requires PortAudio library

### Important Notes

1. **PYTHONPATH Conflicts**: The main issue was that `/data/gpfs/projects/punim2354/ywatanabe/mngs_repo/src` was in the Python path, causing imports to come from the old mngs repository instead of scitex.

2. **Clean Environment**: The setup scripts ensure:
   - Only SciTeX source is in PYTHONPATH
   - No user site packages interfere (`PYTHONNOUSERSITE=1`)
   - Consistent test environment

3. **Module Structure**: All modules now import from local scitex modules, not from mngs.

### For Other Agents

When running tests, always use the clean environment scripts provided. Do not run pytest directly as it may pick up incorrect import paths.