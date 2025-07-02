#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-02 06:40:00 (ywatanabe)"
# File: ./mcp_servers/examples/gen_translation_demo.py
# ----------------------------------------

"""
Comprehensive demonstration of bidirectional translation with scitex-gen MCP server.

This example shows how the gen module translates between standard Python
and SciTeX patterns for general utilities.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Example 1: Data Normalization Patterns
print("=" * 70)
print("EXAMPLE 1: DATA NORMALIZATION PATTERNS")
print("=" * 70)

standard_normalization = """
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# Load experimental data
data = pd.read_csv('experimental_results.csv')
measurements = data[['measurement_1', 'measurement_2', 'measurement_3']].values

# Manual z-score normalization
mean_vals = np.mean(measurements, axis=0)
std_vals = np.std(measurements, axis=0)
measurements_zscore = (measurements - mean_vals) / std_vals

# Manual min-max normalization
min_vals = measurements.min(axis=0)
max_vals = measurements.max(axis=0)
measurements_scaled = (measurements - min_vals) / (max_vals - min_vals)

# Using sklearn
scaler = StandardScaler()
measurements_sklearn = scaler.fit_transform(measurements)

# Remove outliers manually
q1 = np.percentile(measurements, 25, axis=0)
q3 = np.percentile(measurements, 75, axis=0)
iqr = q3 - q1
lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr
measurements_clipped = np.clip(measurements, lower_bound, upper_bound)
"""

scitex_normalization = """
import scitex as stx

# Load experimental data
data = stx.io.load('./experimental_results.csv')
measurements = data[['measurement_1', 'measurement_2', 'measurement_3']].values

# Z-score normalization
measurements_zscore = stx.gen.to_z(measurements)

# Min-max normalization to [0, 1]
measurements_scaled = stx.gen.to_01(measurements)

# Clip outliers at 95th percentile
measurements_clipped = stx.gen.clip_perc(measurements, percentile=95)

# Remove bias
measurements_unbiased = stx.gen.unbias(measurements)

# Apply custom normalization range
measurements_custom = stx.gen.to_nan01(measurements)  # NaN-aware normalization
"""

print("STANDARD PYTHON:")
print(standard_normalization)
print("\nTRANSLATES TO SCITEX:")
print(scitex_normalization)

# Example 2: Caching and Performance
print("\n" + "=" * 70)
print("EXAMPLE 2: CACHING AND PERFORMANCE OPTIMIZATION")
print("=" * 70)

standard_caching = """
import functools
import time
from joblib import Memory

# Using functools LRU cache
@functools.lru_cache(maxsize=128)
def compute_correlation_matrix(data_hash):
    # Expensive computation
    time.sleep(0.1)  # Simulate computation
    data = load_data(data_hash)
    return np.corrcoef(data.T)

# Manual caching implementation
cache = {}
def compute_features(data_id):
    if data_id in cache:
        return cache[data_id]
    
    # Expensive feature computation
    result = expensive_feature_extraction(data_id)
    cache[data_id] = result
    return result

# Using joblib Memory
memory = Memory('cache_dir', verbose=0)

@memory.cache
def process_large_dataset(dataset_path):
    data = pd.read_csv(dataset_path)
    # Complex processing...
    return processed_data
"""

scitex_caching = """
import scitex as stx

# Simple caching decorator
@stx.gen.cache
def compute_correlation_matrix(data):
    # Expensive computation
    return np.corrcoef(data.T)

# Cache with custom parameters
@stx.decorators.cache_disk(cache_dir='./cache')
def compute_features(data_id):
    # Expensive feature computation
    return expensive_feature_extraction(data_id)

# Memory-efficient batch processing with caching
@stx.decorators.batch_fn(batch_size=1000)
@stx.gen.cache
def process_large_dataset(data_batch):
    # Complex processing...
    return processed_data
"""

print("STANDARD PYTHON:")
print(standard_caching)
print("\nTRANSLATES TO SCITEX:")
print(scitex_caching)

# Example 3: Experiment Lifecycle Management
print("\n" + "=" * 70)
print("EXAMPLE 3: EXPERIMENT LIFECYCLE MANAGEMENT")
print("=" * 70)

standard_experiment = """
import os
import sys
import json
import random
import numpy as np
from datetime import datetime
import logging

# Manual experiment setup
def setup_experiment(config_path):
    # Set random seeds
    random.seed(42)
    np.random.seed(42)
    
    # Load configuration
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Create output directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = f"experiments/{config['name']}_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"{output_dir}/experiment.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Track experiment metadata
    metadata = {
        'config': config,
        'timestamp': timestamp,
        'output_dir': output_dir,
        'random_seed': 42
    }
    
    return metadata

# Manual timing
start_time = datetime.now()
metadata = setup_experiment('config.json')

# Run experiment...
for epoch in range(100):
    epoch_start = datetime.now()
    # Training code...
    epoch_end = datetime.now()
    logging.info(f"Epoch {epoch}: {epoch_end - epoch_start}")

end_time = datetime.now()
logging.info(f"Total time: {end_time - start_time}")

# Save results
with open(f"{metadata['output_dir']}/results.json", 'w') as f:
    json.dump(results, f)
"""

scitex_experiment = """
import scitex as stx

# Automated experiment setup with reproducibility
config = stx.gen.start(
    description="Neural network training experiment",
    config_path='./config/experiment.yaml',
    verbose=True
)

# Automatic time tracking
ts = stx.gen.TimeStamper()
ts.stamp('Experiment initialized')

# Run experiment with automatic output management
for epoch in range(100):
    ts.stamp(f'Epoch {epoch} started')
    
    # Training code...
    metrics = train_one_epoch(model, data)
    
    # Automatic output saving with organization
    stx.io.save(metrics, f'./metrics/epoch_{epoch}.json', symlink_from_cwd=True)
    
    ts.stamp(f'Epoch {epoch} completed')

# Generate timing report
timing_df = ts.get_df()
stx.io.save(timing_df, './timing_analysis.csv', symlink_from_cwd=True)

# Close experiment with automatic cleanup
stx.gen.close()
"""

print("STANDARD PYTHON:")
print(standard_experiment)
print("\nTRANSLATES TO SCITEX:")
print(scitex_experiment)

# Example 4: Path and Environment Management
print("\n" + "=" * 70)
print("EXAMPLE 4: PATH AND ENVIRONMENT MANAGEMENT")
print("=" * 70)

standard_path = """
import os
import sys
from pathlib import Path

# Get current script directory
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# Add to Python path
sys.path.insert(0, project_root)

# Create output directories
output_base = os.path.join(project_root, 'output')
figures_dir = os.path.join(output_base, 'figures')
data_dir = os.path.join(output_base, 'data')

os.makedirs(figures_dir, exist_ok=True)
os.makedirs(data_dir, exist_ok=True)

# Platform-specific handling
if sys.platform == 'win32':
    cache_dir = os.path.join(os.environ['TEMP'], 'experiment_cache')
elif sys.platform == 'darwin':
    cache_dir = os.path.expanduser('~/Library/Caches/experiment')
else:  # Linux
    cache_dir = os.path.expanduser('~/.cache/experiment')

# Environment detection
is_cluster = 'SLURM_JOB_ID' in os.environ
is_debug = os.environ.get('DEBUG', '').lower() == 'true'
"""

scitex_path = """
import scitex as stx

# Automatic path resolution
current_dir = stx.gen.src(__file__)
project_root = stx.path.find_git_root(current_dir)

# Structured path creation with auto-organization
experiment_paths = stx.path.mk_spath(
    'neural_network_experiment',
    makedirs=True
)

# Platform-independent environment detection
if stx.gen.is_host('cluster'):
    cache_dir = './cluster_cache'
elif stx.gen.is_host('local'):
    cache_dir = './local_cache'

# Check execution environment
is_notebook = stx.gen.is_ipython()
is_script = stx.gen.is_script()

# Automatic directory creation handled by stx.io.save()
# No need for explicit makedirs calls
"""

print("STANDARD PYTHON:")
print(standard_path)
print("\nTRANSLATES TO SCITEX:")
print(scitex_path)

# Example 5: Array and Data Transformations
print("\n" + "=" * 70)
print("EXAMPLE 5: ARRAY AND DATA TRANSFORMATIONS")
print("=" * 70)

standard_transforms = """
import numpy as np

# Ensure even array length
data = np.random.randn(101)  # Odd length
if len(data) % 2 != 0:
    data = data[:-1]  # Remove last element

# Ensure odd array length
features = np.random.randn(100)  # Even length
if len(features) % 2 == 0:
    features = np.append(features, 0)  # Add zero

# Convert to ranks
values = np.array([3.2, 1.5, 4.8, 2.1, 3.9])
sorted_indices = np.argsort(values)
ranks = np.empty_like(sorted_indices)
ranks[sorted_indices] = np.arange(len(values))

# Title formatting
experiment_name = "Neural Network Training - Batch Size 32"
safe_filename = experiment_name.lower().replace(' ', '_').replace('-', '_')
safe_filename = ''.join(c for c in safe_filename if c.isalnum() or c == '_')
"""

scitex_transforms = """
import scitex as stx

# Ensure even array length
data = np.random.randn(101)  # Odd length
data = stx.gen.to_even(data)

# Ensure odd array length
features = np.random.randn(100)  # Even length
features = stx.gen.to_odd(features)

# Convert to ranks
values = np.array([3.2, 1.5, 4.8, 2.1, 3.9])
ranks = stx.gen.to_rank(values)

# Title formatting with safe path conversion
experiment_name = "Neural Network Training - Batch Size 32"
safe_filename = stx.gen.title2path(experiment_name)

# Advanced array operations
data_transposed = stx.gen.transpose(data)
info = stx.gen.var_info(data)  # Get variable information
"""

print("STANDARD PYTHON:")
print(standard_transforms)
print("\nTRANSLATES TO SCITEX:")
print(scitex_transforms)

# Summary
print("\n" + "=" * 70)
print("BIDIRECTIONAL TRANSLATION SUMMARY")
print("=" * 70)
print("""
The scitex-gen MCP server provides bidirectional translation for:

1. DATA NORMALIZATION
   - Manual calculations → stx.gen.to_z(), to_01(), clip_perc()
   - sklearn scalers → SciTeX normalization functions
   - Outlier handling → Integrated percentile clipping

2. CACHING & PERFORMANCE
   - functools.lru_cache → @stx.gen.cache
   - Manual cache dicts → Automatic caching
   - joblib Memory → Disk-based caching

3. EXPERIMENT MANAGEMENT
   - Manual setup → stx.gen.start()
   - Timestamp tracking → TimeStamper class
   - Manual cleanup → stx.gen.close()

4. PATH & ENVIRONMENT
   - os.path operations → stx.gen.src(), stx.path utilities
   - Platform checks → stx.gen.is_host()
   - Manual makedirs → Automatic with stx.io.save()

5. ARRAY TRANSFORMATIONS
   - Manual length adjustments → to_even(), to_odd()
   - Custom ranking → to_rank()
   - String formatting → title2path()

All translations are bidirectional - SciTeX code can be converted back
to standard Python when needed for compatibility.
""")

print("\nFor more examples, see the individual test files in mcp_servers/examples/")

# EOF