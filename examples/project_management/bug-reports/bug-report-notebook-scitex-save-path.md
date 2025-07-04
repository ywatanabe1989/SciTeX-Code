<!-- ---
!-- Timestamp: 2025-07-04 11:16:00
!-- Author: fe6fa634-5871-11f0-9666-00155d3c010a
!-- File: ./project_management/bug-reports/bug-report-notebook-scitex-save-path.md
!-- --- -->

# Bug Report: Notebook Execution Fails Due to SciTeX Path Management

## Summary
Example notebooks fail when executed with papermill because `scitex.io.save()` saves files to `script_out/` directory following SciTeX conventions, but the notebooks expect files to be saved in the current working directory.

## Environment
- SciTeX version: 2.0.0
- Python: 3.11
- Papermill: Latest
- Location: `./examples/01_scitex_io.ipynb`

## Steps to Reproduce
1. Install papermill: `pip install papermill`
2. Create scitex kernel: `python -m ipykernel install --user --name scitex`
3. Run notebook: `cd examples && papermill 01_scitex_io.ipynb output.ipynb --kernel scitex`

## Expected Behavior
Notebook should execute successfully, with files saved and accessible for subsequent operations.

## Actual Behavior
Notebook fails at cell 6 with:
```
FileNotFoundError: [Errno 2] No such file or directory: 'io_examples/large_data.pkl'
```

## Root Cause
The notebook code:
```python
uncompressed_file = data_dir / "large_data.pkl"
scitex.io.save(large_data, uncompressed_file)
file_sizes['uncompressed'] = uncompressed_file.stat().st_size  # FAILS HERE
```

`scitex.io.save()` follows SciTeX conventions and saves to `./01_scitex_io_out/io_examples/large_data.pkl` instead of `./io_examples/large_data.pkl`.

## Proposed Solutions
1. **Update notebooks** to use the actual save path returned by `scitex.io.save()`
2. **Add symlink_from_cwd=True** parameter to ensure files are accessible from expected location
3. **Modify notebooks** to check the `_out` directory for saved files
4. **Add notebook mode** to `scitex.io.save()` that saves in current directory for interactive use

## Workaround
For now, users should run notebooks interactively in Jupyter where the path issues are less problematic, or modify the notebooks to account for SciTeX path conventions.

<!-- EOF -->