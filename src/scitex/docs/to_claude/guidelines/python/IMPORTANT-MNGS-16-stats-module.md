<!-- ---
!-- Timestamp: 2025-05-29 20:33:30
!-- Author: ywatanabe
!-- File: /ssh:ywatanabe@sp:/home/ywatanabe/.dotfiles/.claude/to_claude/guidelines/python/MNGS-16-mngs-stats-module.md
!-- --- -->

## `mngs.stats`

- `mngs.stats` is a module for statistical tests

```python
# Format p-values with stars
stars = mngs.stats.p2stars(0.001)  # '***'

# Apply multiple comparison correction
corrected = mngs.stats.fdr_correction(results_df)

# Correlation tests
r, p = mngs.stats.tests.corr_test(x, y, method='pearson')
```

## Statistical Reporting

Report statistical results with:
- p-value
- Significance stars
- Sample size
- Effect size
- Test name
- Statistic value
- Null hypothesis

```python
# Example results dictionary
results = {
    "p_value": pval,
    "stars": mngs.stats.p2stars(pval),  # Format: 0.02 -> "*", 0.009 -> "**"
    "n1": n1,
    "n2": n2,
    "dof": dof,
    "effsize": effect_size,
    "test_name": test_name_text,
    "statistic": statistic_value,
    "H0": null_hypothesis_text,
}
```

### Using p2stars

```python
>>> mngs.stats.p2stars(0.0005)
'***'
>>> mngs.stats.p2stars("0.03")
'*'
>>> mngs.stats.p2stars("1e-4")
'***'
>>> df = pd.DataFrame({'p_value': [0.001, "0.03", 0.1, "NA"]})
>>> mngs.stats.p2stars(df)
   p_value
0  0.001 ***
1  0.030   *
2  0.100
3     NA  NA
```

### Multiple Comparisons Correction

Always use FDR correction for multiple comparisons:

```python
# Apply FDR correction to DataFrame with p_value column
corrected_results = mngs.stats.fdr_correction(results_df)
```

## Your Understanding Check
Did you understand the guideline? If yes, please say:
`CLAUDE UNDERSTOOD: <THIS FILE PATH HERE>`

<!-- EOF -->