# SciTeX Stats Module - Implementation Progress

**Last Updated**: 2025-10-01
**Status**: Production Ready ✓

---

## Summary

A professional statistical testing framework with **16 statistical tests**, **3 multiple comparison corrections**, comprehensive effect sizes, and publication-ready outputs.

### Key Achievements
- ✓ Normalized `test_*` naming for all tests
- ✓ Clean module structure: `tests`, `correct`, `effect_sizes`, `power`
- ✓ 9 export formats (CSV, LaTeX, Excel, JSON, etc.)
- ✓ Automatic assumption checking
- ✓ Publication-ready visualizations
- ✓ Consistent API across all tests

---

## Module Structure

```
scitex.stats/
├── tests/              # 16 statistical tests (all with test_* prefix)
│   ├── parametric/     # 4 tests: t-tests (3 variants), ANOVA
│   ├── nonparametric/  # 4 tests: Brunner-Munzel, Wilcoxon, Kruskal, Mann-Whitney
│   ├── normality/      # 4 tests: Shapiro-Wilk, test_normality, KS (2 variants)
│   ├── correlation/    # 2 tests: Pearson, Spearman
│   └── categorical/    # 2 tests: Chi-square, Fisher's exact
├── correct/            # 3 multiple comparison corrections
├── effect_sizes/       # Effect size computations + interpretations
└── power/              # Power analysis functions
```

---

## Implemented Tests (16 Total)

### Parametric Tests (4) ✓

#### 1. Independent Samples t-test (`test_ttest_ind`)
```python
from scitex.stats.tests import test_ttest_ind
import numpy as np

x = np.random.normal(0, 1, 30)
y = np.random.normal(0.5, 1, 30)

result = test_ttest_ind(x, y, plot=True)
print(f"t = {result['statistic']:.3f}, p = {result['pvalue']:.4f}")
print(f"Cohen's d = {result['effect_size']:.3f} ({result['effect_size_interpretation']})")
```

**Features**:
- Student's t-test and Welch's t-test (automatic selection)
- Cohen's d effect size
- Statistical power computation
- 2-panel visualization: histograms + box plots

#### 2. Paired Samples t-test (`test_ttest_rel`)
```python
from scitex.stats.tests import test_ttest_rel

before = np.array([120, 135, 118, 127, 130])
after = np.array([110, 125, 115, 120, 118])

result = test_ttest_rel(before, after, var_x='Before', var_y='After', plot=True)
```

**Features**:
- Within-subjects design
- Cohen's d for paired differences
- Automatic normality checking of differences
- Difference distribution visualization

#### 3. One-Sample t-test (`test_ttest_1samp`)
```python
from scitex.stats.tests import test_ttest_1samp

sample = np.array([5.2, 5.8, 6.1, 5.5, 6.3])
population_mean = 5.0

result = test_ttest_1samp(sample, popmean=population_mean, plot=True)
```

**Features**:
- Compare sample mean to known population value
- Cohen's d for one sample
- One-sided and two-sided tests

#### 4. One-Way ANOVA (`test_anova`)
```python
from scitex.stats.tests import test_anova

group_a = np.random.normal(10, 2, 20)
group_b = np.random.normal(12, 2, 20)
group_c = np.random.normal(11, 2, 20)

result = test_anova(
    [group_a, group_b, group_c],
    var_names=['Control', 'Treatment A', 'Treatment B'],
    check_assumptions=True,
    plot=True
)
```

**Features**:
- F-statistic and eta-squared (η²) effect size
- **Automatic assumption checking**: normality (Shapiro-Wilk) + homogeneity (Levene's test)
- 4-panel visualization: box plots, violin plots, histograms, Q-Q plots
- Warnings and recommendations when assumptions violated
- Post-hoc comparison examples

---

### Non-Parametric Tests (4) ✓

#### 5. Brunner-Munzel Test (`test_brunner_munzel`)
```python
from scitex.stats.tests import test_brunner_munzel

x = np.random.exponential(2, 25)
y = np.random.exponential(3, 30)

result = test_brunner_munzel(x, y, plot=True)
print(f"P(X>Y) = {result['effect_size']:.3f}")
print(f"Cliff's delta = {result['effect_size_secondary']:.3f}")
```

**Features**:
- **Dual effect sizes**: P(X>Y) probability of superiority + Cliff's delta
- Robust to non-normality, unequal variances, outliers
- Q-Q plots and distribution comparisons
- More powerful than Mann-Whitney U

#### 6. Wilcoxon Signed-Rank Test (`test_wilcoxon`)
```python
from scitex.stats.tests import test_wilcoxon

before = np.array([8.5, 9.2, 7.8, 8.1, 9.0])
after = np.array([7.2, 8.5, 7.0, 7.5, 8.2])

result = test_wilcoxon(before, after, plot=True)
```

**Features**:
- Non-parametric paired test (alternative to paired t-test)
- Rank-biserial correlation effect size
- Handles ties automatically
- Distribution of signed ranks visualization

#### 7. Kruskal-Wallis H Test (`test_kruskal`)
```python
from scitex.stats.tests import test_kruskal

group1 = np.random.gamma(2, 2, 15)
group2 = np.random.gamma(3, 2, 15)
group3 = np.random.gamma(2.5, 2, 15)

result = test_kruskal(
    [group1, group2, group3],
    var_names=['Method A', 'Method B', 'Method C'],
    plot=True
)
```

**Features**:
- Non-parametric alternative to one-way ANOVA (3+ groups)
- Epsilon-squared (ε²) effect size
- Box plots + violin plots with significance annotations
- Works with ordinal data (Likert scales)
- Post-hoc pairwise comparison examples

#### 8. Mann-Whitney U Test (`test_mannwhitneyu`)
```python
from scitex.stats.tests import test_mannwhitneyu

group_a = [7, 8, 6, 9, 7, 8, 100]  # Has outlier
group_b = [5, 6, 5, 7, 6, 5, 6]

result = test_mannwhitneyu(group_a, group_b, plot=True)
```

**Features**:
- Non-parametric two-sample test
- Rank-biserial correlation: r = 1 - (2U)/(n₁×n₂)
- 4-panel visualization: box plots, histograms, rank distribution, CDF
- Robust to outliers
- Comparison with t-test and Brunner-Munzel

---

### Normality Tests (4) ✓

#### 9. Shapiro-Wilk Test (`test_shapiro`)
```python
from scitex.stats.tests import test_shapiro

data = np.random.normal(0, 1, 50)

result = test_shapiro(data, var_x='Sample', plot=True)
print(f"W = {result['statistic']:.4f}, p = {result['pvalue']:.4f}")
```

**Features**:
- W statistic and p-value
- Q-Q plot for visual assessment
- Sample size warnings (n < 3 or n > 5000)
- Recommendations for alternative tests

#### 10. Test Normality for Multiple Samples (`test_normality`)
```python
from scitex.stats.tests import test_normality

result = test_normality(
    group_a, group_b, group_c,
    var_names=['A', 'B', 'C'],
    alpha=0.05
)

print(f"All normal: {result['all_normal']}")
for r in result['results']:
    print(f"{r['var_x']}: {r['normal']}")
```

**Features**:
- Check multiple samples simultaneously
- Uses Shapiro-Wilk for each sample
- Integrated into ANOVA assumption checking
- Returns summary + individual results

#### 11. One-Sample Kolmogorov-Smirnov Test (`test_ks_1samp`)
```python
from scitex.stats.tests import test_ks_1samp

data = np.random.normal(0, 1, 100)

# Test against normal distribution
result = test_ks_1samp(data, cdf='norm', args=(0, 1), plot=True)

# Test against exponential
result = test_ks_1samp(data, cdf='expon', plot=True)
```

**Features**:
- Test against any scipy.stats distribution
- D statistic (maximum CDF difference)
- CDF comparison plots
- Alternative hypotheses: two-sided, less, greater

#### 12. Two-Sample Kolmogorov-Smirnov Test (`test_ks_2samp`)
```python
from scitex.stats.tests import test_ks_2samp

sample1 = np.random.normal(0, 1, 50)
sample2 = np.random.normal(0.5, 1.5, 50)

result = test_ks_2samp(sample1, sample2, plot=True)
```

**Features**:
- Compare empirical CDFs of two samples
- Distribution-free test
- Sensitive to differences in location, scale, and shape

---

### Correlation Tests (2) ✓

#### 13. Pearson Correlation (`test_pearson`)
```python
from scitex.stats.tests import test_pearson

x = np.random.normal(0, 1, 50)
y = 0.7 * x + np.random.normal(0, 0.5, 50)

result = test_pearson(x, y, var_x='Variable X', var_y='Variable Y', plot=True)
print(f"r = {result['statistic']:.3f}, 95% CI [{result['ci_lower']:.3f}, {result['ci_upper']:.3f}]")
print(f"R² = {result['r_squared']:.3f}")
```

**Features**:
- Measures **linear** relationships
- Fisher's z-transformation for confidence intervals
- R² (coefficient of determination)
- 2-panel plot: scatter + regression line, residual plot
- Comparison with Spearman for non-linear data

#### 14. Spearman Correlation (`test_spearman`)
```python
from scitex.stats.tests import test_spearman

x = np.linspace(1, 50, 50)
y = np.log(x) + np.random.normal(0, 0.3, 50)  # Non-linear monotonic

result = test_spearman(x, y, var_x='x', var_y='log(x)', plot=True)
print(f"ρ = {result['statistic']:.3f}, ρ² = {result['rho_squared']:.3f}")
```

**Features**:
- Measures **monotonic** relationships (not just linear)
- Spearman's ρ from rank-transformed data
- ρ² (variance explained by ranks)
- 2-panel plot: original data, rank scatter plots
- Robust to outliers
- Works with ordinal data

---

### Categorical Tests (2) ✓

#### 15. Chi-Square Test (`test_chi2`)
```python
from scitex.stats.tests import test_chi2
import pandas as pd

# 2×2 table: Treatment × Outcome
observed = np.array([[30, 10], [20, 40]])

result = test_chi2(
    observed,
    var_row='Treatment',
    var_col='Outcome',
    plot=True
)
print(f"χ² = {result['statistic']:.2f}, p = {result['pvalue']:.4f}")
print(f"Cramér's V = {result['effect_size']:.3f} ({result['effect_size_interpretation']})")

# Using DataFrame
df = pd.DataFrame(
    [[45, 25, 10], [30, 40, 30]],
    index=['Control', 'Treatment'],
    columns=['Improved', 'Unchanged', 'Worse']
)
result = test_chi2(df, plot=True)
```

**Features**:
- Independence test for contingency tables (any size)
- Cramér's V effect size with interpretation
- 3-panel visualization: observed, expected, standardized residuals
- Yates' correction for 2×2 tables
- Assumption checking (expected frequencies)
- Warns when Fisher's exact is more appropriate

#### 16. Fisher's Exact Test (`test_fisher`)
```python
from scitex.stats.tests import test_fisher

# 2×2 table with small counts
observed = [[8, 2], [1, 5]]

result = test_fisher(
    observed,
    var_row='Treatment',
    var_col='Response',
    plot=True
)
print(f"OR = {result['statistic']:.2f}, 95% CI [{result['ci_lower']:.2f}, {result['ci_upper']:.2f}]")
```

**Features**:
- **Exact test** for 2×2 tables (no approximation)
- Odds ratio with confidence intervals
- Ideal for small sample sizes
- 2-panel plot: contingency table, OR with CI
- One-sided and two-sided tests
- Comparison with chi-square test

---

## Multiple Comparison Corrections (3) ✓

### 1. Bonferroni Correction (`correct_bonferroni`)
```python
from scitex.stats.correct import correct_bonferroni

# Multiple t-tests
results = []
for i in range(10):
    r = test_ttest_ind(groups_a[i], groups_b[i])
    results.append(r)

# Apply Bonferroni correction
corrected = correct_bonferroni(results, alpha=0.05)
print(f"Adjusted alpha: {corrected['alpha_adjusted']:.4f}")
```

**Features**:
- Conservative FWER control: α_adj = α/m
- Works with dict, list, or DataFrame inputs
- Returns adjusted p-values and significance

### 2. FDR Correction (`correct_fdr`)
```python
from scitex.stats.correct import correct_fdr

# Apply FDR (Benjamini-Hochberg)
corrected = correct_fdr(results, alpha=0.05, method='bh')

# Or Benjamini-Yekutieli (for dependent tests)
corrected = correct_fdr(results, alpha=0.05, method='by')
```

**Features**:
- Controls False Discovery Rate instead of FWER
- More powerful than Bonferroni for large m
- BH method (independent tests) or BY method (dependent tests)

### 3. Holm Correction (`correct_holm`)
```python
from scitex.stats.correct import correct_holm

# Apply Holm-Bonferroni (more powerful than Bonferroni)
corrected = correct_holm(results, alpha=0.05)
```

**Features**:
- Sequential Bonferroni method
- Uniformly more powerful than standard Bonferroni
- Step-down procedure with monotonic adjusted p-values
- Controls FWER at level α

---

## Effect Sizes

All effect sizes include interpretation functions.

### Parametric
- **Cohen's d**: Standardized mean difference
  - Interpretation: negligible (<0.2), small (<0.5), medium (<0.8), large (≥0.8)

- **Eta-squared (η²)**: Proportion of variance explained (ANOVA)
  - Interpretation: small (0.01), medium (0.06), large (0.14)

### Non-Parametric
- **Cliff's delta**: Non-parametric effect size
  - Interpretation: negligible (<0.147), small (<0.33), medium (<0.474), large (≥0.474)

- **P(X>Y)**: Probability of superiority
  - 0.5 = no difference, >0.5 favors X, <0.5 favors Y

- **Epsilon-squared (ε²)**: Kruskal-Wallis effect size
  - Same interpretation as eta-squared

- **Rank-biserial correlation**: Mann-Whitney U and Wilcoxon
  - Same interpretation as Pearson's r

### Categorical
- **Cramér's V**: Association strength in contingency tables
  - Interpretation depends on degrees of freedom

- **Odds Ratio**: Association for 2×2 tables
  - OR = 1: no association, OR > 1: positive, OR < 1: negative

### Correlation
- **Pearson's r / Spearman's ρ**: Correlation coefficient
  - Interpretation: negligible (<0.1), small (<0.3), medium (<0.5), large (≥0.5)

- **R² / ρ²**: Proportion of variance explained
  - 0 to 1 scale

---

## Power Analysis

```python
from scitex.stats.power import power_ttest, sample_size_ttest

# Compute statistical power
power = power_ttest(
    n=30,
    effect_size=0.5,
    alpha=0.05,
    alternative='two-sided'
)
print(f"Power = {power:.3f}")

# Determine required sample size
n = sample_size_ttest(
    effect_size=0.5,
    alpha=0.05,
    power=0.80,
    alternative='two-sided'
)
print(f"Required n = {n} per group")
```

---

## Export Formats (9 Total)

All tests support flexible export via `convert_results()`:

```python
from scitex.stats.utils import convert_results

result = test_anova(groups)

# 1. dict (default)
result_dict = convert_results(result, return_as='dict')

# 2. DataFrame
result_df = convert_results(result, return_as='dataframe')

# 3. CSV
convert_results(result, return_as='csv', path='results.csv')

# 4. JSON
convert_results(result, return_as='json', path='results.json')

# 5. Excel (styled)
convert_results(result, return_as='excel', path='results.xlsx')

# 6. LaTeX table
convert_results(result, return_as='latex', path='table.tex')

# 7. Markdown table
convert_results(result, return_as='markdown', path='results.md')

# 8. HTML table
convert_results(result, return_as='html', path='results.html')

# 9. Plain text report
convert_results(result, return_as='text', path='report.txt')
```

All exports include **SciTeX Stats signature** for professional branding.

---

## Consistent API

Every test function follows the same pattern:

```python
test_xxx(
    data,                    # Input data
    var_x='x',              # Variable name(s)
    var_y='y',
    alternative='two-sided', # Hypothesis: 'two-sided', 'less', 'greater'
    alpha=0.05,             # Significance level
    plot=False,             # Generate visualization
    return_as='dict',       # Output: 'dict', 'dataframe'
    decimals=3              # Rounding precision
)
```

**Returns**:
- Test statistic and p-value
- Effect size with interpretation
- Confidence intervals (where applicable)
- Sample sizes
- Significance indicators
- Assumptions met (where applicable)
- Optional visualization (if `plot=True`)

---

## Design Principles

1. **Normalized naming**: ALL tests use `test_*` prefix
2. **No backward compatibility**: Clean API without legacy clutter
3. **Consistent parameters**: Same API across all 16 tests
4. **Publication-ready**: Professional visualizations and exports
5. **Assumption checking**: Automatic validation where applicable
6. **Comprehensive output**: p-values + effect sizes + CI
7. **Type hints**: Full typing throughout
8. **Documentation**: Formulas, references, examples in docstrings

---

## Testing Strategy

Each test module includes comprehensive examples (`if __name__ == '__main__':`):

- **7-10 examples per test** demonstrating:
  - Basic usage
  - Edge cases (outliers, small samples, ties)
  - Assumption violations
  - Comparison with alternative tests
  - Export demonstrations
  - One-tailed vs two-tailed
  - Large dataset performance

Run with: `python -m scitex.stats.tests.xxx._test_yyy`

---

## Future Roadmap

### High Priority
- [ ] Repeated measures ANOVA
- [ ] Šidák correction
- [ ] Two-way ANOVA
- [ ] McNemar's test (paired categorical)

### Medium Priority
- [ ] Kendall's tau correlation
- [ ] Friedman test (non-parametric RM ANOVA)
- [ ] Cochran's Q test
- [ ] Bootstrap confidence intervals

### Low Priority
- [ ] Mixed-effects models
- [ ] Bayesian alternatives
- [ ] Time series tests
- [ ] Survival analysis basics

---

## Documentation

- **API.md** - Complete function reference
- **SUMMARY.md** - Overview and comparisons
- **PROGRESS.md** - This file
- **ARCHITECTURE.md** - Design decisions

---

## Status: Production Ready ✓

- 16 statistical tests fully implemented and tested
- 3 multiple comparison corrections
- Comprehensive effect sizes with interpretations
- 9 export formats
- Normalized, consistent API
- Professional visualizations
- Automatic assumption checking
- Complete documentation with examples

**Ready for scientific analysis and publication-quality reporting.**
