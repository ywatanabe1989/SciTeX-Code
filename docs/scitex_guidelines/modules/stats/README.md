# SciTeX Stats Module Documentation

## Overview

The `scitex.stats` module provides comprehensive statistical analysis tools for scientific computing. It includes descriptive statistics, hypothesis testing, correlation analysis, and multiple comparison corrections, with seamless integration for both NumPy arrays and PyTorch tensors.

## Key Features

- **Descriptive Statistics**: Comprehensive statistical summaries with NaN handling
- **Hypothesis Testing**: Parametric and non-parametric tests
- **Correlation Analysis**: Pearson, Spearman, and partial correlations
- **Multiple Comparisons**: Bonferroni and FDR corrections
- **Significance Formatting**: Automatic p-value to star conversion

## Core Functions

### P-value Formatting

#### `p2stars()`
Convert p-values to significance stars for publication-ready output.

```python
import scitex.stats

# Single p-value
p_val = 0.003
stars = scitex.stats.p2stars(p_val)
print(f"p = {p_val} {stars}")  # p = 0.003 **

# Multiple p-values
p_values = [0.0001, 0.01, 0.04, 0.06]
stars = [scitex.stats.p2stars(p) for p in p_values]
# Returns: ['***', '**', '*', '']
```

### Correlation Analysis

#### `calc_partial_corr()`
Calculate partial correlation, removing the effect of a confounding variable.

```python
# Partial correlation between X and Y, controlling for Z
import numpy as np
X = np.random.randn(100)
Y = X + np.random.randn(100) * 0.5
Z = X + Y + np.random.randn(100) * 0.5

# Regular correlation
corr_xy = np.corrcoef(X, Y)[0, 1]  # ~0.89

# Partial correlation (controlling for Z)
partial_corr = scitex.stats.calc_partial_corr(X, Y, Z)  # ~0.45
```

## Descriptive Statistics (desc submodule)

### `describe()`
Compute comprehensive descriptive statistics for data.

```python
import torch
import scitex.stats.desc

# Generate sample data
data = torch.randn(100, 50, 30)

# Get all statistics
stats = scitex.stats.desc.describe(data)
print(stats.keys())
# ['mean', 'std', 'var', 'min', 'max', 'q25', 'q50', 'q75', 
#  'kurtosis', 'skewness', 'n', 'missing']

# Dimension-specific statistics
stats_dim1 = scitex.stats.desc.describe(data, dim=1)
# Shape: varies by statistic, computed along dimension 1

# Handle missing values
data_with_nan = data.clone()
data_with_nan[data < -2] = float('nan')
stats_nan = scitex.stats.desc.describe(data_with_nan)
```

## Hypothesis Testing (tests submodule)

### `corr_test()`
Perform correlation testing with permutation-based p-values.

```python
import scitex.stats.tests

# Test correlation significance
x = torch.randn(100)
y = 0.5 * x + torch.randn(100) * 0.5

result = scitex.stats.tests.corr_test(x, y, method='pearson')
print(result)
# {
#   'correlation': 0.71,
#   'p_value': 0.001,
#   'confidence_interval': (0.58, 0.81),
#   'effect_size': 'large',
#   'n': 100,
#   'significance': '***'
# }

# Spearman correlation for non-linear relationships
result_spearman = scitex.stats.tests.corr_test(x, y, method='spearman')
```

### `brunner_munzel_test()`
Non-parametric test for comparing two independent samples.

```python
# Compare two groups
group1 = torch.randn(50) + 0.5
group2 = torch.randn(60)

result = scitex.stats.tests.brunner_munzel_test(group1, group2)
print(result)
# {
#   'statistic': 2.34,
#   'p_value': 0.021,
#   'df': 89.5,
#   'effect_size': 0.65,
#   'significance': '*'
# }
```

## Multiple Comparisons (multiple submodule)

### `bonferroni_correction()`
Apply Bonferroni correction for multiple hypothesis testing.

```python
import scitex.stats.multiple

# Multiple p-values from different tests
p_values = [0.01, 0.03, 0.04, 0.002, 0.15]

# Apply Bonferroni correction
corrected_p = scitex.stats.multiple.bonferroni_correction(p_values)
print(corrected_p)
# [0.05, 0.15, 0.20, 0.01, 0.75]

# With significance threshold
significant = corrected_p < 0.05
# [False, False, False, True, False]
```

### `fdr_correction()`
Apply False Discovery Rate correction (Benjamini-Hochberg).

```python
# FDR correction for multiple comparisons
p_values = np.array([0.001, 0.008, 0.039, 0.041, 0.042])

corrected_p, rejected = scitex.stats.multiple.fdr_correction(p_values, alpha=0.05)
print(f"FDR corrected p-values: {corrected_p}")
print(f"Significant tests: {rejected}")

# For DataFrames
import pandas as pd
df = pd.DataFrame({
    'gene': ['A', 'B', 'C', 'D'],
    'p_value': [0.001, 0.01, 0.03, 0.1]
})

df_corrected = scitex.stats.multiple.fdr_correction(df)
# Adds 'p_value_fdr' and 'significance_fdr' columns
```

## Common Workflows

### 1. Complete Statistical Analysis
```python
import scitex.stats
import torch

# Generate data
control = torch.randn(100) 
treatment = torch.randn(100) + 0.3

# Descriptive statistics
stats_control = scitex.stats.desc.describe(control)
stats_treatment = scitex.stats.desc.describe(treatment)

print(f"Control: mean={stats_control['mean']:.3f}, std={stats_control['std']:.3f}")
print(f"Treatment: mean={stats_treatment['mean']:.3f}, std={stats_treatment['std']:.3f}")

# Statistical test
result = scitex.stats.tests.brunner_munzel_test(control, treatment)
print(f"p-value: {result['p_value']:.4f} {result['significance']}")
```

### 2. Multiple Group Comparisons
```python
# Compare multiple groups with correction
groups = {
    'A': torch.randn(50),
    'B': torch.randn(50) + 0.2,
    'C': torch.randn(50) + 0.5,
    'D': torch.randn(50) - 0.1
}

# Pairwise comparisons
p_values = []
comparisons = []

for i, (name1, data1) in enumerate(groups.items()):
    for name2, data2 in list(groups.items())[i+1:]:
        result = scitex.stats.tests.brunner_munzel_test(data1, data2)
        p_values.append(result['p_value'])
        comparisons.append(f"{name1} vs {name2}")

# Apply FDR correction
corrected_p = scitex.stats.multiple.fdr_correction(p_values)

# Display results
for comp, p_orig, p_corr in zip(comparisons, p_values, corrected_p):
    stars = scitex.stats.p2stars(p_corr)
    print(f"{comp}: p={p_orig:.4f}, p_fdr={p_corr:.4f} {stars}")
```

### 3. Correlation Matrix with Significance
```python
# Create correlation matrix with significance testing
import pandas as pd

# Multiple variables
data = {
    'var1': torch.randn(100),
    'var2': torch.randn(100),
    'var3': torch.randn(100),
    'var4': torch.randn(100)
}
data['var2'] += 0.5 * data['var1']  # Add correlation
data['var3'] += 0.3 * data['var1'] + 0.4 * data['var2']

# Compute correlation matrix
n_vars = len(data)
corr_matrix = torch.zeros(n_vars, n_vars)
p_matrix = torch.ones(n_vars, n_vars)

var_names = list(data.keys())
for i, var1 in enumerate(var_names):
    for j, var2 in enumerate(var_names):
        if i != j:
            result = scitex.stats.tests.corr_test(data[var1], data[var2])
            corr_matrix[i, j] = result['correlation']
            p_matrix[i, j] = result['p_value']
        else:
            corr_matrix[i, j] = 1.0

# Apply FDR correction to upper triangle
upper_tri_idx = torch.triu_indices(n_vars, n_vars, offset=1)
p_values_upper = p_matrix[upper_tri_idx[0], upper_tri_idx[1]]
p_corrected = scitex.stats.multiple.fdr_correction(p_values_upper.numpy())

# Create significance matrix
sig_matrix = pd.DataFrame('', index=var_names, columns=var_names)
for (i, j), p in zip(zip(upper_tri_idx[0], upper_tri_idx[1]), p_corrected):
    sig_matrix.iloc[i, j] = scitex.stats.p2stars(p)
    sig_matrix.iloc[j, i] = sig_matrix.iloc[i, j]  # Symmetric
```

## Integration with Other SciTeX Modules

### With scitex.plt for Visualization
```python
# Statistical plotting
fig, axes = scitex.plt.subplots(1, 2)

# Distribution comparison
axes[0].hist(control.numpy(), alpha=0.5, label='Control')
axes[0].hist(treatment.numpy(), alpha=0.5, label='Treatment')
axes[0].set_title(f"p = {result['p_value']:.4f} {result['significance']}")
axes[0].legend()

# Correlation plot
axes[1].scatter(data['var1'], data['var2'])
axes[1].set_xlabel('Variable 1')
axes[1].set_ylabel('Variable 2')
corr_result = scitex.stats.tests.corr_test(data['var1'], data['var2'])
axes[1].set_title(f"r = {corr_result['correlation']:.3f} {corr_result['significance']}")

fig.save("statistical_analysis.png")
```

### With scitex.io for Results Storage
```python
# Save statistical results
results = {
    'descriptive': {
        'control': stats_control,
        'treatment': stats_treatment
    },
    'hypothesis_test': result,
    'correlation_matrix': corr_matrix.numpy(),
    'p_values': p_matrix.numpy(),
    'metadata': {
        'n_samples': 100,
        'correction_method': 'fdr',
        'alpha': 0.05
    }
}

scitex.io.save(results, "statistical_results.pkl")
```

## Best Practices

1. **Check Data Distribution**: Use `describe()` before applying tests
2. **Choose Appropriate Tests**: Use non-parametric tests for non-normal data
3. **Handle Missing Data**: Stats functions handle NaN values automatically
4. **Multiple Comparisons**: Always apply correction when doing multiple tests
5. **Report Effect Sizes**: Include effect sizes along with p-values

## Troubleshooting

### Common Issues

**Issue**: Different results between NumPy and PyTorch inputs
```python
# Solution: Ensure consistent data types
data_np = np.array([1, 2, 3, 4, 5])
data_pt = torch.tensor([1, 2, 3, 4, 5], dtype=torch.float32)
```

**Issue**: Memory error with large permutation tests
```python
# Solution: Reduce number of permutations
result = scitex.stats.tests.corr_test(x, y, n_permutations=1000)  # Default is 10000
```

**Issue**: FDR correction returns all non-significant
```python
# Solution: Check if p-values are already too high
# or consider less conservative correction
corrected_p = scitex.stats.multiple.fdr_correction(p_values, alpha=0.1)  # More liberal
```

## API Reference

For detailed API documentation, see the individual function docstrings or the Sphinx-generated documentation.

## See Also

- `scitex.plt` - For statistical visualization
- `scitex.pd` - For DataFrame operations with statistical results
- `scipy.stats` - For additional statistical tests