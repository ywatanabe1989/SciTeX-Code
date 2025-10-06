<!-- ---
!-- Timestamp: 2025-10-01 04:31:10
!-- Author: ywatanabe
!-- File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/stats/ARCHITECTURE.md
!-- --- -->

# SciTeX Stats Module Architecture

## Overview
This document describes the proposed reorganization of the `scitex.stats` module for improved clarity, maintainability, and scientific workflow alignment.

## Design Principles

1. **Scientific Workflow Alignment**: Structure follows typical statistical analysis workflow
2. **Clear Separation of Concerns**: Descriptive vs. inferential vs. utilities
3. **Consistent API**: All functions return standardized formats (dict/DataFrame)
4. **No Backward Compatibility**: Clean slate for better architecture

## Proposed Structure

```
scitex/stats/
├── __init__.py                      # Main entry point with key exports
├── descriptive/                     # Descriptive statistics
│   ├── __init__.py
│   ├── _central.py                  # mean, median, mode, trim_mean
│   ├── _dispersion.py               # std, var, sem, iqr, mad
│   ├── _distribution.py             # skew, kurtosis, describe
│   ├── _circular.py                 # circular statistics
│   └── _missing.py                  # nan, real (NaN handling)
│
├── tests/                           # Hypothesis tests (all with test_ prefix)
│   ├── __init__.py
│   ├── parametric/                  # Parametric tests
│   │   ├── __init__.py
│   │   ├── _test_ttest.py           # test_ttest_ind, test_ttest_rel, test_ttest_1samp
│   │   ├── _test_anova.py           # test_anova, test_anova_rm
│   │   └── _test_correlation.py     # test_pearson, test_corr
│   │
│   ├── nonparametric/               # Non-parametric tests
│   │   ├── __init__.py
│   │   ├── _test_mann_whitney.py    # test_mannwhitneyu
│   │   ├── _test_wilcoxon.py        # test_wilcoxon
│   │   ├── _test_kruskal.py         # test_kruskal
│   │   ├── _test_brunner_munzel.py  # test_brunner_munzel, test_bm
│   │   └── _test_spearman.py        # test_spearman, test_corr_spearman
│   │
│   ├── categorical/                 # Tests for categorical data
│   │   ├── __init__.py
│   │   ├── _test_chi2.py            # test_chi2_contingency, test_chisquare
│   │   └── _test_fisher.py          # test_fisher_exact
│   │
│   ├── normality/                   # Normality tests
│   │   ├── __init__.py
│   │   ├── _test_shapiro.py         # test_shapiro
│   │   └── _test_kstest.py          # test_kstest
│   │
│   ├── outliers/                    # Outlier detection tests
│   │   ├── __init__.py
│   │   ├── _test_grubbs.py          # test_grubbs, test_smirnov_grubbs
│   │   └── _test_dixon.py           # test_dixon
│   │
│   └── multivariate/                # Multivariate tests
│       ├── __init__.py
│       ├── _test_partial_corr.py    # test_partial_corr
│       └── _test_multivariate.py    # test_corr_multi, test_nocorrelation
│
├── correct/                         # Multiple comparison corrections (correct_ prefix)
│   ├── __init__.py
│   ├── _correct_bonferroni.py       # correct_bonferroni
│   ├── _correct_fdr.py              # correct_fdr (Benjamini-Hochberg)
│   ├── _correct_holm.py             # correct_holm (Holm-Bonferroni)
│   └── _correct_multicompair.py     # correct_multicompair (pairwise framework)
│
├── utils/                           # Utility functions
│   ├── __init__.py
│   ├── _validators.py               # StatisticalValidator
│   ├── _effect_size.py              # EffectSizeCalculator
│   ├── _power.py                    # Statistical power analysis
│   ├── _formatters.py               # p2stars, result formatting
│   ├── _normalizers.py              # Output format normalization
│   ├── _distributions.py            # norm, t, chi2, nct distributions
│   └── _diagnostics.py              # probplot, Q-Q plots
│
└── ARCHITECTURE.md                  # This file
```

## Module Details

### 1. `descriptive/` - Descriptive Statistics

**Purpose**: Compute summary statistics for data exploration

**Modules**:
- `_central.py`: Measures of central tendency
  - `mean()`, `median()`, `mode()`, `trim_mean()`

- `_dispersion.py`: Measures of variability
  - `std()`, `var()`, `sem()`, `iqr()`, `mad()`

- `_distribution.py`: Distribution shape
  - `skewness()`, `kurtosis()`, `describe()`

- `_circular.py`: Circular statistics
  - `circular_mean()`, `circular_std()`, `rayleigh_test()`

- `_missing.py`: Missing data handling
  - `nan()`: Count/identify NaN values
  - `real()`: Extract non-NaN values

**Output Format**: Dictionary or DataFrame with standardized keys

### 2. `tests/` - Hypothesis Testing

**Purpose**: Statistical hypothesis tests organized by type

**Example Usage**:
```python
import scitex as stx
import pandas as pd

# Single test - returns dict
result = stx.stats.tests.parametric.test_ttest_ind(
    group1, group2,
    var_x="Control", var_y="Treatment"
)
print(result)
# Output:
# {
#     'test_method': 'Independent t-test',
#     'statistic_name': 't',
#     'statistic': 2.45,
#     'alternative': 'two-sided',
#     'n_samples': 100,
#     'n_x': 50,
#     'n_y': 50,
#     'var_x': 'Control',
#     'var_y': 'Treatment',
#     'pvalue': 0.023,
#     'pstars': '*',
#     'effect_size': 0.49,
#     'effect_size_type': "Cohen's d",
#     'H0': 'μ1 = μ2',
#     'rejected': True,
#     'alpha': 0.05,
#     'df': 98,
#     'ci': (0.15, 2.34)
# }

# Multiple tests - returns DataFrame
df = pd.DataFrame({
    'age': [25, 30, 35, ...],
    'BMI': [22.5, 26.3, 24.1, ...],
    'blood_pressure': [120, 135, 128, ...]
})

results_df = stx.stats.tests.multivariate.test_corr_multi(df)
print(results_df)
# Output DataFrame:
#   var_x           var_y      n_x  n_y  n_pairs  statistic  pvalue  pstars  ...
# 0 age             BMI        98   97   95       0.45       0.023   *       ...
# 1 age             blood_p... 98   96   94       0.33       0.056   ns      ...
# 2 BMI             blood_p... 97   96   93       0.67       0.001   ***     ...
```

#### 2.1 `parametric/`
Classical parametric tests assuming normal distributions (all with `test_` prefix)

- `_test_ttest.py`:
  - `test_ttest_ind()`: Independent samples t-test
  - `test_ttest_rel()`: Paired samples t-test
  - `test_ttest_1samp()`: One-sample t-test

- `_test_anova.py`:
  - `test_anova()`: One-way ANOVA
  - `test_anova_rm()`: Repeated measures ANOVA

- `_test_correlation.py`:
  - `test_pearson()`: Pearson correlation test
  - `test_corr()`: Generic correlation test wrapper

#### 2.2 `nonparametric/`
Distribution-free tests (all with `test_` prefix)

- `_test_mann_whitney.py`: `test_mannwhitneyu()`
- `_test_wilcoxon.py`: `test_wilcoxon()`
- `_test_kruskal.py`: `test_kruskal()`
- `_test_brunner_munzel.py`: `test_brunner_munzel()`, `test_bm()`
- `_test_spearman.py`: `test_spearman()`, `test_corr_spearman()`

#### 2.3 `categorical/`
Tests for categorical/count data (all with `test_` prefix)

- `_test_chi2.py`: `test_chi2_contingency()`, `test_chisquare()`
- `_test_fisher.py`: `test_fisher_exact()`

#### 2.4 `normality/`
Tests for distribution assumptions (all with `test_` prefix)

- `_test_shapiro.py`: `test_shapiro()`
- `_test_kstest.py`: `test_kstest()`

#### 2.5 `outliers/`
Outlier detection (all with `test_` prefix)

- `_test_grubbs.py`: `test_grubbs()`, `test_smirnov_grubbs()`
- `_test_dixon.py`: `test_dixon()`

#### 2.6 `multivariate/`
Tests involving multiple variables (all with `test_` prefix)

- `_test_partial_corr.py`: `test_partial_corr()`
- `_test_multivariate.py`: `test_corr_multi()`, `test_nocorrelation()`

**Output Format (Dict)**:
```python
{
    "test_method": str,        # e.g., "Independent t-test"
    "statistic_name": str,     # e.g., "t", "F", "U", "r"
    "statistic": float,        # The test statistic value
    "alternative": str,        # "two-sided", "greater", "less" (H1)
    "n_samples": int,          # Total sample size
    "n_x": int,                # Sample size for variable x (if applicable)
    "n_y": int,                # Sample size for variable y (if applicable)
    "var_x": str,              # Label for variable x (if applicable)
    "var_y": str,              # Label for variable y (if applicable)
    "pvalue": float,           # P-value (uncorrected)
    "pvalue_adjusted": float,  # Adjusted p-value (after multiple comparison correction)
    "pstars": str,             # "***", "**", "*", "ns" (based on adjusted pvalue if available)
    "alpha": float,            # Significance level (default: 0.05)
    "alpha_adjusted": float,   # Adjusted alpha (e.g., Bonferroni-corrected)
    "rejected": bool,          # H0 rejected using adjusted criteria
    "effect_size": float,      # Effect size value
    "effect_size_type": str,   # "Cohen's d", "eta-squared", "r", etc.
    "power": float,            # Statistical power (1 - β)
    "H0": str,                 # Null hypothesis (e.g., "μ1 = μ2", "ρ = 0")
    # Additional test-specific fields (e.g., "df", "ci_lower", "ci_upper", etc.)
}
```

**Output Format (DataFrame for multiple tests)**:
```python
# Example: test_corr_multi(df) output
pd.DataFrame with columns:
    var_x           : str    # First variable label
    var_y           : str    # Second variable label
    n_x             : int    # Sample size for var_x (non-NaN)
    n_y             : int    # Sample size for var_y (non-NaN)
    n_pairs         : int    # Valid pairs (both non-NaN)
    test_method     : str    # "Pearson correlation"
    statistic_name  : str    # "r"
    statistic       : float  # Correlation coefficient
    pvalue          : float  # P-value (uncorrected)
    pvalue_adjusted : float  # Adjusted p-value (NaN if not corrected)
    pstars          : str    # Significance stars (based on adjusted if available)
    alpha           : float  # Significance level (default: 0.05)
    alpha_adjusted  : float  # Adjusted alpha (NaN if not corrected)
    rejected        : bool   # Whether significant (using adjusted criteria)
    effect_size     : float  # Same as statistic for correlation
    effect_size_type: str    # "Pearson's r"
    power           : float  # Statistical power (1 - β)
    H0              : str    # "ρ = 0"
    alternative     : str    # "two-sided"
```

### 3. `correct/` - Multiple Comparison Corrections

**Purpose**: Adjust p-values for multiple testing (all with `correct_` prefix)

**Modules**:
- `_correct_bonferroni.py`: `correct_bonferroni()`
- `_correct_fdr.py`: `correct_fdr()` (Benjamini-Hochberg FDR)
- `_correct_holm.py`: `correct_holm()` (Holm-Bonferroni)
- `_correct_multicompair.py`: `correct_multicompair()` (pairwise framework)

**Output Format**:
```python
{
    "pvalues_corrected": np.ndarray,
    "reject": np.ndarray,  # Boolean mask
    "method": str,
    "alpha": float
}
```

### 4. `utils/` - Utility Functions

**Purpose**: Supporting functionality for statistical analysis

**Modules**:
- `_validators.py`:
  - `StatisticalValidator`: Input validation class

- `_effect_size.py`:
  - `EffectSizeCalculator`: Effect size computation class
  - `cohens_d()`, `hedges_g()`, `glass_delta()`
  - `eta_squared()`, `omega_squared()`, `cramers_v()`

- `_power.py`:
  - `compute_power()`: Calculate statistical power for a test
  - `compute_sample_size()`: Required sample size for desired power
  - `power_ttest()`: Power analysis for t-tests
  - `power_anova()`: Power analysis for ANOVA
  - `power_correlation()`: Power analysis for correlations
  - `power_chisquare()`: Power analysis for chi-square tests

- `_formatters.py`:
  - `p2stars()`: Convert p-values to significance stars
  - `format_pvalue()`: Format p-values for publication

- `_normalizers.py`:
  - `normalize_result()`: Normalize test results to standard format
  - `to_dataframe()`: Convert dict/list of results to DataFrame
  - `force_dataframe()`: Ensure DataFrame output with NaN filling
  - `to_dict()`: Convert DataFrame row to dict

- `_distributions.py`:
  - `norm`, `t`, `chi2`, `nct`: Distribution objects/functions

- `_diagnostics.py`:
  - `probplot()`: Probability plots
  - `qq_plot()`: Q-Q plots

**Normalizer Usage Examples**:

```python
from scitex.stats.utils import to_dataframe, force_dataframe

# Example 1: Single test result
result = test_ttest_ind(x, y)
df = to_dataframe(result)  # Convert dict to single-row DataFrame

# Example 2: Multiple results with missing fields
results = [
    {'var_x': 'A', 'var_y': 'B', 'pvalue': 0.01},
    {'var_x': 'C', 'var_y': 'D', 'pvalue': 0.05, 'effect_size': 0.5},
]
df = force_dataframe(results, fill_na=True)
# Output:
#   var_x var_y  pvalue  effect_size
# 0     A     B    0.01          NaN
# 1     C     D    0.05          0.5

# Example 3: Ensure all standard columns exist
df = force_dataframe(
    results,
    columns=['var_x', 'var_y', 'pvalue', 'pstars', 'effect_size', 'rejected'],
    fill_na=True,
    defaults={'pstars': 'ns', 'rejected': False}
)
```

**Key Features**:
1. **Automatic column detection**: Infers standard columns from data
2. **NaN filling**: Fills missing values appropriately
3. **Type coercion**: Ensures correct dtypes (float, int, bool, str)
4. **Defaults**: Provides sensible defaults for missing fields
5. **Validation**: Checks for required fields before conversion

**Power Analysis Usage Examples**:

```python
from scitex.stats.utils import compute_power, compute_sample_size

# Example 1: Post-hoc power analysis (after running test)
result = test_ttest_ind(group1, group2)
# Power is already included in result['power']
print(f"Statistical power: {result['power']:.3f}")

# Example 2: A priori power analysis (before collecting data)
# How many samples needed for power=0.8 with effect_size=0.5?
n_required = compute_sample_size(
    test='ttest_ind',
    effect_size=0.5,
    alpha=0.05,
    power=0.8,
    alternative='two-sided'
)
print(f"Required sample size per group: {n_required}")

# Example 3: Sensitivity analysis
# What effect size can we detect with n=50 per group?
min_effect_size = compute_effect_size(
    test='ttest_ind',
    n=50,
    alpha=0.05,
    power=0.8,
    alternative='two-sided'
)
print(f"Minimum detectable effect size: {min_effect_size:.3f}")
```

**Multiple Comparison Correction Usage Examples**:

```python
from scitex.stats.correct import correct_fdr, correct_bonferroni
from scitex.stats.utils import force_dataframe

# Example 1: Correct p-values in DataFrame
df_results = test_corr_multi(data)

# Apply FDR correction
df_corrected = correct_fdr(df_results, alpha=0.05)
# Adds columns: 'pvalue_adjusted', 'alpha_adjusted', 'rejected'
# Updates 'pstars' based on adjusted pvalue

# Example 2: Apply Bonferroni correction
df_corrected = correct_bonferroni(df_results, alpha=0.05)

# Example 3: Manually apply to p-values array
pvalues = df_results['pvalue'].values
corrected_pvals, rejected = correct_fdr(pvalues, alpha=0.05, return_rejected=True)

# Add back to DataFrame
df_results['pvalue_adjusted'] = corrected_pvals
df_results['rejected'] = rejected

# Example 4: Correction with custom alpha
df_corrected = correct_fdr(df_results, alpha=0.01)  # More stringent
```

## API Design Principles

### 1. Consistent Return Format

All statistical tests return dictionaries with standardized keys:

```python
# Example: t-test
result = stx.stats.tests.parametric.ttest_ind(x, y)
# Returns:
{
    "statistic": 2.45,
    "pvalue": 0.023,
    "df": 18,
    "method": "Independent samples t-test",
    "alternative": "two-sided",
    "ci": (0.15, 2.34),  # 95% confidence interval
    "effect_size": 0.82,  # Cohen's d
}
```

### 2. DataFrame Support

Multi-variable tests return pandas DataFrames:

```python
# Example: Multiple correlations
result = stx.stats.tests.multivariate.corr_test_multi(df)
# Returns DataFrame:
#     var1  var2  statistic  pvalue  method
# 0    x     y      0.45    0.023   Pearson
# 1    x     z      0.33    0.056   Pearson
# 2    y     z      0.67    0.001   Pearson
```

### 3. Flexible Input and Output

Accept both numpy arrays and pandas Series/DataFrames, with automatic format conversion:

```python
import numpy as np
import pandas as pd
from scitex.stats.tests.parametric import test_ttest_ind
from scitex.stats.utils import to_dataframe, force_dataframe

# Works with numpy - returns dict
result = test_ttest_ind(np.array([1,2,3]), np.array([4,5,6]))
# result is a dict

# Works with pandas - automatically extracts variable names
result = test_ttest_ind(df['Control'], df['Treatment'])
# result['var_x'] = 'Control', result['var_y'] = 'Treatment'

# Convert any result to DataFrame
df_result = to_dataframe(result)

# Run multiple tests and combine
results = []
for col in ['age', 'BMI', 'BP']:
    r = test_ttest_ind(df_control[col], df_treatment[col], var_x='Control', var_y='Treatment')
    results.append(r)

# Normalize to DataFrame with consistent columns
df_results = force_dataframe(
    results,
    columns=['var_x', 'var_y', 'statistic', 'pvalue', 'pstars', 'effect_size', 'rejected'],
    fill_na=True
)
```

### 4. Sensible Defaults

Common use cases work with minimal parameters:

```python
# Simple call with defaults
stx.stats.tests.parametric.ttest_ind(x, y)  # two-sided, equal_var=True

# Advanced usage with options
stx.stats.tests.parametric.ttest_ind(
    x, y,
    alternative='greater',
    equal_var=False,  # Welch's t-test
    alpha=0.01
)
```

## Migration Strategy

### Phase 1: Create New Structure
1. Create new directory structure
2. Implement core functionality with new API
3. Add comprehensive tests
4. Document all functions

### Phase 2: Parallel Operation
1. New structure coexists with old
2. Update examples to use new API
3. Deprecation warnings in old functions

### Phase 3: Complete Migration
1. Remove old structure
2. Update all internal SciTeX code
3. Final documentation pass

## Import Patterns

### Top-level convenience imports
```python
import scitex as stx

# Common functions available at top level
stx.stats.ttest_ind(x, y)              # Re-exported for convenience
stx.stats.describe(data)                # Re-exported for convenience
stx.stats.bonferroni_correction(pvals) # Re-exported for convenience
```

### Explicit imports for clarity
```python
from scitex.stats.tests.parametric import ttest_ind, pearsonr
from scitex.stats.tests.nonparametric import mannwhitneyu
from scitex.stats.multiple_comparisons import fdr_correction
from scitex.stats.descriptive import describe
```

### Submodule imports for organization
```python
from scitex.stats import tests, descriptive, utils

# Use with submodule prefix
tests.parametric.ttest_ind(x, y)
descriptive.describe(data)
utils.p2stars(pvalues)
```

## Implementation Notes

### 1. Class-based vs Function-based

**Use classes for**:
- Validators (StatisticalValidator)
- Effect size calculators (EffectSizeCalculator)
- Complex stateful operations

**Use functions for**:
- All statistical tests
- Descriptive statistics
- Simple transformations

### 2. Error Handling

All functions should:
- Validate inputs using StatisticalValidator
- Raise informative errors with suggestions
- Handle edge cases gracefully

```python
def ttest_ind(x, y, **kwargs):
    """Independent samples t-test."""
    # Validate inputs
    x, y = StatisticalValidator.validate_samples(x, y)

    # Check assumptions
    if not StatisticalValidator.check_normality(x):
        logger.warning("Sample x may not be normally distributed. "
                      "Consider using mannwhitneyu() instead.")

    # Perform test
    ...
```

### 3. Logging

Use scitex.logging for informative messages:

```python
from scitex import logging
logger = logging.getLogger(__name__)

# Inform about assumptions
logger.info("Performing Welch's t-test (unequal variances)")

# Warn about potential issues
logger.warning("Small sample size (n<30). Results may be unreliable.")
```

## Testing Strategy

### Unit Tests
- Each function has comprehensive unit tests
- Test edge cases, invalid inputs, NaN handling
- Compare against scipy.stats where applicable

### Integration Tests
- Test workflow patterns
- Verify format consistency
- Test with real scientific data

### Performance Tests
- Benchmark against scipy
- Profile memory usage
- Test with large datasets

## Documentation Requirements

Each function must have:

1. **Docstring** following NumPy style
2. **Mathematical formula** in LaTeX
3. **Usage example** with real data
4. **Reference** to paper/textbook
5. **See Also** linking related functions

Example:

```python
def ttest_ind(x, y, alternative='two-sided', equal_var=True, alpha=0.05):
    """
    Independent samples t-test.

    Tests the null hypothesis that two independent samples have identical
    average (expected) values.

    Parameters
    ----------
    x : array_like
        First sample observations
    y : array_like
        Second sample observations
    alternative : {'two-sided', 'less', 'greater'}, default 'two-sided'
        Alternative hypothesis
    equal_var : bool, default True
        If True, perform standard t-test assuming equal variances.
        If False, perform Welch's t-test (unequal variances).
    alpha : float, default 0.05
        Significance level for confidence interval

    Returns
    -------
    result : dict
        Dictionary containing:
        - statistic : float
            The t-statistic
        - pvalue : float
            Two-tailed p-value
        - df : float
            Degrees of freedom
        - ci : tuple
            Confidence interval for the difference in means
        - effect_size : float
            Cohen's d effect size

    Notes
    -----
    The t-statistic is calculated as:

    .. math::
        t = \\frac{\\bar{x}_1 - \\bar{x}_2}{s_p \\sqrt{\\frac{1}{n_1} + \\frac{1}{n_2}}}

    where :math:`s_p` is the pooled standard deviation.

    References
    ----------
    .. [1] Student (1908). "The probable error of a mean". Biometrika.

    Examples
    --------
    >>> import numpy as np
    >>> import scitex as stx
    >>>
    >>> # Compare two groups
    >>> group1 = np.random.normal(10, 2, 50)
    >>> group2 = np.random.normal(12, 2, 50)
    >>>
    >>> result = stx.stats.tests.parametric.ttest_ind(group1, group2)
    >>> print(f"t = {result['statistic']:.3f}, p = {result['pvalue']:.4f}")

    See Also
    --------
    ttest_rel : Paired samples t-test
    mannwhitneyu : Non-parametric alternative
    """
    ...
```

## Benefits of This Architecture

1. **Clarity**: Clear organization by statistical domain
2. **Discoverability**: Easy to find the right function
3. **Consistency**: Standardized API across all functions
4. **Maintainability**: Separation of concerns
5. **Extensibility**: Easy to add new tests
6. **Teaching**: Structure reflects statistical workflow
7. **IDE Support**: Better autocomplete and documentation

## Timeline

- **Week 1**: Create directory structure, implement descriptive stats
- **Week 2**: Implement parametric and nonparametric tests
- **Week 3**: Implement multiple comparisons and utils
- **Week 4**: Documentation, examples, and testing
- **Week 5**: Migration and deprecation

## Questions for Discussion

1. Should we keep `StatisticalValidator` and `EffectSizeCalculator` as classes or convert to functional APIs?
2. How should we handle scipy.stats re-exports vs. wrappers?
3. Should we include Bayesian statistics in a separate submodule?
4. How granular should the submodule structure be?

<!-- EOF -->