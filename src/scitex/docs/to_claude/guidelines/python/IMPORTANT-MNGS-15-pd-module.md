<!-- ---
!-- Timestamp: 2025-05-29 20:33:26
!-- Author: ywatanabe
!-- File: /ssh:ywatanabe@sp:/home/ywatanabe/.dotfiles/.claude/to_claude/guidelines/python/MNGS-15-mngs-pd-module.md
!-- --- -->

### `mngs.pd` Module (Pandas Utilities)

```python
# Round numeric values
rounded_df = mngs.pd.round(df, factor=3)

# Enhanced DataFrame slicing
filtered = mngs.pd.slice(df, {'column1': 'value', 'column2': [1, 2, 3]})

# Coordinate conversion
xyz_data = mngs.pd.to_xyz(df)
```

## Your Understanding Check
Did you understand the guideline? If yes, please say:
`CLAUDE UNDERSTOOD: <THIS FILE PATH HERE>`

<!-- EOF -->