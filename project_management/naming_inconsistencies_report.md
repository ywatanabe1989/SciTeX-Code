# SciTeX Naming Inconsistencies Analysis

## File Naming Issues
Found 1 file naming issues:

- Not snake_case: src/scitex/ai/optim/Ranger_Deep_Learning_Optimizer/ranger/ranger913A.py

## Function Naming Issues
Found 14 functions not following snake_case:

- src/scitex/gen/_close.py:59 - _escape_ANSI_from_log_files
- src/scitex/gists/_SigMacro_toBlue.py:1 - SigMacro_toBlue
- src/scitex/gists/_SigMacro_processFigure_S.py:1 - SigMacro_processFigure_S
- src/scitex/dsp/utils/pac.py:57 - plot_PAC_scitex_vs_tensorpac
- src/scitex/types/_is_listed_X.py:13 - is_listed_X
- src/scitex/ai/classification_reporter.py:157 - calc_bACC
- src/scitex/ai/classification_reporter.py:229 - calc_AUCs
- src/scitex/ai/classification_reporter.py:267 - _calc_AUCs_binary
- src/scitex/ai/plt/_conf_mat.py:199 - calc_bACC_from_cm
- src/scitex/ai/metrics/_bACC.py:12 - bACC
... and 4 more

## Class Naming Issues
✅ All classes follow PascalCase!

## Inconsistent Abbreviations
Found inconsistent abbreviations (showing first 20):

- src/scitex/str/__init__.py:14 - '\bfilename\b' should be 'filepath'
- src/scitex/str/__init__.py:15 - '\bfilename\b' should be 'filepath'
- src/scitex/str/__init__.py:16 - '\bfilename\b' should be 'filepath'
- src/scitex/str/__init__.py:26 - '\bfilename\b' should be 'filepath'
- src/scitex/plt/ax/_style/_set_ticks.py:233 - '\bfs\b' should be 'sample_rate'
- src/scitex/plt/ax/_style/_set_ticks.py:234 - '\bfs\b' should be 'sample_rate'
- src/scitex/plt/utils/_calc_nice_ticks.py:23 - '\bnum_' should be 'n_'
- src/scitex/plt/utils/_calc_nice_ticks.py:40 - '\bnum_' should be 'n_'
- src/scitex/plt/utils/_calc_nice_ticks.py:72 - '\bnum_' should be 'n_'
- src/scitex/plt/utils/_calc_nice_ticks.py:84 - '\bnum_' should be 'n_'
- src/scitex/plt/utils/_calc_nice_ticks.py:85 - '\bnum_' should be 'n_'
- src/scitex/plt/_subplots/__init__.py:20 - '\bfilename\b' should be 'filepath'
- src/scitex/plt/_subplots/__init__.py:21 - '\bfilename\b' should be 'filepath'
- src/scitex/plt/_subplots/__init__.py:22 - '\bfilename\b' should be 'filepath'
- src/scitex/plt/_subplots/__init__.py:37 - '\bfilename\b' should be 'filepath'
- src/scitex/plt/_subplots/_FigWrapper.py:55 - '\bfname\b' should be 'filepath'
- src/scitex/plt/_subplots/_FigWrapper.py:58 - '\bfname\b' should be 'filepath'
- src/scitex/plt/_subplots/_FigWrapper.py:62 - '\bfname\b' should be 'filepath'
- src/scitex/plt/color/_interpolate.py:18 - '\bnum_' should be 'n_'
- src/scitex/plt/color/_interpolate.py:22 - '\bnum_' should be 'n_'

## Missing Docstrings
Found functions/classes without docstrings (showing first 20):

- src/scitex/__main__.py:46 - main
- src/scitex/str/_gen_timestamp.py:9 - gen_timestamp
- src/scitex/str/_mask_api.py:7 - mask_api
- src/scitex/str/_mask_api_key.py:7 - mask_api
- src/scitex/str/_gen_ID.py:11 - gen_id
- src/scitex/str/_search.py:61 - to_list
- src/scitex/str/_print_debug.py:11 - print_debug
- src/scitex/plt/ax/_style/_sci_note.py:17 - OOMFormatter
- src/scitex/plt/ax/_style/_sci_note.py:18 - __init__
- src/scitex/plt/ax/_style/_add_marginal_ax.py:17 - add_marginal_ax
- src/scitex/plt/ax/_style/_force_aspect.py:16 - force_aspect
- src/scitex/plt/ax/_style/_set_ticks.py:21 - set_ticks
- src/scitex/plt/ax/_style/_map_ticks.py:92 - numeric_example
- src/scitex/plt/ax/_style/_map_ticks.py:113 - string_example
- src/scitex/plt/ax/_style/_add_panel.py:51 - panel
- src/scitex/plt/ax/_style/_share_axes.py:18 - sharexy
- src/scitex/plt/ax/_style/_share_axes.py:23 - sharex
- src/scitex/plt/ax/_style/_share_axes.py:28 - sharey
- src/scitex/plt/ax/_style/_share_axes.py:33 - get_global_xlim
- src/scitex/plt/ax/_style/_share_axes.py:64 - get_global_ylim

Note: Private functions (_name) are excluded from this check.

## Summary
- Total naming issues: 55
- File naming issues: 1
- Function naming issues: 14
- Class naming issues: 0
- Abbreviation issues: 20+
- Missing docstrings: 20+