# AI Module Reorganization Plan

## Current Structure Issues
- Mixed responsibilities in single directory
- Unclear module boundaries
- Vendored code mixed with core functionality

## New Structure

```
scitex/ai/
├── genai/              # Generative AI providers (from _gen_ai/)
├── clustering/         # UMAP, PCA, etc. (already exists)
├── metrics/            # bACC, silhouette score (already exists)
├── training/           # Training utilities
│   ├── early_stopping.py (moved from root)
│   ├── learning_curve_logger.py (moved from root)
│   └── __init__.py
├── visualization/      # Visualization utilities
│   └── (link to plt submodule)
├── sklearn/            # sklearn wrappers
│   └── (move from sk/)
├── classification/     # Classification utilities
│   ├── classification_reporter.py (moved from root)
│   ├── classifier_server.py (moved from root)
│   └── __init__.py
└── __init__.py         # Updated imports
```

## Migration Steps

### Phase 1: Structure Creation (Current)
1. ✅ Create new directories
2. ✅ Document migration plan

### Phase 2: File Movement
1. Move _gen_ai/* → genai/
2. Move early_stopping.py, _LearningCurveLogger.py → training/
3. Move classification_reporter.py, classifier_server.py → classification/
4. Move sk/* → sklearn/

### Phase 3: Import Updates
1. Update __init__.py files in each submodule
2. Update main ai/__init__.py
3. Update all imports throughout codebase

### Phase 4: Cleanup
1. Remove empty directories
2. Update tests to match new structure
3. Verify all functionality works

## Benefits
- Clear separation of concerns
- Better discoverability
- Easier to maintain and extend
- Follows Python packaging best practices