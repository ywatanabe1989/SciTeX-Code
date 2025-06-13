# SciTeX gen Module - Detailed Reference

The `gen` module is the cornerstone of SciTeX, providing experiment management, environment setup, and reproducibility features.

## Core Philosophy

The gen module follows these principles:
1. **Automatic organization**: Creates timestamped directories for outputs
2. **Complete logging**: Captures all stdout/stderr to files
3. **Reproducibility**: Sets random seeds across all libraries
4. **Configuration management**: Provides a unified config object
5. **Clean lifecycle**: Proper startup and shutdown procedures

## Primary Functions

### scitex.gen.start()

```python
CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(
    sys,                    # Python sys module
    plt,                    # Matplotlib pyplot module
    sdir="./",             # Save directory
    verbose=True,          # Print startup information
    random_seed=None,      # Random seed for reproducibility
    matplotlib_backend="Agg",  # Matplotlib backend
    os_env_vars=None,      # Environment variables to set
    ID=None,               # Custom experiment ID
    **kwargs               # Additional config parameters
)
```

**What it does:**
1. Creates a unique experiment ID and timestamp
2. Sets up save directory structure:
   ```
   sdir/
   └── YYYY-MM-DD-HH-MM-SS_ID/
       ├── log/
       ├── fig/
       └── data/
   ```
3. Redirects stdout/stderr to both console and log files
4. Configures matplotlib for non-interactive use
5. Sets random seeds for numpy, random, torch (if available)
6. Returns configuration objects for experiment tracking

**Returns:**
- `CONFIG`: DotDict with all configuration parameters
- `sys.stdout`: Wrapped stdout for logging
- `sys.stderr`: Wrapped stderr for logging
- `plt`: Configured matplotlib.pyplot
- `CC`: ClosedCaption object for structured logging

### scitex.gen.close()

```python
scitex.gen.close(CONFIG, verbose=True)
```

**What it does:**
1. Restores original stdout/stderr
2. Saves final logs
3. Creates symlinks for easy access to latest results
4. Prints summary of saved files
5. Cleans up resources

## Utility Functions

### scitex.gen.gen_ID()

```python
unique_id = scitex.gen.gen_ID(n=8)
```

Generates a random alphanumeric ID for experiment tracking.

**Parameters:**
- `n`: Length of ID (default: 8)

**Example:**
```python
exp_id = scitex.gen.gen_ID(12)  # e.g., "A3B9X7K2L5M8"
```

### scitex.gen.gen_timestamp()

```python
timestamp = scitex.gen.gen_timestamp()
```

Generates a formatted timestamp string.

**Returns:**
- String in format: "YYYY-MM-DD-HH-MM-SS"

### scitex.gen.title2path()

```python
safe_path = scitex.gen.title2path("My Experiment: Test #1")
```

Converts a title string to a safe filename.

**What it does:**
- Replaces spaces with underscores
- Removes special characters
- Converts to lowercase
- Ensures valid filename

**Example:**
```python
title = "Results: α=0.01, β=0.5"
path = scitex.gen.title2path(title)  # "results_alpha_0_01_beta_0_5"
```

## Internal Classes

### TimeStamper

Used internally for creating timestamped log entries.

```python
ts = scitex.gen.TimeStamper()
ts.print("Processing started")  # [2025-05-31 10:30:45] Processing started
```

### ClosedCaption (CC)

Provides structured logging with sections.

```python
CC.set_section("Data Loading")
CC.print("Loading dataset...")
CC.set_section("Processing")
CC.print("Applying filters...")
```

## Directory Structure

When you call `scitex.gen.start()`, it creates:

```
./
└── sdir/
    └── YYYY-MM-DD-HH-MM-SS_XXXXXXXX/
        ├── log/
        │   ├── stdout.log      # Captured stdout
        │   ├── stderr.log      # Captured stderr
        │   └── config.yaml     # Saved configuration
        ├── fig/                # For plots (via scitex.io.save)
        ├── data/               # For data files
        └── _RUNNING            # Marker file (removed on close)
```

## Best Practices

### 1. Always use start/close pattern

```python
import sys
import matplotlib.pyplot as plt
import scitex

# Start
CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(sys, plt)

try:
    # Your experiment code
    data = process_data()
    results = run_analysis(data)
    scitex.io.save(results, "results.pkl")
    
finally:
    # Always close, even if error occurs
    scitex.gen.close(CONFIG)
```

### 2. Use CONFIG for experiment parameters

```python
CONFIG, *_ = scitex.gen.start(
    sys, plt,
    learning_rate=0.001,
    batch_size=32,
    n_epochs=100
)

# Access parameters
print(f"Training with LR: {CONFIG.learning_rate}")
```

### 3. Leverage automatic paths

```python
# Don't hardcode paths
# Bad:
save_path = "./outputs/2025-05-31/results.csv"

# Good:
save_path = f"{CONFIG.sdir}/results.csv"
# Or even better:
scitex.io.save(results, "results.csv")  # Uses CONFIG.sdir automatically
```

### 4. Set random seeds for reproducibility

```python
CONFIG, *_ = scitex.gen.start(sys, plt, random_seed=42)
# Now numpy, random, torch all use consistent seeds
```

## Integration with Other Modules

The gen module integrates seamlessly with:

- **io module**: Uses CONFIG.sdir for saving files
- **plt module**: Pre-configures matplotlib settings
- **All modules**: Provides logging infrastructure

## Common Patterns

### Running multiple experiments

```python
for seed in [42, 123, 456]:
    CONFIG, *_ = scitex.gen.start(sys, plt, 
                                sdir=f"./results/seed_{seed}",
                                random_seed=seed)
    try:
        results = run_experiment()
        scitex.io.save(results, "results.pkl")
    finally:
        scitex.gen.close(CONFIG)
```

### Distributed computing

```python
# Each job gets unique ID
job_id = os.environ.get('SLURM_JOB_ID', 'local')
CONFIG, *_ = scitex.gen.start(sys, plt, 
                           sdir=f"./results/job_{job_id}",
                           ID=job_id)
```

### Debug mode

```python
# Verbose mode for debugging
CONFIG, *_ = scitex.gen.start(sys, plt, verbose=True)

# Quiet mode for production
CONFIG, *_ = scitex.gen.start(sys, plt, verbose=False)
```

## Troubleshooting

### Issue: "Directory already exists"
This happens if a previous run didn't close properly.
```python
# Force new directory with timestamp
CONFIG, *_ = scitex.gen.start(sys, plt, ID=scitex.gen.gen_ID())
```

### Issue: "Can't see print statements"
Stdout is being captured. Use verbose mode or check log files:
```python
# Option 1: Verbose mode
CONFIG, *_ = scitex.gen.start(sys, plt, verbose=True)

# Option 2: Check logs
cat sdir/*/log/stdout.log
```

### Issue: "Random results not reproducible"
Ensure you're setting seeds before any random operations:
```python
CONFIG, *_ = scitex.gen.start(sys, plt, random_seed=42)
# NOW import other modules that might use randomness
import sklearn
import torch
```

## Advanced Usage

### Custom configuration

```python
CONFIG, *_ = scitex.gen.start(
    sys, plt,
    # Experiment parameters
    model_type="resnet50",
    dataset="imagenet",
    # Hardware settings
    device="cuda:0",
    num_workers=8,
    # Custom paths
    data_root="/path/to/data",
    checkpoint_dir="./checkpoints"
)

# All accessible via CONFIG
model = load_model(CONFIG.model_type)
model.to(CONFIG.device)
```

### Conditional setup

```python
# Different settings for debugging vs production
debug = os.environ.get('DEBUG', False)

CONFIG, *_ = scitex.gen.start(
    sys, plt,
    sdir="./debug" if debug else "./results",
    verbose=debug,
    random_seed=42 if debug else None
)
```

## Summary

The gen module provides the foundation for organized, reproducible research code. By handling the boilerplate of experiment setup, logging, and organization, it lets you focus on your actual research while maintaining best practices automatically.