# SciTeX Module Dependency Analysis Report

## Summary
- Total modules analyzed: 26
- Total dependencies: 89

## Circular Dependencies
⚠️ Found 1 circular dependencies:
1. scitex.ai._gen_ai._genai_factory → scitex.ai._gen_ai._Perplexity → scitex.ai._gen_ai._genai_factory

## Module Statistics
| Module | Files | Dependencies In | Dependencies Out | Total Coupling |
|--------|-------|-----------------|------------------|----------------|
| io | 10 | 5 | 23 | 28 |
| decorators | 10 | 7 | 15 | 22 |
| nn | 15 | 1 | 19 | 20 |
| dsp | 25 | 1 | 18 | 19 |
| gen | 13 | 3 | 12 | 15 |
| plt | 31 | 2 | 9 | 11 |
| stats | 17 | 0 | 10 | 10 |
| str | 5 | 6 | 1 | 7 |
| types | 1 | 4 | 3 | 7 |
| dict | 1 | 4 | 1 | 5 |
| utils | 3 | 3 | 1 | 4 |
| ai | 40 | 0 | 4 | 4 |
| linalg | 3 | 0 | 4 | 4 |
| _sh | 1 | 3 | 0 | 3 |
| resource | 4 | 0 | 3 | 3 |
| torch | 1 | 1 | 2 | 3 |
| pd | 4 | 1 | 1 | 2 |
| context | 1 | 1 | 1 | 2 |
| path | 4 | 2 | 0 | 2 |
| gists | 1 | 0 | 2 | 2 |
| db | 20 | 1 | 1 | 2 |
| __main__ | 1 | 0 | 1 | 1 |
| dev | 2 | 1 | 0 | 1 |
| os | 1 | 0 | 1 | 1 |
| tex | 1 | 0 | 1 | 1 |
| web | 2 | 0 | 0 | 0 |

## Detailed Dependencies

### io
**Depends on by:** ai, dsp, gen, plt, resource
**Depends on:** _cache, _flush, _glob, _json2md, _load, _load_configs, _load_modules, _mv_to_tmp, _path, _reload, _save, _save_image, _save_listed_dfs_as_csv, _save_listed_scalars_as_csv, _save_mp4, _save_optuna_study_as_csv_and_pngs, _save_text, _sh, db, decorators, dict, path, str

### decorators
**Depends on by:** dsp, gen, io, linalg, nn, plt, stats
**Depends on:** _DataTypeDecorators, _batch_fn, _cache_disk, _cache_mem, _converters, _deprecated, _not_implemented, _numpy_fn, _pandas_fn, _preserve_doc, _signal_fn, _timeout, _torch_fn, _wrap, str

### nn
**Depends on by:** dsp
**Depends on:** _AxiswiseDropout, _BNet, _ChannelGainChanger, _DropoutChannels, _Filters, _FreqGainChanger, _Hilbert, _MNet_1000, _ModulationIndex, _PAC, _PSD, _ResNet1D, _SpatialAttention, _SwapChannels, _TransposeLayer, _Wavelet, decorators, dsp, gen

### dsp
**Depends on by:** nn
**Depends on:** _crop, _demo_sig, _detect_ripples, _hilbert, _misc, _mne, _modulation_index, _pac, _psd, _resample, _time, _transform, _wavelet, decorators, gen, io, nn, str

### gen
**Depends on by:** __main__, dsp, nn
**Depends on:** _sh, _start, decorators, dev, dict, io, path, plt, reproduce, str, torch, utils

### plt
**Depends on by:** gen, tex
**Depends on:** _subplots, _tpl, context, decorators, dict, io, pd, types, utils

### stats
**Depends on:** _corr_test_multi, _corr_test_wrapper, _describe_wrapper, _multiple_corrections, _nan_stats, _p2stars_wrapper, _statistical_tests, decorators, tests, types

### str
**Depends on by:** db, decorators, dsp, gen, io, resource
**Depends on:** dict

### types
**Depends on by:** ai, pd, plt, stats
**Depends on:** _ArrayLike, _ColorLike, _is_listed_X

### dict
**Depends on by:** gen, io, plt, str
**Depends on:** utils

### utils
**Depends on by:** dict, gen, plt
**Depends on:** reproduce

### ai
**Depends on:** _gen_ai, io, reproduce, types

### linalg
**Depends on:** _distance, _geometric_median, _misc, decorators

### _sh
**Depends on by:** gen, io, resource

### resource
**Depends on:** _sh, io, str

### torch
**Depends on by:** gen
**Depends on:** _apply_to, _nan_funcs

### pd
**Depends on by:** plt
**Depends on:** types

### context
**Depends on by:** plt
**Depends on:** _suppress_output

### path
**Depends on by:** gen, io

### gists
**Depends on:** _SigMacro_processFigure_S, _SigMacro_toBlue

### db
**Depends on by:** io
**Depends on:** str

### __main__
**Depends on:** gen

### dev
**Depends on by:** gen

### os
**Depends on:** _mv

### tex
**Depends on:** plt

## Recommendations

### Highly Coupled Modules
These modules have high coupling and might benefit from refactoring:
- **str** (coupling: 7)
- **plt** (coupling: 11)
- **stats** (coupling: 10)
- **gen** (coupling: 15)
- **nn** (coupling: 20)
- **dsp** (coupling: 19)
- **decorators** (coupling: 22)
- **types** (coupling: 7)
- **io** (coupling: 28)

### Independent Modules
These modules have no dependencies (good modularity):
- web