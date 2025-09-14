<!-- ---
!-- Timestamp: 2025-09-14 11:21:57
!-- Author: ywatanabe
!-- File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/rng/README.md
!-- --- -->

# SciTeX RNG Module

Simple, robust random state management for reproducible scientific computing.

## Installation

```bash
pip install scitex
```

## Quick Start

### Basic Usage - Unified random seed fixation for libraries

**Supported Libaries**: `os`, `hash`, `python-builtin`, `numpy`, `sklearn`, `torch`, `tensorflow`, `jax`

```python
import scitex as stx
import random
import numpy as np
import torch
import tensorflow as tf

# Initialize once - fixes everything!
rng = stx.rng.RandomStateManager(seed=42)

# Python random - automatically fixed
python_val = random.random()  # Reproducible!

# NumPy - both old and new API fixed
np_old = np.random.rand(10)  # Old API - reproducible
np_new = rng.get_np_generator("data").random(10)  # Get named numpy generator

# PyTorch - CPU and CUDA fixed
torch_tensor = torch.randn(5, 5)  # Reproducible
if torch.cuda.is_available():
    cuda_tensor = torch.randn(5, 5).cuda()  # CUDA also reproducible!

# TensorFlow - all operations fixed
tf_tensor = tf.random.normal([5, 5])  # Reproducible

# All libraries stay synchronized and reproducible!
```

### Reproducibility verification

``` python
# --------------------
# Verify data is consistent with the previous run based on cached hash
# --------------------
rng.verify(data, "my_data")

# When verifification succeeeds:
# ✓ Reproducibility verified for 'my_data'

# When verification fails:
# ⚠️ Reproducibility broken for my_data'!
#    Expected: a3b5c7d9...
#    Got:      f1e2d3c4...
# ValueError: Reproducibility verification failed  # Stops execution

# --------------------
# How to clear cache
# --------------------
rng.clear_cache("my_data")  # Clear specific
# rng.clear_cache(["test1", "test2"])  # Multiple entries
# rng.clear_cache("experiment_*")  # Clear pattern
# rng.clear_cache()  # Clear all cache

# --------------------
# Working from terminal
# --------------------
# $ cat $HOME/.scitex/rng/my_data.json # {"name": "my_data", "hash": "a3b5c7d9...", "seed": 42}
# $ rm $HOME/.scitex/rng/my_data.json`
```

### Working with Session

```python
import sys
import scitex as stx

# Session.start returns RNG, fixing random seeds of the supported libraries automatically
CONFIG, stdout, stderr, plt, CC, rng = stx.session.start(
    sys=sys,
    seed=42
)

# Use immediately
data = rng.get_np_generator("data").random(1000)
model = rng.get_np_generator("model").normal(size=(10, 10))
```

<details>
<summary>Advanced Usage</summary>

### Checkpointing

Save and restore exact random states:

```python
# Save state
checkpoint = rng.checkpoint("before_training")

# Do work
train_model()

# Restore exact state
rng.restore(checkpoint)
```

### Temporary Seeds

Use different seed temporarily without affecting main flow:

```python
with rng.temporary_seed(999):
    debug_data = generate_debug()  # Different seed
# Main seed continues here
```

</details>

<details>
<summary>Library-Specific Usage</summary>

### NumPy
```python
# Get named generator
gen = rng.get_np_generator("data")
values = gen.random(100)
indices = gen.permutation(1000)
```

### Scikit-learn
```python
# Option 1: Let sklearn use NumPy's fixed seed (automatic)
# When random_state=None (default), sklearn uses NumPy's global state
# which is already fixed by RandomStateManager!
X_train, X_test = train_test_split(X, y)  # Uses fixed NumPy seed

# Option 2: Explicit random state for critical operations
# Use this for important reproducibility requirements
from sklearn.ensemble import RandomForestClassifier

random_state = rng.get_sklearn_random_state("model")
clf = RandomForestClassifier(random_state=random_state)
```

**Important**: Scikit-learn doesn't have a global seed setting. It uses:
- `random_state=None` (default) → Uses NumPy's global state (which we fix!)
- `random_state=int` → Uses that specific seed
- That's why we provide `get_sklearn_random_state()` for explicit control

### PyTorch
```python
# Get named generator
gen = rng.get_torch_generator("model")
tensor = torch.randn(5, 5, generator=gen)

# Or use global PyTorch state (already fixed)
tensor = torch.randn(5, 5)  # Uses fixed global seed
```

### TensorFlow, JAX
```python
# These use their global states (already fixed)
tf_tensor = tf.random.normal([5, 5])  # TensorFlow
jax_array = jax.random.normal(key, shape=(5, 5))  # JAX
```

</details>

<details>
<summary>Technical Details</summary>

### Automatic Seed Fixing

When you create a RandomStateManager, it automatically:

1. **OS Level**: Sets `PYTHONHASHSEED` environment variable
2. **Python**: Calls `random.seed()` for built-in random module
3. **NumPy**: Sets both `np.random.seed()` and creates `default_rng()`
4. **PyTorch**: 
   - Sets `torch.manual_seed()`
   - Sets `torch.cuda.manual_seed_all()` if CUDA available
   - Enables `torch.backends.cudnn.deterministic = True`
   - Disables `torch.backends.cudnn.benchmark`
5. **TensorFlow**: Sets `tf.random.set_seed()`
6. **JAX**: Creates `jax.random.PRNGKey()`

### Other Technical Details

- **Independent generators** - Each name gets deterministic seed derived from master seed using MD5 hashing
- **Cache location** - `~/.scitex/rng/` for verification hashes and checkpoints
- **Hash algorithm** - SHA256 for verification, MD5 for name-to-seed mapping
- **No configuration needed** - Automatically detects which libraries are installed

</details>

## Contact

yusuke.watanabe@scitex.ai

<!-- EOF -->