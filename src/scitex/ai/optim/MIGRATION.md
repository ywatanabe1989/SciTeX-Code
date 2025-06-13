# Ranger Optimizer Migration Guide

## Overview
The Ranger optimizer has been migrated from a vendored implementation to use the external `pytorch-optimizer` package.

## Changes

### Before
```python
from scitex.ai.optim.Ranger_Deep_Learning_Optimizer.ranger.ranger2020 import Ranger
```

### After
```python
from pytorch_optimizer import Ranger21 as Ranger
```

## Installation
```bash
pip install pytorch-optimizer
```

## Backward Compatibility
- The old API (`scitex.ai.optim.get` and `scitex.ai.optim.set`) still works but shows deprecation warnings
- The vendored Ranger code is used as fallback if pytorch-optimizer is not installed
- New code should use `get_optimizer` and `set_optimizer`

## Example Usage

### Old API (deprecated)
```python
optimizer = scitex.ai.optim.set(model, 'ranger', lr=0.001)
```

### New API
```python
optimizer = scitex.ai.optim.set_optimizer(model, 'ranger', lr=0.001)
```

## Removal Timeline
- Version 1.12.0: Deprecation warnings added
- Version 2.0.0: Vendored Ranger code will be removed
- Users must install pytorch-optimizer for Ranger support