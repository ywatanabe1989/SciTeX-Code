# Statistical Validation Framework Documentation

## Overview

The Statistical Validation Framework in SciTeX provides tools to ensure the scientific validity of statistical analyses. It helps researchers:

1. Check statistical assumptions before running tests
2. Choose appropriate statistical tests based on data characteristics
3. Calculate and interpret effect sizes
4. Validate sample sizes for adequate statistical power

## Components

### 1. StatisticalValidator

The `StatisticalValidator` class provides methods to check common statistical assumptions.

#### Methods

##### check_normality(data, alpha=0.05, test='shapiro')

Tests whether data follows a normal distribution.

```python
from scitex.stats import StatisticalValidator

# Check if data is normally distributed
is_normal, p_value, stats = StatisticalValidator.check_normality(data)

# Parameters:
# - data: array-like data to test
# - alpha: significance level (default 0.05)
# - test: 'shapiro', 'anderson', or 'normaltest'

# Returns:
# - is_normal: boolean indicating normality
# - p_value: p-value from the test
# - stats: dict with skewness, kurtosis, test statistic
```

##### check_homoscedasticity(*groups, alpha=0.05, test='levene')

Tests for equal variances across groups.

```python
# Check if groups have equal variances
is_homo, p_value, stats = StatisticalValidator.check_homoscedasticity(group1, group2)

# Parameters:
# - *groups: variable number of array-like groups
# - alpha: significance level
# - test: 'levene', 'bartlett', or 'fligner'

# Returns:
# - is_homoscedastic: boolean indicating equal variances
# - p_value: p-value from the test
# - stats: dict with variances, variance ratio, etc.
```

##### validate_sample_size(data, test_type, min_size=None, warn_only=True)

Validates whether sample size is adequate for a given test.

```python
# Check if sample size is adequate
is_adequate, info = StatisticalValidator.validate_sample_size(data, 't_test')

# Parameters:
# - data: array-like or list of arrays
# - test_type: type of test ('t_test', 'anova', 'correlation', etc.)
# - min_size: override default minimum size
# - warn_only: if False, returns False for inadequate size

# Supported test types and default minimum sizes:
# - 't_test': 30
# - 'mann_whitney': 20
# - 'anova': 20 per group
# - 'correlation': 30
# - 'regression': 50
# - 'brunner_munzel': 10 per group
```

##### suggest_test(data_characteristics, hypothesis='two_sample')

Suggests appropriate statistical tests based on data characteristics.

```python
# Get test recommendations
data_chars = {
    'is_normal': True,
    'is_homoscedastic': True,
    'n_groups': 2,
    'is_paired': False,
    'sample_size': 50
}

suggestions = StatisticalValidator.suggest_test(data_chars, 'two_sample')
# Returns dict with 'primary', 'alternatives', and 'rationale'
```

### 2. EffectSizeCalculator

The `EffectSizeCalculator` class provides methods to calculate and interpret effect sizes.

#### Methods

##### cohens_d(group1, group2, pooled=True)

Calculates Cohen's d effect size for two groups.

```python
from scitex.stats import EffectSizeCalculator

# Calculate Cohen's d
result = EffectSizeCalculator.cohens_d(treatment, control)

# Returns dict with:
# - d: Cohen's d value
# - interpretation: 'negligible', 'small', 'medium', or 'large'
# - ci_lower, ci_upper: 95% confidence interval
# - n1, n2: sample sizes
# - mean_diff: mean difference

# Interpretation thresholds:
# - |d| < 0.2: negligible
# - |d| < 0.5: small
# - |d| < 0.8: medium
# - |d| >= 0.8: large
```

##### hedges_g(group1, group2)

Calculates Hedges' g (bias-corrected Cohen's d), better for small samples.

```python
# Calculate Hedges' g
result = EffectSizeCalculator.hedges_g(treatment, control)

# Includes correction factor for small sample bias
```

##### eta_squared(groups, partial=False)

Calculates eta-squared for ANOVA.

```python
# Calculate eta-squared for multiple groups
result = EffectSizeCalculator.eta_squared([group1, group2, group3])

# Returns dict with:
# - eta_squared or partial_eta_squared
# - interpretation
# - sum of squares components

# Interpretation:
# - η² < 0.01: negligible
# - η² < 0.06: small
# - η² < 0.14: medium
# - η² >= 0.14: large
```

##### omega_squared(groups)

Calculates omega-squared (less biased than eta-squared).

```python
# Calculate omega-squared
result = EffectSizeCalculator.omega_squared([group1, group2, group3])

# Better for smaller samples than eta-squared
```

##### odds_ratio(table, alpha=0.05)

Calculates odds ratio for 2x2 contingency tables.

```python
# 2x2 table: [[a, b], [c, d]]
result = EffectSizeCalculator.odds_ratio(contingency_table)

# Returns dict with:
# - odds_ratio: OR value
# - ci_lower, ci_upper: confidence interval
# - interpretation
# - significant: whether CI excludes 1
```

##### relative_risk(table, alpha=0.05)

Calculates relative risk for 2x2 contingency tables.

```python
# Calculate relative risk
result = EffectSizeCalculator.relative_risk(contingency_table)

# Returns dict with:
# - relative_risk: RR value
# - risk_exposed, risk_unexposed
# - interpretation
```

## Usage Examples

### Complete Analysis Workflow

```python
import numpy as np
from scitex.stats import StatisticalValidator, EffectSizeCalculator

# 1. Generate or load your data
control = np.random.normal(100, 15, 50)
treatment = np.random.normal(107, 15, 55)

# 2. Check assumptions
# Normality
ctrl_normal, _, _ = StatisticalValidator.check_normality(control)
trt_normal, _, _ = StatisticalValidator.check_normality(treatment)

# Equal variances
is_homo, p_homo, _ = StatisticalValidator.check_homoscedasticity(control, treatment)

# Sample size
is_adequate, _ = StatisticalValidator.validate_sample_size([control, treatment], 't_test')

# 3. Get test recommendation
data_chars = {
    'is_normal': ctrl_normal and trt_normal,
    'is_homoscedastic': is_homo,
    'n_groups': 2,
    'is_paired': False,
    'sample_size': min(len(control), len(treatment))
}

test_rec = StatisticalValidator.suggest_test(data_chars, 'two_sample')
print(f"Recommended test: {test_rec['primary']}")

# 4. Calculate effect size
effect = EffectSizeCalculator.cohens_d(treatment, control)
print(f"Cohen's d = {effect['d']:.3f} ({effect['interpretation']})")
print(f"95% CI: [{effect['ci_lower']:.3f}, {effect['ci_upper']:.3f}]")
```

### Handling Violations

```python
# Non-normal data
if not ctrl_normal or not trt_normal:
    # Use non-parametric test
    from scitex.stats import brunner_munzel
    result = brunner_munzel(control, treatment)
    
# Unequal variances
if not is_homo:
    # Use Welch's t-test
    from scipy.stats import ttest_ind
    stat, p = ttest_ind(control, treatment, equal_var=False)
    
# Small sample size
if not is_adequate:
    # Consider exact tests or collect more data
    print("Warning: Sample size may be inadequate")
```

## Best Practices

1. **Always check assumptions first**
   - Don't assume normality - test it
   - Check variance equality for t-tests and ANOVA
   - Validate sample sizes for adequate power

2. **Report effect sizes**
   - P-values tell you if an effect exists
   - Effect sizes tell you how large it is
   - Always report both

3. **Use appropriate tests**
   - Let the data characteristics guide test selection
   - Don't force parametric tests on non-normal data
   - Consider robust alternatives (e.g., Brunner-Munzel)

4. **Interpret effect sizes properly**
   - Small effects can be meaningful in some contexts
   - Large effects with small samples need replication
   - Consider confidence intervals, not just point estimates

5. **Document your validation process**
   - Report which assumptions were checked
   - Explain why specific tests were chosen
   - Include effect sizes in results sections

## Integration with SciTeX

The validation framework integrates seamlessly with other SciTeX modules:

```python
import scitex as stx

# Load data
data = stx.io.load("experiment_data.pkl")

# Validate before analysis
is_normal, _, _ = stx.stats.StatisticalValidator.check_normality(data['group1'])

# Run appropriate test
if is_normal:
    result = stx.stats.ttest_ind(data['group1'], data['group2'])
else:
    result = stx.stats.brunner_munzel(data['group1'], data['group2'])

# Calculate effect size
effect = stx.stats.EffectSizeCalculator.cohens_d(data['group1'], data['group2'])

# Save results
results = {
    'test_result': result,
    'effect_size': effect,
    'assumptions_met': is_normal
}
stx.io.save("analysis_results.pkl", results)
```

## References

- Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences
- Lakens, D. (2013). Calculating and reporting effect sizes
- Field, A. (2013). Discovering Statistics Using IBM SPSS Statistics
- Brunner, E., & Munzel, U. (2000). The nonparametric Behrens-Fisher problem