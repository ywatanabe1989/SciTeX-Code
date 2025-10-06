# SciTeX Stats Module - API Reference

## Normalized Naming Convention

All statistical test functions use the `test_*` prefix for clarity and consistency.

## Module Structure

```python
import scitex as stx

stx.stats.tests          # Statistical tests
stx.stats.correct        # Multiple comparison corrections
stx.stats.effect_sizes   # Effect size measures
stx.stats.power          # Power analysis
```

## Statistical Tests (stx.stats.tests)

### Parametric Tests
- `test_ttest_ind()` - Independent samples t-test
- `test_ttest_rel()` - Paired (related) samples t-test
- `test_ttest_1samp()` - One-sample t-test
- `test_anova()` - One-way ANOVA

### Non-parametric Tests
- `test_brunner_munzel()` - Brunner-Munzel test (robust 2-sample comparison)
- `test_wilcoxon()` - Wilcoxon signed-rank test (paired samples)
- `test_kruskal()` - Kruskal-Wallis H test (3+ independent groups)
- `test_mannwhitneyu()` - Mann-Whitney U test (2 independent samples)

### Normality Tests
- `test_shapiro()` - Shapiro-Wilk normality test (single sample)
- `test_normality()` - Check normality for multiple samples (uses Shapiro-Wilk)
- `test_ks_1samp()` - One-sample Kolmogorov-Smirnov test
- `test_ks_2samp()` - Two-sample Kolmogorov-Smirnov test

### Correlation Tests
- `test_pearson()` - Pearson correlation (linear relationships)
- `test_spearman()` - Spearman rank correlation (monotonic relationships)

### Categorical Tests
- `test_chi2()` - Chi-square test of independence (contingency tables)
- `test_fisher()` - Fisher's exact test (2×2 tables, small samples)


## Multiple Comparison Corrections (stx.stats.correct)

- `correct_bonferroni()` - Bonferroni correction (conservative)
- `correct_fdr()` - False Discovery Rate (Benjamini-Hochberg/Benjamini-Yekutieli)
- `correct_holm()` - Holm-Bonferroni correction (more powerful than Bonferroni)

## Effect Sizes (stx.stats.effect_sizes)

### Effect Size Functions
- `cohens_d()` - Cohen's d for standardized mean difference
- `cliffs_delta()` - Cliff's delta (non-parametric effect size)
- `prob_superiority()` - P(X>Y) probability of superiority
- `eta_squared()` - Eta-squared for ANOVA
- `epsilon_squared()` - Epsilon-squared for Kruskal-Wallis

### Interpretation Functions
- `interpret_cohens_d()`
- `interpret_cliffs_delta()`
- `interpret_prob_superiority()`
- `interpret_eta_squared()`
- `interpret_epsilon_squared()`

## Power Analysis (stx.stats.power)

- `power_ttest()` - Compute statistical power for t-tests
- `sample_size_ttest()` - Determine required sample size for t-tests

## Common Parameters

All test functions support consistent parameters:

```python
test_xxx(
    data,                    # Input data
    var_x='x',               # Variable names for labeling
    var_y='y',
    alternative='two-sided', # Hypothesis direction
    alpha=0.05,              # Significance level
    plot=False,              # Generate visualization
    return_as='dict',        # Output format: 'dict', 'dataframe'
    decimals=3               # Rounding precision
)
```

## Export Formats

All test results can be exported to 9 formats using `convert_results()`:

1. `'dict'` - Python dictionary
2. `'dataframe'` - pandas DataFrame
3. `'csv'` - CSV file with SciTeX signature
4. `'json'` - JSON format
5. `'excel'` - Styled Excel workbook
6. `'latex'` - LaTeX table
7. `'markdown'` - Markdown table
8. `'html'` - HTML table
9. `'text'` - Plain text report

## Usage Examples

### Basic Test
```python
import scitex as stx
import numpy as np

x = np.random.normal(0, 1, 30)
y = np.random.normal(0.5, 1, 30)

# Run t-test
result = stx.stats.tests.test_ttest_ind(x, y, plot=True)
print(result)
```

### With Multiple Comparison Correction
```python
# Run multiple tests
results = []
for i in range(10):
    result = stx.stats.tests.test_ttest_ind(group_a[i], group_b[i])
    results.append(result)

# Apply Holm correction
corrected = stx.stats.correct.correct_holm(results, alpha=0.05)
```

### Access Effect Sizes
```python
# Compute Cohen's d
d = stx.stats.effect_sizes.cohens_d(x, y)
interpretation = stx.stats.effect_sizes.interpret_cohens_d(d)
print(f"Cohen's d = {d:.3f} ({interpretation})")
```

### Power Analysis
```python
# Compute required sample size
n = stx.stats.power.sample_size_ttest(
    effect_size=0.5,
    alpha=0.05,
    power=0.80,
    alternative='two-sided'
)
print(f"Required n = {n} per group")
```

## Notes

- **Consistent naming**: All test functions use the `test_*` prefix
- **No backward compatibility**: Clean, normalized API without legacy names
- **Clear organization**: Tests grouped by category (parametric, nonparametric, etc.)

## Design Principles

1. **Consistent naming**: All tests use `test_*` prefix
2. **Comprehensive output**: p-values, effect sizes, confidence intervals
3. **Publication-ready**: Visualizations and formatted export
4. **Assumption checking**: Automatic validation where applicable
5. **Flexible returns**: dict, DataFrame, or exported files
6. **Professional branding**: SciTeX signature in all exports
