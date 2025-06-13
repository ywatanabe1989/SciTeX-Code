# Missing Files Action Plan

## Date: 2025-06-13

## Current Situation

### 1. Branch Divergence
- **develop branch**: Missing entire `src/mngs/io/_save_modules/` directory (180+ files)
- **scitex-initial branch**: Has all files properly migrated from mngs to scitex
- **Original mngs repository**: Contains all original files

### 2. GIF Support Status
- **Issue**: GIF was declared in dispatch table but never implemented in _image.py
- **Resolution**: Added GIF support to scitex-initial branch (completed)
- **Location**: `/data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/mngs_repo/src/scitex/io/_save_modules/_image.py`

### 3. Uncommitted Changes in develop branch
- `src/mngs/ai/_gen_ai/_Google.py`
- `src/mngs/ai/feature_extraction/__init__.py`
- `src/mngs/ai/loss/__init__.py`
- `src/mngs/ai/sk/__init__.py`
- These appear to add import error handling

## Recommended Actions

### Immediate Priority
1. **Merge scitex-initial into develop** to restore missing files
   - This will bring back all 180+ missing files
   - Will include the GIF support fix
   
2. **Commit AI module changes** in develop branch
   - Review and commit the import error handling additions
   
3. **Create tests for GIF support**
   - Add comprehensive tests for the new GIF functionality
   - Test PIL Image, Plotly, and Matplotlib GIF saving

### Medium Priority
1. **Verify file integrity** after merge
   - Ensure all files from mngs are properly present
   - Check for any merge conflicts
   
2. **Update documentation**
   - Document GIF support in API docs
   - Update save function documentation

### Long Term
1. **Establish test coverage** for _save_modules
   - Create test directory structure
   - Add tests for all save formats
   
2. **Clean up repository structure**
   - Remove obsolete files
   - Ensure consistent naming between mngs and scitex

## Technical Details

### Missing Directories
- `src/mngs/io/_save_modules/` (entire directory)
- Various test files for save modules

### GIF Implementation Added
```python
# GIF
elif spath.endswith(".gif"):
    # PIL image
    if isinstance(obj, Image.Image):
        obj.save(spath, save_all=True)
    # plotly - convert via PNG first
    elif isinstance(obj, plotly.graph_objs.Figure):
        buf = _io.BytesIO()
        obj.write_image(buf, format="png")
        buf.seek(0)
        img = Image.open(buf)
        img.save(spath, "GIF")
        buf.close()
    # matplotlib
    else:
        buf = _io.BytesIO()
        try:
            obj.savefig(buf, format="png")
        except:
            obj.figure.savefig(buf, format="png")
        buf.seek(0)
        img = Image.open(buf)
        img.save(spath, "GIF")
        buf.close()
    del obj
```

## Next Steps
1. Get approval for merge strategy
2. Backup current state
3. Execute merge from scitex-initial to develop
4. Test functionality
5. Update documentation