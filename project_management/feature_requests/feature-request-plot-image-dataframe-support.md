<!-- ---
!-- Timestamp: 2025-06-09 23:35:00
!-- Author: ywatanabe
!-- File: /data/gpfs/projects/punim2354/ywatanabe/.claude-worktree/scitex_repo/project_management/feature_requests/feature-request-plot-image-dataframe-support.md
!-- --- -->

# Feature Request: Enhanced DataFrame Support for plot_image

## Summary
Add native pandas DataFrame support to `plot_image` to automatically preserve and display index/column labels.

## Current Behavior
- `plot_image` only accepts numpy arrays
- DataFrame metadata (index/column names) is lost
- Users must manually set tick labels for meaningful axes

## Desired Behavior
```python
# Create DataFrame with meaningful labels
df = pd.DataFrame(comodulogram_data,
                  index=phase_frequencies,
                  columns=amplitude_frequencies)
df.index.name = 'Phase Frequency (Hz)'
df.columns.name = 'Amplitude Frequency (Hz)'

# Should automatically use DataFrame labels
ax.plot_image(df, cbar_label='PAC Strength')
```

## Benefits
1. **Scientific plots**: Comodulograms, correlation matrices, etc. often have meaningful axes
2. **Convenience**: No manual tick label setting required
3. **Export**: CSV export could include axis information
4. **Consistency**: Similar to how seaborn handles DataFrames

## Implementation Suggestions
1. Check if input is DataFrame in `plot_image`
2. Extract and store index/column information
3. Automatically set tick positions and labels
4. Use index.name/columns.name as axis labels if available
5. Include metadata in tracking for CSV export

## Priority
Medium - Would significantly improve usability for scientific plotting

## Related Issues
- CSV export currently shows `plot_image` as "not implemented"
- Users need workarounds for common scientific visualizations

<!-- EOF -->