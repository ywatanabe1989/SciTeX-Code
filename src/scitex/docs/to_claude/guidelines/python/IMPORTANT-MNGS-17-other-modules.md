<!-- ---
!-- Timestamp: 2025-05-29 20:33:33
!-- Author: ywatanabe
!-- File: /ssh:ywatanabe@sp:/home/ywatanabe/.dotfiles/.claude/to_claude/guidelines/python/MNGS-17-mngs-other-modules.md
!-- --- -->

### Utility Functions
```python
# Colored console output with specified border
mngs.str.printc("message here", c='blue', char="-", n=40)
# ----------------------------------------
# message here
# ----------------------------------------

# Convert p-values to significance stars (e.g., *)
mngs.stats.p2stars(p_value)

# Apply FDR correction for multiple comparisons
mngs.stats.fdr_correction(results_df)

# Round numeric values in dataframe
mngs.pd.round(df, factor=3)
```

## Your Understanding Check
Did you understand the guideline? If yes, please say:
`CLAUDE UNDERSTOOD: <THIS FILE PATH HERE>`

<!-- EOF -->