# SciTeX Stats - Quick Start Guide

## Installation

The module is already part of SciTeX. No additional installation needed!

## Import

```python
import scitex as stx
import numpy as np
```

## Basic Usage

### 1. Compare Two Groups

```python
# Generate sample data
group_a = np.random.normal(10, 2, 30)
group_b = np.random.normal(12, 2, 30)

# Parametric test (assumes normality)
result = stx.stats.tests.test_ttest_ind(
    group_a, group_b,
    var_x='Control',
    var_y='Treatment',
    plot=True
)

print(f"t = {result['statistic']:.3f}, p = {result['pvalue']:.4f}")
print(f"Cohen's d = {result['effect_size']:.3f} ({result['effect_size_interpretation']})")

# Non-parametric alternative (no normality assumption)
result = stx.stats.tests.test_mannwhitneyu(group_a, group_b, plot=True)
```

### 2. Compare 3+ Groups

```python
group_a = np.random.normal(10, 2, 20)
group_b = np.random.normal(12, 2, 20)
group_c = np.random.normal(11, 2, 20)

# One-way ANOVA with automatic assumption checking
result = stx.stats.tests.test_anova(
    [group_a, group_b, group_c],
    var_names=['Control', 'Treatment A', 'Treatment B'],
    check_assumptions=True,  # Checks normality + homogeneity
    plot=True
)

print(f"F = {result['statistic']:.3f}, p = {result['pvalue']:.4f}")
print(f"η² = {result['effect_size']:.3f}")

# Non-parametric alternative
result = stx.stats.tests.test_kruskal([group_a, group_b, group_c], plot=True)
```

### 3. Paired Samples

```python
before = np.array([120, 135, 118, 127, 130])
after = np.array([110, 125, 115, 120, 118])

# Paired t-test
result = stx.stats.tests.test_ttest_rel(before, after, plot=True)

# Non-parametric alternative
result = stx.stats.tests.test_wilcoxon(before, after, plot=True)
```

### 4. Correlation

```python
x = np.random.normal(0, 1, 50)
y = 0.7 * x + np.random.normal(0, 0.5, 50)

# Pearson (linear correlation)
result = stx.stats.tests.test_pearson(x, y, plot=True)
print(f"r = {result['statistic']:.3f}, R² = {result['r_squared']:.3f}")

# Spearman (monotonic correlation, more robust)
result = stx.stats.tests.test_spearman(x, y, plot=True)
print(f"ρ = {result['statistic']:.3f}")
```

### 5. Categorical Data

```python
# Chi-square test
observed = np.array([[30, 10], [20, 40]])  # 2×2 table
result = stx.stats.tests.test_chi2(
    observed,
    var_row='Treatment',
    var_col='Outcome',
    plot=True
)
print(f"χ² = {result['statistic']:.2f}, Cramér's V = {result['effect_size']:.3f}")

# Fisher's exact test (for small samples)
observed = [[8, 2], [1, 5]]
result = stx.stats.tests.test_fisher(observed, plot=True)
print(f"OR = {result['statistic']:.2f}")
```

## Multiple Comparisons

```python
from scitex.stats.tests import test_ttest_ind
from scitex.stats.correct import correct_holm

# Run multiple tests
results = []
for i in range(10):
    r = test_ttest_ind(groups_a[i], groups_b[i])
    results.append(r)

# Apply Holm correction (more powerful than Bonferroni)
corrected = correct_holm(results, alpha=0.05)

print(f"Number of rejections: {corrected['n_rejected']}")
```

## Export Results

```python
from scitex.stats.utils import convert_results

result = stx.stats.tests.test_anova([group_a, group_b, group_c])

# Export to different formats
convert_results(result, return_as='csv', path='results.csv')
convert_results(result, return_as='latex', path='table.tex')
convert_results(result, return_as='excel', path='results.xlsx')
```

## Complete Workflow Example

```python
import scitex as stx
import numpy as np

# 1. Generate data
np.random.seed(42)
control = np.random.normal(100, 15, 30)
treatment_a = np.random.normal(110, 15, 30)
treatment_b = np.random.normal(105, 15, 30)

# 2. Run ANOVA
result = stx.stats.tests.test_anova(
    [control, treatment_a, treatment_b],
    var_names=['Control', 'Treatment A', 'Treatment B'],
    check_assumptions=True,
    plot=True,
    alpha=0.05
)

print(f"ANOVA Results:")
print(f"  F({result['df_between']}, {result['df_within']}) = {result['statistic']:.3f}")
print(f"  p = {result['pvalue']:.4f} {result['stars']}")
print(f"  η² = {result['effect_size']:.3f} ({result['effect_size_interpretation']})")

# 3. Check assumptions
if not result['assumptions_met']:
    print("\nAssumptions violated! Using Kruskal-Wallis instead:")
    result = stx.stats.tests.test_kruskal(
        [control, treatment_a, treatment_b],
        var_names=['Control', 'Treatment A', 'Treatment B'],
        plot=True
    )
    print(f"  H = {result['statistic']:.3f}, p = {result['pvalue']:.4f}")

# 4. Post-hoc comparisons (if ANOVA significant)
if result['significant']:
    from scitex.stats.tests import test_ttest_ind
    from scitex.stats.correct import correct_holm

    groups = [control, treatment_a, treatment_b]
    group_names = ['Control', 'Treatment A', 'Treatment B']

    posthoc_results = []
    for i in range(3):
        for j in range(i+1, 3):
            r = test_ttest_ind(
                groups[i], groups[j],
                var_x=group_names[i],
                var_y=group_names[j]
            )
            posthoc_results.append(r)

    # Apply Holm correction
    corrected = correct_holm(posthoc_results, alpha=0.05)

    print(f"\nPost-hoc comparisons (Holm-corrected):")
    for r in corrected['results']:
        print(f"  {r['var_x']} vs {r['var_y']}: p = {r['pvalue_adjusted']:.4f} {r['stars']}")

# 5. Export results
convert_results(result, return_as='excel', path='anova_results.xlsx')
convert_results(corrected, return_as='latex', path='posthoc_results.tex')
```

## All Available Tests

### Parametric
- `test_ttest_ind()` - Independent t-test
- `test_ttest_rel()` - Paired t-test
- `test_ttest_1samp()` - One-sample t-test
- `test_anova()` - One-way ANOVA

### Non-Parametric
- `test_brunner_munzel()` - Robust 2-sample comparison
- `test_wilcoxon()` - Paired samples
- `test_kruskal()` - 3+ independent groups
- `test_mannwhitneyu()` - 2 independent samples

### Normality
- `test_shapiro()` - Single sample normality
- `test_normality()` - Multiple samples
- `test_ks_1samp()` - KS test vs distribution
- `test_ks_2samp()` - KS test 2 samples

### Correlation
- `test_pearson()` - Linear correlation
- `test_spearman()` - Monotonic correlation

### Categorical
- `test_chi2()` - Chi-square independence
- `test_fisher()` - Fisher's exact test

## Common Parameters

All tests support:
- `alpha` - Significance level (default: 0.05)
- `plot` - Generate visualization (default: False)
- `return_as` - Output format: 'dict' or 'dataframe' (default: 'dict')
- `decimals` - Rounding precision (default: 3)
- `alternative` - Hypothesis: 'two-sided', 'less', 'greater'

## Need Help?

See full documentation:
- **README.md** - Overview
- **docs/API.md** - Complete API reference
- **docs/PROGRESS.md** - Detailed examples for each test
- **docs/SUMMARY.md** - Comparison with other libraries

## Run Test Examples

```bash
# See 7-10 comprehensive examples for each test
python -m scitex.stats.tests.parametric._test_ttest
python -m scitex.stats.tests.categorical._test_chi2
python -m scitex.stats.tests.correlation._test_spearman
```

---

Happy analyzing! 🎉
