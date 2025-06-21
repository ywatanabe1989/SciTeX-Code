#!/usr/bin/env python3
"""
SciTeX v2.0.0 Feature Showcase
==============================

This example demonstrates the key features of SciTeX v2.0.0,
showcasing why it's the go-to package for scientific Python workflows.
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scitex

# =============================================================================
# 1. REPRODUCIBLE EXPERIMENT SETUP
# =============================================================================
print("1. Setting up reproducible experiment environment...")

# Start with automatic seed management and output logging
CONFIG, sys.stdout, sys.stderr, plt, CC = scitex.gen.start(
    sys, plt,
    sdir="./scitex_v2_showcase_out",
    seed=42,  # Ensures reproducibility across numpy, torch, random
    verbose=True
)

print(f"   ✓ Experiment ID: {CONFIG.id}")
print(f"   ✓ Output directory: {CONFIG.sdir}")
print(f"   ✓ Random seed fixed: {CONFIG.seed}")

# =============================================================================
# 2. UNIFIED I/O INTERFACE
# =============================================================================
print("\n2. Demonstrating unified I/O interface...")

# Create sample data in various formats
data_dict = {"x": np.arange(100), "y": np.sin(np.arange(100) * 0.1)}
data_df = pd.DataFrame(data_dict)
data_array = np.column_stack([data_dict["x"], data_dict["y"]])

# Save in different formats - all with the same interface!
scitex.io.save(data_dict, "data.json")
scitex.io.save(data_df, "data.csv")
scitex.io.save(data_array, "data.npy")
scitex.io.save({"dict": data_dict, "df": data_df}, "data.pkl")

print("   ✓ Saved data in JSON, CSV, NPY, and PKL formats")

# Load them back - format detected automatically
loaded_json = scitex.io.load("data.json")
loaded_csv = scitex.io.load("data.csv")
loaded_npy = scitex.io.load("data.npy")
loaded_pkl = scitex.io.load("data.pkl")

print("   ✓ Loaded all formats with single load() function")

# =============================================================================
# 3. ENHANCED PLOTTING WITH DATA TRACKING
# =============================================================================
print("\n3. Creating plots with automatic data export...")

# Create a multi-panel figure
fig, axes = scitex.plt.subplots(2, 2, figsize=(10, 8))

# Panel 1: Time series
ax = axes[0, 0]
t = np.linspace(0, 4*np.pi, 1000)
y1 = np.sin(t) + 0.1 * np.random.randn(len(t))
y2 = np.cos(t) + 0.1 * np.random.randn(len(t))
ax.plot(t, y1, label="sin(t) + noise", alpha=0.8)
ax.plot(t, y2, label="cos(t) + noise", alpha=0.8)
ax.set_xyt("Time (s)", "Amplitude", "Noisy Trigonometric Functions")
ax.legend()

# Panel 2: Scatter plot with statistics
ax = axes[0, 1]
x = np.random.randn(100)
y = 2 * x + 1 + np.random.randn(100) * 0.5
ax.scatter(x, y, alpha=0.6)
result = scitex.stats.corr_test(x, y)
ax.set_xyt("X", "Y", f"Correlation: r={result['r']:.3f}, p={result['p']:.4f}")

# Panel 3: Histogram with KDE
ax = axes[1, 0]
data = np.concatenate([np.random.normal(0, 1, 500), np.random.normal(3, 0.5, 300)])
ax.hist(data, bins=30, density=True, alpha=0.7, label="Histogram")
# Add KDE overlay
from scipy import stats as scipy_stats
kde = scipy_stats.gaussian_kde(data)
x_kde = np.linspace(data.min(), data.max(), 200)
ax.plot(x_kde, kde(x_kde), 'r-', lw=2, label="KDE")
ax.set_xyt("Value", "Density", "Bimodal Distribution")
ax.legend()

# Panel 4: Heatmap
ax = axes[1, 1]
matrix = np.random.randn(10, 10)
im = ax.imshow(matrix, cmap='viridis', aspect='auto')
plt.colorbar(im, ax=ax)
ax.set_xyt("Column", "Row", "Random Heatmap")

# Save figure - this also exports the data!
scitex.io.save(fig, "showcase_plots.png", dpi=150)
print("   ✓ Saved figure and automatically exported plot data to CSV")

# =============================================================================
# 4. SIGNAL PROCESSING CAPABILITIES
# =============================================================================
print("\n4. Demonstrating signal processing tools...")

# Generate a complex signal
fs = 1000  # Sampling frequency
t = np.arange(0, 2, 1/fs)
signal = (
    np.sin(2 * np.pi * 5 * t) +      # 5 Hz component
    np.sin(2 * np.pi * 50 * t) * 0.5 + # 50 Hz component
    np.random.randn(len(t)) * 0.2      # Noise
)

# Apply bandpass filter
filtered = scitex.dsp.bandpass(signal, low=3, high=10, fs=fs)

# Compute power spectral density
freqs, psd = scitex.dsp.psd(signal, fs=fs)

# Phase-amplitude coupling example
phase_signal = filtered
amplitude_signal = scitex.dsp.bandpass(signal, low=40, high=60, fs=fs)
pac_value = scitex.dsp.pac(phase_signal, amplitude_signal, fs=fs)

print(f"   ✓ Filtered signal (3-10 Hz bandpass)")
print(f"   ✓ Computed PSD")
print(f"   ✓ Phase-amplitude coupling: {pac_value:.3f}")

# =============================================================================
# 5. MACHINE LEARNING INTEGRATION
# =============================================================================
print("\n5. Machine learning utilities...")

# Generate classification dataset
from sklearn.datasets import make_classification
X, y = make_classification(n_samples=1000, n_features=20, n_informative=15, 
                          n_redundant=5, n_classes=3, random_state=42)

# Split data
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Create a simple classifier
from sklearn.ensemble import RandomForestClassifier
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Generate classification report
from scitex.ai import ClassificationReporter
reporter = ClassificationReporter()
report = reporter.report(y_test, clf.predict(X_test))
print("   ✓ Generated classification report")

# =============================================================================
# 6. PANDAS ENHANCEMENTS
# =============================================================================
print("\n6. Pandas utilities...")

# Create sample dataframe
df = pd.DataFrame({
    'A': np.random.randn(100),
    'B': np.random.randn(100) * 2 + 1,
    'C': np.random.choice(['X', 'Y', 'Z'], 100),
    'D': np.random.randint(0, 10, 100)
})

# Round numeric columns
df_rounded = scitex.pd.round(df, 3)

# Convert to numeric where possible
df_numeric = scitex.pd.to_numeric(df)

# Advanced slicing
subset = scitex.pd.slice(df, rows=slice(0, 50), cols=['A', 'B'])

print("   ✓ Rounded numeric columns to 3 decimal places")
print("   ✓ Converted columns to numeric types")
print("   ✓ Created subset with advanced slicing")

# =============================================================================
# 7. STRING AND PATH UTILITIES
# =============================================================================
print("\n7. String and path utilities...")

# Colored terminal output
scitex.str.printc("   ✓ This is green!", c="green")
scitex.str.printc("   ⚠ This is yellow!", c="yellow")
scitex.str.printc("   ✗ This is red!", c="red")

# Path utilities
latest_file = scitex.path.find_latest("*.png")
print(f"   ✓ Latest PNG file: {latest_file}")

# Title to safe filename
safe_name = scitex.gen.title2path("My Experiment: Test #1 @ 2024")
print(f"   ✓ Safe filename: {safe_name}")

# =============================================================================
# 8. DECORATORS FOR COMMON PATTERNS
# =============================================================================
print("\n8. Function decorators...")

@scitex.decorators.numpy_fn
def process_data(x, y):
    """This function accepts lists, arrays, tensors - returns numpy array"""
    return x + y

@scitex.decorators.timeout(1.0)
def slow_function():
    """This will timeout after 1 second"""
    import time
    time.sleep(0.5)
    return "Completed!"

@scitex.decorators.cache_disk
def expensive_computation(n):
    """Results are cached to disk"""
    return sum(i**2 for i in range(n))

result1 = process_data([1, 2, 3], [4, 5, 6])
result2 = slow_function()
result3 = expensive_computation(1000000)

print("   ✓ Numpy decorator: auto-converts inputs")
print("   ✓ Timeout decorator: prevents hanging")
print("   ✓ Cache decorator: speeds up repeated calls")

# =============================================================================
# 9. CONFIGURATION MANAGEMENT
# =============================================================================
print("\n9. Configuration management...")

# Load all YAML files from config directory
try:
    all_configs = scitex.io.load_configs("./config")
    print("   ✓ Loaded configuration files")
except:
    # Create sample config
    sample_config = {
        "experiment": {
            "name": "SciTeX Demo",
            "version": "2.0.0",
            "parameters": {
                "learning_rate": 0.001,
                "batch_size": 32,
                "epochs": 100
            }
        }
    }
    scitex.io.save(sample_config, "config.yaml")
    print("   ✓ Created sample configuration")

# =============================================================================
# 10. CLEANUP AND SUMMARY
# =============================================================================
print("\n10. Experiment complete!")

# Show what was created
import os
output_files = os.listdir(CONFIG.sdir)
print(f"\nCreated {len(output_files)} output files:")
for f in sorted(output_files)[:10]:  # Show first 10
    print(f"   - {f}")
if len(output_files) > 10:
    print(f"   ... and {len(output_files) - 10} more")

# Close and clean up
scitex.gen.close(CONFIG)

print("\n" + "="*60)
print("SciTeX v2.0.0 - Making Scientific Python Lazy (in a good way!)")
print("Install: pip install scitex")
print("Docs: https://scitex.readthedocs.io")
print("="*60)