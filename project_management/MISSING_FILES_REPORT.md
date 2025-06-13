# Missing Files Report - mngs Repository Comparison

## Summary
Total missing files: 180
Comparison between mngs-original/main branch and current repository

## Missing Files by Module

### IO Module (22 files)
- `.gitkeep`
- `README.md`
- **_save_modules/** (20 files)
  - `__init__.py`
  - `_catboost.py`
  - `_csv.py`
  - `_excel.py`
  - `_hdf5.py`
  - `_html.py`
  - `_image.py`
  - `_joblib.py`
  - `_json.py`
  - `_listed_dfs_as_csv.py`
  - `_listed_scalars_as_csv.py`
  - `_matlab.py`
  - `_mp4.py`
  - `_numpy.py`
  - `_optuna_study_as_csv_and_pngs.py`
  - `_pickle.py`
  - `_plotly.py`
  - `_text.py`
  - `_torch.py`
  - `_yaml.py`

### AI Module (68 files)
Major missing components:
- Documentation files
- Test output directories
- Configuration files

### PLT Module (61 files)
Major missing components:
- Gallery-related files
- Output directories
- GIF-related files (including `_scientific_captions_out/test_figure_4_enhanced.gif`)

### DSP Module (16 files)
- Various output directories
- Documentation files

### Stats Module (7 files)
- Documentation and configuration files

### Other Modules
- **gen**: 2 files
- **str**: 3 files  
- **path**: 1 file
- **pd**: 0 files (complete)
- **dict**: 0 files (complete)
- **nn**: 0 files (complete)

## GIF-Related Files
- `examples/plt_gallery/convert_to_gif.py` (not in src/mngs)
- `src/mngs/plt/utils/_scientific_captions_out/test_figure_4_enhanced.gif`

## Critical Missing Components
1. **IO _save_modules**: Complete directory with 20 save modules
2. **Documentation files**: Multiple README.md and .gitkeep files
3. **Test output directories**: Various _out directories
4. **Configuration files**: Various module-specific configs

## Next Steps
1. Restore missing _save_modules in IO module
2. Review and restore critical functionality files
3. Determine if documentation files need restoration
4. Assess impact of missing output directories