# Jupyter Notebook Cleanup Plan
**Date**: 2025-07-04
**Priority**: 10 (Highest)
**Agent**: cd929c74-58c6-11f0-8276-00155d3c097c

## Objective
Clean up all Jupyter notebook examples to be simple, without variants or suffixes, and ensure they run cleanly without print statements.

## Files to Remove

### 1. Executed Variants (24 files)
All files ending with `_executed.ipynb`

### 2. Backup Files (37 files)
All files with extensions `.bak`, `.bak2`, `.bak3`

### 3. Test Variants (30+ files)
- `*_test_fix.ipynb`
- `*_test_fixed.ipynb`
- `*_test_output.ipynb`
- `*_output.ipynb`
- `test_*.ipynb`

### 4. Directories to Clean
- `./examples/backups/` - Contains duplicate notebooks
- `./examples/executed/` - Contains executed variants
- `./examples/notebooks_back/` - Contains backup notebooks
- `./examples/old/` - Contains legacy notebooks
- `./examples/.ipynb_checkpoints/` - Jupyter checkpoints
- `./examples/test_fixed/` - Test variants

## Base Notebooks to Keep (24 files)
1. 00_SCITEX_MASTER_INDEX.ipynb
2. 01_scitex_io.ipynb
3. 02_scitex_gen.ipynb
4. 03_scitex_utils.ipynb
5. 04_scitex_str.ipynb
6. 05_scitex_path.ipynb
7. 06_scitex_context.ipynb
8. 07_scitex_dict.ipynb
9. 08_scitex_types.ipynb
10. 09_scitex_os.ipynb
11. 10_scitex_parallel.ipynb
12. 11_scitex_stats.ipynb
13. 12_scitex_linalg.ipynb
14. 13_scitex_dsp.ipynb
15. 14_scitex_plt.ipynb
16. 15_scitex_pd.ipynb
17. 16_scitex_ai.ipynb
18. 16_scitex_scholar.ipynb
19. 17_scitex_nn.ipynb
20. 18_scitex_torch.ipynb
21. 19_scitex_db.ipynb
22. 20_scitex_tex.ipynb
23. 21_scitex_decorators.ipynb
24. 22_scitex_repro.ipynb
25. 23_scitex_web.ipynb

## Cleanup Actions
1. Use `./docs/to_claude/bin/safe_rm.sh` to safely remove all variant files
2. Ensure base notebooks have no print statements (scitex handles output)
3. Verify each notebook can run from scratch in order
4. Remove any output directories associated with variants

## Expected Result
- Only 24 clean base notebooks in `./examples/`
- No variants, backups, or test files
- All notebooks executable from scratch
- Clean directory structure