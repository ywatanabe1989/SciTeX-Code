# MNGS Structure Audit Report

## Overview
- Total Python files: 447
- Main package location: `./src/mngs/`
- Test location: `./tests/mngs/`

## Current Module Structure

### Core Modules
1. **ai/** - AI/ML utilities
   - act/ - Activation functions
   - clustering/ - Clustering algorithms (PCA, UMAP)
   - feature_extraction/ - Feature extraction (ViT)
   - _gen_ai/ - Generative AI interfaces (OpenAI, Anthropic, etc.)
   - layer/ - Neural network layers
   - loss/ - Loss functions
   - metrics/ - Evaluation metrics
   - optim/ - Optimizers (includes Ranger)
   - plt/ - AI-specific plotting (AUCs, confusion matrix)
   - sampling/ - Data sampling utilities
   - sk/ - Scikit-learn utilities
   - utils/ - AI utility functions

2. **dsp/** - Digital Signal Processing
   - Multiple signal processing functions
   - Contains subdirectories for specific operations

3. **io/** - Input/Output operations
   - File loading and saving
   - Multiple format support

4. **plt/** - Plotting utilities
   - Extensive plotting functions
   - Subplot management system

5. **gen/** - General utilities
   - Environment management
   - General-purpose functions

6. **Other modules**: context, db, decorators, dev, dict, dt, etc, gists, life, linalg, nn, os, parallel, path, pd, reproduce, resource, stats, str, tex, torch, types, utils, web

## Issues Found

### 1. Versioned Files (12 files)
```
./src/mngs/ai/_gen_ai/._BaseGenAI.py-versions/_BaseGenAI.py_v001
./src/mngs/ai/_gen_ai/._Google.py-versions/_Google.py_v001
./src/mngs/ai/_gen_ai/._Google.py-versions/_Google.py_v002
./src/mngs/decorators/._DataTypeDecorators-versions/_DataTypeDecorators_v001.py
./src/mngs/decorators/._DataTypeDecorators-versions/_DataTypeDecorators_v002.py
./src/mngs/decorators/._DataTypeDecorators-versions/_DataTypeDecorators_v003.py
./src/mngs/decorators/.old/_DataTypeDecorators_v1.py_
./src/mngs/decorators/.old/DataTypeDecorator_v1.py
./src/mngs/dsp/_pac/RUNNING/2024Y-11M-26D-22h15m55s_v9IO
./src/mngs/dsp/_pac/RUNNING/2024Y-11M-26D-22h15m55s_v9IOlogs
./src/mngs/io/.old/_save_v01.py_
./src/mngs/io/_save_v01.py_
```

### 2. Structural Observations
- Hidden version directories (.-versions)
- .old directories containing backups
- RUNNING directories with timestamps
- Some modules have both underscore and non-underscore versions

### 3. Potential Duplications
- Multiple plotting modules (ai/plt vs main plt)
- Possible overlap between utils in different modules
- Version control artifacts mixed with source code

## Recommendations

### Immediate Actions
1. Clean up versioned files using safe_rm.sh
2. Remove hidden version directories
3. Clear RUNNING directories with old timestamps
4. Consolidate .old directories

### Structural Improvements
1. Consider merging overlapping modules
2. Establish clear module boundaries
3. Create consistent naming conventions
4. Separate development artifacts from source code

## Module Categories

### Scientific Computing
- dsp, linalg, stats, torch

### Data Processing
- pd (pandas utilities), io, db

### Visualization
- plt (main plotting), ai/plt (AI-specific)

### Development Tools
- decorators, dev, reproduce, resource

### Utilities
- gen, dict, dt, etc, path, str, types, utils

### Domain-Specific
- ai, nn, web, life, tex

This structure shows a comprehensive scientific computing package with some organizational issues that need addressing.