<!-- ---
!-- Timestamp: 2025-07-04 11:21:00
!-- Author: fe6fa634-5871-11f0-9666-00155d3c010a
!-- File: ./project_management/feature-requests/feature-request-improved-notebook-path-handling.md
!-- --- -->

# Feature Request: Improved Path Handling for Notebook Environments

## Summary
Enhance `scitex.io.save()` to better handle different execution environments (scripts, notebooks, IPython console) with more intuitive path behavior.

## Current Behavior
- Scripts: Save to `{script_name}_out/` directory
- IPython/Notebooks: Save to `/tmp/{USER}/` directory
- Detection: Simple check for "ipython" in stack or `<stdin>`

## Problems
1. **Notebook users expect files in working directory**, not `/tmp/`
2. **Poor environment discrimination** - notebooks and IPython console treated the same
3. **Confusing for interactive use** - files disappear to `/tmp/`
4. **Breaks notebook examples** that expect files in relative paths

## Proposed Solution

### 1. Enhanced Environment Detection
Created `scitex.gen._detect_environment.py` with better detection:
```python
def detect_environment() -> Literal['script', 'jupyter', 'ipython', 'interactive', 'unknown']:
    # Check ipykernel + ZMQInteractiveShell for Jupyter
    # Check TerminalInteractiveShell for IPython console
    # Check sys.argv[0].endswith('.py') for scripts
    # Check hasattr(sys, 'ps1') for interactive Python
```

### 2. Environment-Specific Path Strategies
- **Scripts**: Current behavior (`{script_name}_out/`)
- **Jupyter Notebooks**: `{notebook_name}_out/` (same pattern as scripts!)
  - If notebook is `./examples/analysis.ipynb`
  - Output goes to `./examples/analysis_out/`
- **IPython Console**: `/tmp/{USER}/ipython/` (no fixed location)
- **Interactive Python**: `/tmp/{USER}/python/`

### 3. Configuration Options
Add parameters to `scitex.io.save()`:
```python
scitex.io.save(data, "file.csv", 
    notebook_mode=True,  # Force notebook-friendly paths
    base_dir="./outputs",  # Override base directory
    use_script_dir=False  # Disable script_out convention
)
```

### 4. Environment Variable Override
```bash
export SCITEX_OUTPUT_MODE=notebook  # or 'script', 'temp'
export SCITEX_OUTPUT_DIR=./my_outputs
```

## Benefits
1. **Notebooks work as expected** - files appear where users expect
2. **Better user experience** - intuitive behavior per environment
3. **Backward compatible** - existing scripts unchanged
4. **Configurable** - users can override defaults

## Implementation Steps
1. ✅ Create enhanced environment detection module
2. ⬜ Update `scitex.io._save.py` to use new detection
3. ⬜ Add configuration parameters
4. ⬜ Update documentation and examples
5. ⬜ Test in all environments

## Alternative Approaches
1. **Always use current directory** - simpler but breaks existing workflows
2. **Add `save_here()` function** - explicit local save for notebooks
3. **Detect `.ipynb` files** - check for notebook file in working directory

## Additional Benefits of {notebook_name}_out/ Approach
1. **Consistency** - Same pattern for scripts and notebooks
2. **Discoverability** - Output directory right next to notebook file
3. **Organization** - Each notebook has its own output directory
4. **No collisions** - Different notebooks don't overwrite each other's outputs
5. **Git-friendly** - Easy to add `*_out/` to .gitignore

## Code Example
```python
# In notebook
import scitex as stx

# Current: saves to /tmp/ywatanabe/data.csv
stx.io.save(df, "data.csv")  

# Proposed: If notebook is ./analysis.ipynb
# saves to ./analysis_out/data.csv
stx.io.save(df, "data.csv")

# Or with explicit mode
stx.io.save(df, "data.csv", notebook_mode=True)
```

## Priority
High - This affects all notebook users and example execution

<!-- EOF -->