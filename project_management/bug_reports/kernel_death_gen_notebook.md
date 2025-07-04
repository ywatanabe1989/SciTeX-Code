<!-- ---
!-- Timestamp: 2025-07-04 19:05:00
!-- Author: Claude
!-- File: ./project_management/bug_reports/kernel_death_gen_notebook.md
!-- --- -->

# Bug Report: Kernel Death in 02_scitex_gen.ipynb

## Issue Description
The notebook `examples/02_scitex_gen.ipynb` causes kernel death when executed with papermill, preventing automated testing of the notebook.

## Severity
Medium - Prevents automated testing but doesn't affect library functionality

## Steps to Reproduce
1. Run: `python scripts/test_single_notebook.py examples/02_scitex_gen.ipynb`
2. Notebook execution fails with "nbclient.exceptions.DeadKernelError: Kernel died"

## Expected Behavior
The notebook should execute completely without kernel crashes.

## Actual Behavior
The kernel dies during execution, likely around cell 15 (the caching demonstration cell).

## Potential Causes
1. **Caching cell**: The modified caching demonstration might be consuming too much memory
2. **TimeStamper cell**: Although we reduced sleep times, there might be other issues
3. **Environment detection functions**: Some of the gen module functions might not work well in papermill context

## Already Fixed Issues
- Fixed `to_even()` and `to_odd()` to handle scalar inputs only (not arrays)
- Fixed `transpose()` usage to use numpy's `.T` instead of scitex's dimension-based transpose
- Reduced sleep times in demonstration cells

## Suggested Next Steps
1. Run the notebook interactively to identify the exact cell causing kernel death
2. Add memory profiling to identify memory-intensive operations
3. Consider simplifying or removing problematic demonstration cells
4. Add error handling and recovery mechanisms

## Related Files
- `examples/02_scitex_gen.ipynb`
- `src/scitex/gen/_cache.py`
- `src/scitex/gen/_TimeStamper.py`

<!-- EOF -->